"""Lossless, bounded JSONL parts with closed membership and logical digests."""
from pathlib import Path
from types import SimpleNamespace
import hashlib
import io
import json
import re

SCHEMA = 'controlled-followup-v6.framed-jsonl/v1'
INDEX = 'streams.json'
STREAMS = ('setups.jsonl', 'attempt-intents.jsonl', 'single-points.jsonl',
           'traces.jsonl', 'decoder-cells.jsonl')
METADATA = ('engine-summary.json', 'engine-completion.json')
PART_BYTES = 128 << 20
LINE_BYTES = 64 << 20


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       allow_nan=False) + '\n').encode()


def _pairs(items):
    value = {}
    for key, item in items:
        need(key not in value, 'duplicate framing key')
        value[key] = item
    return value


def _digest(value):
    return type(value) is str and re.fullmatch('[0-9a-f]{64}', value) is not None


class Writer:
    """One canonical record per write; a record never spans physical parts."""
    def __init__(self, root, name, part_bytes=PART_BYTES):
        need(name in STREAMS, 'unknown logical stream')
        need(type(part_bytes) is int and 0 < part_bytes <= PART_BYTES,
             'bounded part size')
        self.root, self.name, self.limit = Path(root), name, part_bytes
        self.directory = self.root / name
        self.directory.mkdir(exist_ok=False)
        self.parts = []
        self.total = self.records = 0
        self.digest = hashlib.sha256()
        self.handle = None
        self.closed = False

    def _finish_part(self):
        if self.handle is not None:
            self.handle.close()
            self.parts.append({'path': self.part.relative_to(self.root).as_posix(),
                               'bytes': self.part_size, 'records': self.part_rows,
                               'sha256': self.part_digest.hexdigest()})
            self.handle = None

    def write(self, raw):
        need(not self.closed, 'closed logical stream')
        need(type(raw) is bytes and raw.endswith(b'\n') and raw.count(b'\n') == 1,
             'one complete JSONL record required')
        need(len(raw) <= min(LINE_BYTES, self.limit), 'record exceeds framing cap')
        if self.handle is not None and self.part_size + len(raw) > self.limit:
            self._finish_part()
        if self.handle is None:
            self.part = self.directory / ('part-%06d.jsonl' % len(self.parts))
            self.handle = self.part.open('xb')
            self.part_size = self.part_rows = 0
            self.part_digest = hashlib.sha256()
        need(self.handle.write(raw) == len(raw), 'short part write')
        self.part_digest.update(raw)
        self.digest.update(raw)
        self.part_size += len(raw)
        self.part_rows += 1
        self.total += len(raw)
        self.records += 1
        return len(raw)

    def flush(self):
        if self.handle is not None:
            self.handle.flush()

    def close(self):
        self._finish_part()
        self.closed = True

    def manifest(self):
        need(self.closed, 'stream must close before its manifest')
        return {'bytes': self.total, 'records': self.records,
                'sha256': self.digest.hexdigest(), 'parts': list(self.parts)}


def write_index(root, writers, part_bytes):
    value = {'schema': SCHEMA, 'part_bytes': part_bytes,
             'streams': {writer.name: writer.manifest() for writer in writers}}
    need(set(value['streams']) == set(STREAMS), 'exact five logical streams')
    with (Path(root) / INDEX).open('xb') as target:
        target.write(canonical(value))
    return value


class _Reader(io.RawIOBase):
    def __init__(self, paths):
        super().__init__()
        self.paths = iter(paths)
        self.current = None

    def readable(self):
        return True

    def readinto(self, target):
        if self.closed:
            raise ValueError('closed framed reader')
        while True:
            if self.current is None:
                path = next(self.paths, None)
                if path is None:
                    return 0
                self.current = path.open('rb')
            count = self.current.readinto(target)
            if count:
                return count
            self.current.close()
            self.current = None

    def close(self):
        if self.current is not None:
            self.current.close()
            self.current = None
        super().close()


class LogicalFile:
    def __init__(self, name, root, manifest):
        self.name = name
        self.root = root
        self.manifest = manifest

    def stat(self):
        return SimpleNamespace(st_size=self.manifest['bytes'])

    def open(self, mode='rb'):
        need(mode == 'rb', 'framed streams are read-only binary data')
        return io.BufferedReader(_Reader([self.root / p['path']
                                          for p in self.manifest['parts']]), 1 << 16)

    def read_bytes(self):
        # Small disclosed fixtures only. Production consumers use streaming open().
        need(self.manifest['bytes'] <= LINE_BYTES, 'whole-stream read cap')
        with self.open() as source:
            return source.read(LINE_BYTES + 1)


def open_logical(root):
    """Verify every part and digest before exposing a logical read capability."""
    root = Path(root)
    need(root.is_dir() and not root.is_symlink(), 'regular framing directory')
    index = root / INDEX
    need(index.is_file() and not index.is_symlink() and index.stat().st_size <= 4 << 20,
         'bounded framing index')
    value = json.loads(index.read_bytes(), object_pairs_hook=_pairs,
                       parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite framing value')))
    need(type(value) is dict and set(value) == {'schema', 'part_bytes', 'streams'}
         and value['schema'] == SCHEMA, 'framing schema')
    limit = value['part_bytes']
    need(type(limit) is int and 0 < limit <= PART_BYTES, 'framing part cap')
    need(type(value['streams']) is dict and set(value['streams']) == set(STREAMS),
         'exact logical stream membership')
    expected = {INDEX, *METADATA}
    result = {}
    for name in STREAMS:
        stream = value['streams'][name]
        need(type(stream) is dict and set(stream) == {'bytes', 'records', 'sha256', 'parts'},
             'logical stream fields')
        need(type(stream['bytes']) is int and stream['bytes'] >= 0
             and type(stream['records']) is int and stream['records'] >= 0
             and _digest(stream['sha256']) and type(stream['parts']) is list,
             'logical stream values')
        digest = hashlib.sha256()
        total = rows = 0
        for sequence, part in enumerate(stream['parts']):
            need(type(part) is dict and set(part) == {'path', 'bytes', 'records', 'sha256'},
                 'part fields')
            relative = name + '/part-%06d.jsonl' % sequence
            need(part['path'] == relative and _digest(part['sha256'])
                 and type(part['bytes']) is int and 0 < part['bytes'] <= limit
                 and type(part['records']) is int and part['records'] > 0,
                 'part sequence/path/size')
            expected.add(relative)
            path = root / relative
            need(path.is_file() and not path.is_symlink()
                 and path.stat().st_size == part['bytes'], 'missing or resized part')
            part_hash = hashlib.sha256()
            part_rows = size = line_size = 0
            with path.open('rb') as source:
                while True:
                    raw = source.readline(LINE_BYTES + 1)
                    if not raw:
                        break
                    need(len(raw) <= LINE_BYTES and raw.endswith(b'\n') and raw.strip(),
                         'partial/blank/oversized framed record')
                    digest.update(raw)
                    part_hash.update(raw)
                    part_rows += 1
                    size += len(raw)
            need(size == part['bytes'] and part_rows == part['records']
                 and part_hash.hexdigest() == part['sha256'], 'part digest/records')
            total += size
            rows += part_rows
        need(total == stream['bytes'] and rows == stream['records']
             and digest.hexdigest() == stream['sha256'], 'logical digest/records')
        result[name] = LogicalFile(name, root, stream)
    actual = set()
    for path in root.rglob('*'):
        need(not path.is_symlink(), 'framing symlink')
        if path.is_file():
            actual.add(path.relative_to(root).as_posix())
    need(actual == expected, 'missing or extra physical framing members')
    result.update({name: root / name for name in METADATA})
    return result


def logical_file(path):
    path = Path(path)
    if path.is_dir():
        need(path.name in STREAMS, 'unknown logical directory')
        return open_logical(path.parent)[path.name]
    return path
