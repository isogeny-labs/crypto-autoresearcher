"""The formal receipt binds the parser that interprets its frozen target."""

import hashlib
from pathlib import Path
import subprocess

import yaml

from orchestration.formal.receipts import archived_verifier_inputs, verifier_inputs


def test_current_verifier_inputs_include_yaml_loader_and_installed_parser():
    inputs = verifier_inputs()
    helper = Path(__file__).resolve().parents[1] / 'orchestration/fast_yaml.py'
    assert inputs['orchestration/fast_yaml.py'] == hashlib.sha256(helper.read_bytes()).hexdigest()
    package = Path(yaml.__file__).resolve().parent
    parser = f'runtime/PyYAML/{yaml.__version__}/__init__.py'
    assert inputs[parser] == hashlib.sha256((package/'__init__.py').read_bytes()).hexdigest()
    for extension in package.glob('*.so'):
        assert f'runtime/PyYAML/{yaml.__version__}/{extension.name}' in inputs


def test_archived_legacy_closure_remains_distinct_from_new_closure(tmp_path):
    formal = tmp_path / 'orchestration/formal'
    formal.mkdir(parents=True)
    (formal/'receipts.py').write_text('old verifier\n')
    (formal.parent/'fast_yaml.py').write_text('old parser\n')
    subprocess.run(['git', 'init', '-q'], cwd=tmp_path, check=True)
    subprocess.run(['git', 'add', '.'], cwd=tmp_path, check=True)
    subprocess.run(['git', '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                    'commit', '-qm', 'archive'], cwd=tmp_path, check=True)
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=tmp_path,
                                       text=True).strip()
    legacy = archived_verifier_inputs(tmp_path, revision)
    closed = archived_verifier_inputs(tmp_path, revision, yaml_closure=True)
    assert set(legacy) == {'orchestration/formal/receipts.py'}
    assert closed['orchestration/fast_yaml.py'] == hashlib.sha256(b'old parser\n').hexdigest()
    assert any(key.startswith('runtime/PyYAML/') for key in closed)
