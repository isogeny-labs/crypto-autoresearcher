//! Independent streaming replay of exceptional PEXT square classes.
//!
//! No producer arithmetic is imported. The versioned binary input is specified
//! in native_squareclass_stream.py. This checks arithmetic rows, not candidate
//! set completeness, source descent, C5 or a scientific cohort.

use std::io::{self, Read};

const MAGIC: &[u8; 8] = b"PXSCV1\0\0";
const MAX_FIELD: usize = 4096;
const MAX_ROWS: u64 = 2_000_000;

fn fail(message: &str) -> String { message.to_owned() }
fn check(ok: bool, message: &str) -> Result<(), String> {
    if ok { Ok(()) } else { Err(fail(message)) }
}

fn read_fixed<const N: usize>(reader: &mut impl Read) -> Result<[u8; N], String> {
    let mut bytes = [0u8; N];
    reader.read_exact(&mut bytes).map_err(|_| fail("truncated native squareclass stream"))?;
    Ok(bytes)
}
fn read_u8(reader: &mut impl Read) -> Result<u8, String> { Ok(read_fixed::<1>(reader)?[0]) }
fn read_u16(reader: &mut impl Read) -> Result<u16, String> {
    Ok(u16::from_le_bytes(read_fixed::<2>(reader)?))
}
fn read_u32(reader: &mut impl Read) -> Result<u32, String> {
    Ok(u32::from_le_bytes(read_fixed::<4>(reader)?))
}
fn read_u64(reader: &mut impl Read) -> Result<u64, String> {
    Ok(u64::from_le_bytes(read_fixed::<8>(reader)?))
}

#[derive(Clone)]
struct Field {
    p: usize,
    n: usize,
    q: usize,
    add_table: Vec<u16>,
    mul_table: Vec<u16>,
    inverse: Vec<u16>,
    frobenius: Vec<u16>,
    nonsquare: Vec<bool>,
}
impl Field {
    fn digits(mut value: usize, p: usize, n: usize) -> Vec<usize> {
        let mut out = Vec::with_capacity(n);
        for _ in 0..n { out.push(value % p); value /= p; }
        out
    }
    fn raw_add(a: usize, b: usize, p: usize, n: usize) -> usize {
        let mut aa = a;
        let mut bb = b;
        let mut place = 1;
        let mut result = 0;
        for _ in 0..n {
            result += ((aa % p + bb % p) % p) * place;
            aa /= p; bb /= p; place *= p;
        }
        result
    }
    fn raw_mul(a: usize, b: usize, p: usize, n: usize, modulus: &[usize]) -> usize {
        let da = Self::digits(a, p, n);
        let db = Self::digits(b, p, n);
        let mut product = vec![0usize; 2 * n - 1];
        for i in 0..n { for j in 0..n {
            product[i+j] = (product[i+j] + da[i] * db[j]) % p;
        }}
        for k in (n..2*n-1).rev() {
            let coefficient = product[k];
            for j in 0..n {
                product[k-n+j] = (product[k-n+j] + p
                    - coefficient * modulus[j] % p) % p;
            }
        }
        let mut place = 1;
        let mut result = 0;
        for digit in product.iter().take(n) {
            result += digit * place;
            place *= p;
        }
        result
    }
    fn new(p: usize, n: usize, modulus: &[usize]) -> Result<Self, String> {
        check([3,5,7,11,13].contains(&p) && [3,5,7].contains(&n),
              "unsupported prime or extension degree")?;
        let q = p.checked_pow(n as u32).ok_or_else(|| fail("field overflow"))?;
        check(q <= MAX_FIELD && modulus.len() == n + 1
              && modulus[n] == 1 && modulus.iter().all(|&x| x < p),
              "field size or modulus invalid")?;
        let entries = q.checked_mul(q).ok_or_else(|| fail("field table overflow"))?;
        let mut add_table = vec![0u16; entries];
        let mut mul_table = vec![0u16; entries];
        for a in 0..q { for b in 0..q {
            let index = a*q+b;
            add_table[index] = Self::raw_add(a,b,p,n) as u16;
            mul_table[index] = Self::raw_mul(a,b,p,n,modulus) as u16;
        }}
        let mut field = Self {p,n,q,add_table,mul_table,
            inverse: vec![0;q], frobenius: vec![0;q], nonsquare: vec![false;q]};
        for a in 1..q {
            let inv = field.pow(a as u16, (q-2) as u64);
            check(field.mul(a as u16,inv)==1,
                  "reducible field modulus or invalid multiplication")?;
            field.inverse[a]=inv;
        }
        for a in 0..q {
            field.frobenius[a]=field.pow(a as u16,p as u64);
            if a>0 {
                let symbol=field.pow(a as u16,((q-1)/2) as u64);
                check(symbol==1 || symbol==field.neg(1),
                      "invalid quadratic character")?;
                field.nonsquare[a]=symbol!=1;
            }
        }
        Ok(field)
    }
    #[inline] fn add(&self,a:u16,b:u16)->u16 {self.add_table[a as usize*self.q+b as usize]}
    #[inline] fn mul(&self,a:u16,b:u16)->u16 {self.mul_table[a as usize*self.q+b as usize]}
    #[inline] fn neg(&self,a:u16)->u16 {
        if a==0 {0} else {
            let mut value=a as usize;let mut place=1;let mut result=0;
            for _ in 0..self.n {
                result+=((self.p-value%self.p)%self.p)*place;
                value/=self.p;place*=self.p;
            }
            result as u16
        }
    }
    #[inline] fn sub(&self,a:u16,b:u16)->u16 {self.add(a,self.neg(b))}
    #[inline] fn div(&self,a:u16,b:u16)->Result<u16,String> {
        check(b!=0,"division by zero")?;Ok(self.mul(a,self.inverse[b as usize]))
    }
    fn pow(&self,mut a:u16,mut e:u64)->u16 {
        let mut out=1;
        while e>0 {
            if e&1!=0 {out=self.mul(out,a);}
            a=self.mul(a,a);e>>=1;
        }
        out
    }
}

type Poly = Vec<u16>;
fn trim(poly: &mut Poly) {while poly.last()==Some(&0){poly.pop();}}
fn degree(poly:&Poly)->usize {poly.len().saturating_sub(1)}
fn monic(field:&Field,mut poly:Poly)->Result<Poly,String> {
    trim(&mut poly);
    check(!poly.is_empty(),"zero polynomial support")?;
    let inv=field.inverse[*poly.last().unwrap() as usize];
    for value in &mut poly {*value=field.mul(*value,inv);}
    Ok(poly)
}
fn poly_mul(field:&Field,a:&Poly,b:&Poly)->Poly {
    if a.is_empty() || b.is_empty(){return vec![];}
    let mut out=vec![0;a.len()+b.len()-1];
    for (i,&x) in a.iter().enumerate() {for (j,&y) in b.iter().enumerate(){
        out[i+j]=field.add(out[i+j],field.mul(x,y));
    }}
    trim(&mut out);out
}
fn divmod(field:&Field,mut a:Poly,b:&Poly)->Result<(Poly,Poly),String> {
    trim(&mut a);let mut divisor=b.clone();trim(&mut divisor);
    check(!divisor.is_empty(),"zero polynomial divisor")?;
    let mut quotient=vec![0;a.len().saturating_sub(divisor.len())+1];
    while a.len()>=divisor.len() {
        let offset=a.len()-divisor.len();
        let factor=field.div(*a.last().unwrap(),*divisor.last().unwrap())?;
        quotient[offset]=factor;
        for (i,&value) in divisor.iter().enumerate(){
            a[offset+i]=field.sub(a[offset+i],field.mul(factor,value));
        }
        trim(&mut a);
    }
    trim(&mut quotient);
    Ok((quotient,a))
}
fn exact_quotient(field:&Field,a:Poly,b:&Poly)->Result<Poly,String> {
    let (quotient,remainder)=divmod(field,a,b)?;
    check(remainder.is_empty(),"inexact support quotient")?;
    Ok(quotient)
}
fn gcd(field:&Field,mut a:Poly,mut b:Poly)->Result<Poly,String> {
    while !b.is_empty() {
        let (_,rem)=divmod(field,a,&b)?;
        a=b;b=rem;
    }
    monic(field,a)
}
fn derivative(field:&Field,a:&Poly)->Poly {
    let mut result=vec![0;a.len().saturating_sub(1)];
    for i in 1..a.len(){
        let scalar=(i%field.p) as u16;
        result[i-1]=field.mul(a[i],scalar);
    }
    trim(&mut result);result
}
fn linear_product(field:&Field,a:&Poly,b:&Poly)->Poly {poly_mul(field,a,b)}
fn transform(field:&Field,form:&[u16;5],matrix:&[u16;4])->Result<[u16;5],String> {
    let [a,b,c,d]=*matrix;
    let det=field.sub(field.mul(a,d),field.mul(b,c));
    check(det!=0,"singular projective matrix")?;
    let left=vec![field.neg(b),d];
    let right=vec![a,field.neg(c)];
    let mut result=[0u16;5];
    for i in 0..5 {
        let mut term=vec![form[i]];
        for _ in 0..i {term=linear_product(field,&term,&left);}
        for _ in 0..(4-i) {term=linear_product(field,&term,&right);}
        for (j,value) in term.into_iter().enumerate(){
            result[j]=field.add(result[j],value);
        }
    }
    Ok(result)
}
fn rank(mut vectors:Vec<u64>)->usize {
    let mut pivots=[0u64;64];
    let mut count=0;
    for vector in vectors.drain(..) {
        let mut value=vector;
        while value!=0 {
            let pivot=63-value.leading_zeros() as usize;
            if pivots[pivot]==0 {pivots[pivot]=value;count+=1;break;}
            value^=pivots[pivot];
        }
    }
    count
}
#[derive(Debug,PartialEq,Eq)]
struct Geometry {rg:u8,ra:u8,constant:bool,branch:u8,genus:u16}
fn assess(field:&Field,form:&[u16;5],matrix:&[u16;4])->Result<Geometry,String> {
    let mut current=transform(field,form,matrix)?;
    let mut forms=Vec::with_capacity(field.n);
    for _ in 0..field.n {
        forms.push(current);
        current=current.map(|x|field.frobenius[x as usize]);
    }
    check(current==forms[0],"coefficient Frobenius orbit does not close")?;
    let mut atoms:Vec<(Poly,u8)>=Vec::new();
    let mut infinity=false;
    let mut coefficient_bits=vec![false;field.n];
    let mut finite_forms=Vec::with_capacity(field.n);
    for (i,form) in forms.iter().enumerate() {
        let mut finite=form.to_vec();trim(&mut finite);
        check((finite.len()==4 || finite.len()==5)
              && gcd(field,finite.clone(),derivative(field,&finite))?==vec![1],
              "quartic support is not squarefree")?;
        infinity|=finite.len()==4;
        coefficient_bits[i]=field.nonsquare[*finite.last().unwrap() as usize];
        finite_forms.push(monic(field,finite)?);
    }
    for (i,finite) in finite_forms.into_iter().enumerate() {
        let mut remainder=finite;
        let mut next=Vec::new();
        for (atom,mask) in atoms {
            let common=gcd(field,atom.clone(),remainder.clone())?;
            if degree(&common)==0 {next.push((atom,mask));continue;}
            let atom_quotient=exact_quotient(field,atom,&common)?;
            remainder=exact_quotient(field,remainder,&common)?;
            if degree(&atom_quotient)>0 {next.push((atom_quotient,mask));}
            next.push((common,mask | (1<<i)));
        }
        if degree(&remainder)>0 {next.push((remainder,1<<i));}
        atoms=next;
    }
    check(atoms.len()+1<64,"too many finite support atoms")?;
    let mut geometric=vec![0u64;field.n];
    let mut branch=if infinity {1usize} else {0};
    for (j,(atom,mask)) in atoms.iter().enumerate() {
        branch+=degree(atom);
        for (i,value) in geometric.iter_mut().enumerate() {
            if mask&(1<<i)!=0 {*value|=1u64<<j;}
        }
    }
    for (i,value) in geometric.iter_mut().enumerate(){
        if forms[i][4]==0 {*value|=1u64<<atoms.len();}
    }
    let rg=rank(geometric.clone());
    let arithmetic=geometric.into_iter().enumerate().map(|(i,value)|
        value | ((coefficient_bits[i] as u64) << (atoms.len()+1))).collect();
    let ra=rank(arithmetic);
    check(rg>=1 && rg<=field.n && (ra==rg || ra==rg+1)
          && branch>=2 && branch<=29 && (rg!=1 || branch%2==0),
          &format!("squareclass rank or branch count invalid: rg={rg} ra={ra} branch={branch} atoms={}",atoms.len()))?;
    let genus=if rg==1 {(branch as i64-2)/2}
        else {1+((1i64<<(rg-2))*(branch as i64-4))};
    check(genus>=0 && genus<=u16::MAX as i64,"component genus invalid")?;
    Ok(Geometry{rg:rg as u8,ra:ra as u8,constant:ra>rg,
                branch:branch as u8,genus:genus as u16})
}

fn run(reader:&mut impl Read)->Result<String,String> {
    check(&read_fixed::<8>(reader)?==MAGIC,"native stream magic/version")?;
    let p=read_u16(reader)? as usize;
    let n=read_u8(reader)? as usize;
    check([3,5,7].contains(&n),"unsupported extension degree")?;
    let mut modulus=Vec::with_capacity(n+1);
    for _ in 0..=n {modulus.push(read_u16(reader)? as usize);}
    let mut form=[0u16;5];
    for value in &mut form {*value=read_u16(reader)?;}
    let structures=read_u64(reader)?;
    let rows=read_u32(reader)? as u64;
    let field=Field::new(p,n,&modulus)?;
    check(form.iter().all(|&x|(x as usize)<field.q),
          "source form coefficient outside field")?;
    let q=field.q as u64;
    let expected=(q*q*q-q)/((p*p*p-p) as u64);
    check(structures==expected && structures<=MAX_ROWS
          && rows<=structures,"published structure count or row cap invalid")?;
    let mut previous=None;
    let mut rank_pairs=[[0u64;8];8];
    for index in 0..rows {
        let ordinal=read_u64(reader)?;
        let mut matrix=[0u16;4];
        for value in &mut matrix {*value=read_u16(reader)?;}
        let given=Geometry{rg:read_u8(reader)?,branch:read_u8(reader)?,
            genus:read_u16(reader)?,ra:read_u8(reader)?,
            constant:match read_u8(reader)?{0=>false,1=>true,
                _=>return Err(fail("constant flag outside boolean domain"))}};
        check(ordinal<structures && previous.is_none_or(|v|ordinal>v)
              && matrix.iter().all(|&x|(x as usize)<field.q),
              "exceptional ordinal order or matrix field range")?;
        previous=Some(ordinal);
        let actual=assess(&field,&form,&matrix).map_err(|error|
            format!("exceptional row {index} ordinal {ordinal}: {error}"))?;
        check(actual==given,&format!("exceptional row {index} arithmetic/geometry mismatch"))?;
        rank_pairs[actual.rg as usize][actual.ra as usize]+=1;
    }
    let mut extra=[0u8;1];
    check(reader.read(&mut extra).map_err(|_|fail("trailing stream read error"))?==0,
          "trailing native squareclass bytes")?;
    let groups=rank_pairs.iter().enumerate().flat_map(|(g,row)|
        row.iter().enumerate().filter_map(move |(a,&count)|
            if count>0 {Some(format!("{g}:{a}:{count}"))} else {None}))
        .collect::<Vec<_>>().join(",");
    Ok(format!("OK rows={rows} rank_pairs={groups}"))
}
fn main(){
    let input=io::stdin();
    match run(&mut input.lock()){
        Ok(summary)=>println!("{summary}"),
        Err(error)=>{eprintln!("INVALID: {error}");std::process::exit(2);}
    }
}
