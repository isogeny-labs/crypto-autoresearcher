default(parisizemax,2000000000);
E=ellinit([0,-1,1,-10,-20]);a=ellap(E,10000169);N=10000169+1-a;print(a);print(N);F=factor(N);print(Vec(F[,1]));print(Vec(F[,2]));
quit
