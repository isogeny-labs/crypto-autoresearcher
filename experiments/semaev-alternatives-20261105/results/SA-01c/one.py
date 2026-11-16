import sys,json,traceback
from search_iii import evalc
try: print(evalc((1,json.loads(sys.argv[1]))))
except Exception: traceback.print_exc()
