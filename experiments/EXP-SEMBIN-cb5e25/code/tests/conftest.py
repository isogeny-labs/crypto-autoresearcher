import os
import sys

CODE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if CODE not in sys.path:
    sys.path.insert(0, CODE)
