import resource, subprocess, sys, time
t=time.time(); r=subprocess.call(sys.argv[1:])
u=resource.getrusage(resource.RUSAGE_CHILDREN)
print(f"TIMED wall={time.time()-t:.1f}s user={u.ru_utime:.1f}s sys={u.ru_stime:.1f}s maxrss_largest_child={u.ru_maxrss/1024:.0f}MiB exit={r}", flush=True)
sys.exit(r)
