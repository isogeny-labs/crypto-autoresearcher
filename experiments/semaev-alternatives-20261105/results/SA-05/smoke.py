from common import *
import subprocess,sys
p=primes_for(40,1)[0]; h=40
pts=small_pts(p,h); print(len(pts))
open('/tmp/b.txt','w').write('\n'.join(str(x) for a,b,x in pts))
import time;t=time.time()
print(subprocess.run(['./sumset',str(p),'/tmp/b.txt','100000','1','/tmp/t.txt'],capture_output=True,text=True).stdout,time.time()-t)
print(open('/tmp/t.txt').read()[:300])
