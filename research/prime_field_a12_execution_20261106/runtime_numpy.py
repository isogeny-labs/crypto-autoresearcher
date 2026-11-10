"""Non-secret installed NumPy build identity; no mathematical fixture generation."""
from contextlib import redirect_stdout
from hashlib import sha256
from io import StringIO
import importlib
from pathlib import Path

def snapshot():
 import numpy as np
 try:extension=importlib.import_module('numpy._core._multiarray_umath')
 except ImportError:extension=importlib.import_module('numpy.core._multiarray_umath')
 path=Path(extension.__file__).resolve();out=StringIO()
 with redirect_stdout(out):np.show_config()
 return dict(version=np.__version__,extension_path=str(path),extension_sha256=sha256(path.read_bytes()).hexdigest(),build_configuration=out.getvalue(),dtype='uint64',maximum_p_exclusive=2**32)
