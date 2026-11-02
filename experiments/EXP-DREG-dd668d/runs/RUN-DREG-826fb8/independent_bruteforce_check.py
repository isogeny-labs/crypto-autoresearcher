# independent of the solver: enumerate all 2^8 boolean assignments (x1..x4 bits, u1,u2 in F_4) and evaluate S_3 chain with scalar F_4 arithmetic
import itertools
def mul(a,b):
    a0,a1,b0,b1=a&1,a>>1,b&1,b>>1
    return (a0&b0^a1&b1)|((a0&b1^a1&b0^a1&b1)<<1)
sq=lambda a:mul(a,a)
def S3(x,y,w,a6): return mul(sq(x),sq(y))^mul(sq(x),sq(w))^mul(sq(y),sq(w))^mul(mul(x,y),w)^a6
for name,a6 in (("domain a6=z",2),("codomain a6=z+1",3)):
    n=sum(1 for x1,x2,x3,x4 in itertools.product((0,1),repeat=4) for u1 in range(4) for u2 in range(4)
          if S3(u1,x1,x2,a6)==0 and S3(u1,u2,x3,a6)==0 and S3(u2,x4,1,a6)==0)
    print(name,"solutions over F_2^8:",n)
