import math, json, sys
sys.path.insert(0,'.')
import model as M
# Table B prime-field rows: (log2 r, |F|, IC log2 GAE, rho log2 GAE, IC/rho measured, x floor)
TB=[(9.7,10,9.36,6.69,6.34,25.8),(11.9,32,9.93,7.48,5.47,17.6),(14.0,26,10.70,8.02,6.43,14.8),(16.0,40,11.54,8.79,6.71,13.2),
    (18.0,64,12.07,9.53,5.82,9.49),(20.0,102,13.42,10.37,8.3,12.1),(21.7,148,14.50,11.11,10.5,14.4),(23.4,222,15.49,11.74,13.5,15.8)]
arm=M.ARMS['PT2 generic pair table (m=2)']
out=[]; 
for lam in (0.0,0.1,1.0):
    for (n,F,ic,rho,rat,xf) in TB:
        c,info=M.arm_cost(arm,n,lam)
        pred_floor=c/M.rho(n)                          # model IC / ideal-rho(=0.886 sqrt N)
        pred_vs_meas_rho=c/(2**rho)                    # model IC / MEASURED rho
        out.append(dict(lam=lam,log2r=n,F_meas=F,B_pred=round(2**info['B_log2'],1),IC_meas=2**ic,IC_pred=c,IC_pred_over_meas=c/2**ic,
                        ratio_meas=rat,ratio_pred_vs_measured_rho=pred_vs_meas_rho,ratio_pred_over_meas=pred_vs_meas_rho/rat,
                        xfloor_meas=xf,xfloor_pred=pred_floor,xfloor_pred_over_meas=pred_floor/xf))
json.dump(out,open('validate_tableB.json','w'),indent=1)
print("lam=0.1")
for r in out:
    if r['lam']==0.1: print(f"n={r['log2r']:5.1f} |F| meas {r['F_meas']:4d} pred {r['B_pred']:6.1f} | IC meas {r['IC_meas']:8.0f} pred {r['IC_pred']:8.0f} x{r['IC_pred_over_meas']:.2f} | IC/rho meas {r['ratio_meas']:5.2f} pred {r['ratio_pred_vs_measured_rho']:5.2f} x{r['ratio_pred_over_meas']:.2f} | xfloor meas {r['xfloor_meas']:5.1f} pred {r['xfloor_pred']:5.1f} x{r['xfloor_pred_over_meas']:.2f}")
for lam in (0.0,1.0):
    v=[r['IC_pred_over_meas'] for r in out if r['lam']==lam]; print("lam",lam,"IC pred/meas range",round(min(v),2),round(max(v),2))
