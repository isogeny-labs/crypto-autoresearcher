"""S_5 lattice (SA-01 (i) / SA-06 JM-basic) on the SA-15 set: exact t=1 size and Howgrave-Graham margin; not executable by LLL on this host."""
import json, math, itertools
D=json.load(open("/home/user/semaev-runs/SA-15/instances.json"))
rows=[]
box=list(itertools.product(range(9),repeat=4)); dim=len(box); mean_deg=sum(sum(a) for a in box)/dim
for g in D['groups']:
    p=int(g['p']); B=g['B']; lp=math.log2(p); lB=math.log2(B)
    geo=(dim-1)/dim*lp+mean_deg*lB         # log2 (det^(1/dim)) for the t=1 lattice on the full box support of S_5(x1..x4,xR)
    # memory of the basis: dim^2/2 nonzero (triangular) entries of ~ (lp+16*lB*...) bits
    maxbits=lp+32*lB
    rows.append(dict(log2p=g['log2p'],B=B,dim=dim,mean_monomial_degree=mean_deg,log2_det_per_dim=geo,log2_p=lp,hg_margin_bits=lp-geo,
                     entry_bits_max=maxbits,est_basis_GB=dim*dim/2*(maxbits/8+16)/1e9, delta_needed=lB/lp, asymptotic_reach_delta=1/80))
print(json.dumps(rows,indent=1)); json.dump(rows,open("s5_analytic.json","w"),indent=1)
