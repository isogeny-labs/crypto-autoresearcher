"""Deterministic substreams (no dependence on the random / numpy versions).

Seed rule (specification replication.seeds): seed = first 8 bytes of
sha256(protocol_sha256 + "\n" + arm + "\n" + cell_id + "\n" + r), big-endian.
HashRng is a counter-mode sha256 generator: block i = sha256(seed8 || label ||
i), consumed 8 bytes at a time. Every draw below is a pure function of
(seed, label, call sequence).
"""
from __future__ import annotations

import hashlib


def seed_for(protocol_sha256: str, arm: str, cell_id: str, r) -> int:
    msg = f"{protocol_sha256}\n{arm}\n{cell_id}\n{r}".encode()
    return int.from_bytes(hashlib.sha256(msg).digest()[:8], "big")


class HashRng:
    def __init__(self, seed: int, label: str = ""):
        self.seed = int(seed)
        self.label = label
        self._key = self.seed.to_bytes(8, "big") + label.encode()
        self._ctr = 0
        self._buf = b""
        self.calls = 0

    def _bytes(self, k: int) -> bytes:
        while len(self._buf) < k:
            self._buf += hashlib.sha256(self._key + self._ctr.to_bytes(8, "big")).digest()
            self._ctr += 1
        out, self._buf = self._buf[:k], self._buf[k:]
        return out

    def getrandbits(self, k: int) -> int:
        if k <= 0:
            return 0
        nb = (k + 7) // 8
        v = int.from_bytes(self._bytes(nb), "big")
        return v >> (nb * 8 - k)

    def randbelow(self, n: int) -> int:
        """Uniform in [0, n) by rejection."""
        if n <= 0:
            raise ValueError("randbelow(n<=0)")
        self.calls += 1
        if n == 1:
            return 0
        k = (n - 1).bit_length()
        while True:
            v = self.getrandbits(k)
            if v < n:
                return v

    def randrange(self, lo: int, hi: int) -> int:
        """Uniform in [lo, hi)."""
        return lo + self.randbelow(hi - lo)

    def shuffle(self, seq: list) -> None:
        for i in range(len(seq) - 1, 0, -1):
            j = self.randbelow(i + 1)
            seq[i], seq[j] = seq[j], seq[i]

    def sample(self, population, k: int) -> list:
        pop = list(population)
        self.shuffle(pop)
        return pop[:k]

    def substream(self, label: str) -> "HashRng":
        return HashRng(self.seed, self.label + "/" + label)
