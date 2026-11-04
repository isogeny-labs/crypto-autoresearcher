"""Run the fixed certificate soundness controls in the normal CI test suite."""
from pathlib import Path
import subprocess
import sys


def test_boolean_closure_certificate_regressions():
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, '-m', 'unittest', 'discover', '-s',
         'analysis/boolean-fall-certificates-20261104', '-v'],
        cwd=root, capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr
