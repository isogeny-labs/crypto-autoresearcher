\\ Heegner machinery for E=36a1 : y^2=x^3+1, X_0(36)=E (degree 1)
E=ellinit([0,0,0,0,1]); Nn=36; Dk=-23;
AN=0; ANM=0;
setan(M)={ if(M>ANM, AN=ellan(E,M); ANM=M); }
phiz(tau)={ my(q=exp(2*Pi*I*tau), aq=abs(q), M, s=0, qn=1, eps=10^(-default(realprecision)-5));
  M=ceil(log(eps)/log(aq))+2; setan(M);
  qn=q; for(n=1,M, s+=AN[n]*qn/n; qn*=q); s }
Mw=0;
setM()={ my(w=E.omega); Mw=[real(w[1]),real(w[2]);imag(w[1]),imag(w[2])]; }
\\ lattice coordinates of z in [0,1)^2
zc(z)={ my(c=matsolve(Mw,[real(z),imag(z)]~)); [frac(c[1]),frac(c[2])] }
zcs(z)={ my(c=matsolve(Mw,[real(z),imag(z)]~)); [c[1]-round(c[1]),c[2]-round(c[2])] } \\ centered
beta0()={ my(r=[]); for(b=0,71, if((b^2+23)%144==0, r=concat(r,b))); r }
redforms(Del)={ my(L=List(),a,c); a=1; while(3*a^2<=-Del, for(b=-a+1,a, if((b^2-Del)%(4*a)==0, c=(b^2-Del)/(4*a); if(c>=a && !(c==a&&b<0) && gcd([a,b,c])==1, listput(L,[a,b,c])))); a++); Vec(L) }
coprep(f)={ my(a=f[1],b=f[2],c=f[3]);
  for(s=1,60, for(x=-s,s, for(y=0,s, if(max(abs(x),y)==s && gcd(x,y)==1,
     my(v=a*x^2+b*x*y+c*y^2); if(gcd(v,6)==1,
       my(g=gcdext(x,y)); \\ g[1]*x+g[2]*y=1 ; want x*vv - y*u =1 -> vv=g[1], u=-g[2]
       my(vv=g[1],u=-g[2]);
       return([v, 2*a*x*u+b*(x*vv+y*u)+2*c*y*vv, a*u^2+b*u*vv+c*vv^2]))))));
  error("no coprime rep") }
heegner_forms(m,beta)={ my(Del=Dk*m^2, F=redforms(Del), R=List());
  for(i=1,#F, my(f=coprep(F[i]), a=f[1], b=f[2], B, A, C);
     B=lift(chinese(Mod(m*beta,72),Mod(b,2*a))); A=Nn*a; C=(B^2-Del)/(4*A);
     if(denominator(C)!=1, error("bad C")); listput(R,[A,B,C]));
  Vec(R) }
tau_of(f,m)=(-f[2]+m*sqrt(Dk+0.*I))/(2*f[1]);
levelpts(m,beta)={ my(F=heegner_forms(m,beta)); vector(#F,i, my(t=tau_of(F[i],m)); [t, phiz(t)]) }
\\ hecke: returns [residual coords (centered) , neighbor z list]
heckeres(t,z,l)={ my(s=phiz(l*t), nb=List()); listput(nb,s); for(j=0,l-1, my(z2=phiz((t+j)/l)); listput(nb,z2); s+=z2); [zcs(s-ellan(E,l)[l]*z), Vec(nb)] }
\\ recognise u+v*sqrt(-23) rational parts; returns [u,v,err]
recK(c,bd)={ my(u=real(c), v=imag(c)/sqrt(23), ur=bestappr(u,bd), vr=bestappr(v,bd), err); err=abs(c-(ur+vr*sqrt(-23+0.*I))); [ur,vr,err] }
xpoly(P)={ my(xs=vector(#P,i,ellztopoint(E,P[i][2])[1])); factorback(vector(#xs,i,'x-xs[i])) }
\\ ---- labelled level data ----
\\ returns vector of [form(reduced class), tau, z, x, y]
level(m,beta)={ my(Del=Dk*m^2, F=redforms(Del), H=heegner_forms(m,beta));
  vector(#F,i, my(t=tau_of(H[i],m), z=phiz(t), pt=ellztopoint(E,z)); [F[i],t,z,pt[1],pt[2]]) }
gcomp(Del,f1,f2)={ my(r=qfbred(qfbcomp(Qfb(f1[1],f1[2],f1[3]),Qfb(f2[1],f2[2],f2[3])))); Vec(r) }
\\ index table: group-law table T[i][j]=index of class i*j
grptab(Lv)={ my(n=#Lv, idx=Map(), T=matrix(n,n)); for(i=1,n, mapput(idx,Lv[i][1],i));
  for(i=1,n,for(j=1,n, T[i,j]=mapget(idx,gcomp(0,Lv[i][1],Lv[j][1])))); T }
principal(Lv,m)={ my(c=(1+23*m^2)/4); for(i=1,#Lv, if(Lv[i][1]==[1,1,c], return(i))); error("no principal") }
\\ Lagrange basis coefficient matrix: row i = coeffs (ascending) of L_i, nodes xs
lagmat(xs)={ my(n=#xs, P=prod(i=1,n,'x-xs[i]), Pd=deriv(P), M=matrix(n,n)); 
  for(i=1,n, my(q=P\('x-xs[i]), d=subst(Pd,'x,xs[i])); q=q/d; for(k=0,n-1, M[i,k+1]=polcoef(q,k)));  [P,M] }
\\ recognise a vector of complex numbers in K; returns [list of [un,ud,vn,vd], maxlog10err]
recvec(v,bd)={ my(out=vector(#v), me=-9999.); for(k=1,#v, my(r=recK(v[k],bd)); out[k]=[numerator(r[1]),denominator(r[1]),numerator(r[2]),denominator(r[2])]; if(r[3]>0, me=max(me,log(r[3])/log(10.)))); [out,me] }
\\ neighbours of a point (tau) at prime l, as z-list: ordered [l*tau, (tau+j)/l]
nbz(t,l)={ my(L=List()); listput(L,phiz(l*t)); for(j=0,l-1,listput(L,phiz((t+j)/l))); Vec(L) }
matchidx(z,Lv,tol)={ for(j=1,#Lv, my(d=zcs(z-Lv[j][3])); if(abs(d[1])+abs(d[2])<tol, return(j))); 0 }
