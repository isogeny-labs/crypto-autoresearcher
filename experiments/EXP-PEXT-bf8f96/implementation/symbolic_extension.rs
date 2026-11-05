// Symbolic K[u]/(m(u)) arithmetic for irreducible m of degree 2, 3 or 4.
// Coefficients use the pinned logarithmic encoding of the existing Fld.
// No table of F_(|K|^d) elements is allocated.

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct SymbolicElement { coefficients:[u32;4] }
impl SymbolicElement {
    pub fn coefficients(&self)->[u32;4] {self.coefficients}
}

pub struct SymbolicExtension<'a> {
    field:&'a Fld,
    modulus:P,
    degree:usize,
    size:u64,
}

fn symbolic_mod_mul(field:&Fld,left:&P,right:&P,modulus:&P)->P {
    pdivrem(field,&pmul(field,left,right),modulus).1
}
fn symbolic_mod_pow(field:&Fld,base:&P,mut exponent:u64,modulus:&P)->P {
    let mut result=pz();result.n=1;result.c[0]=1;
    let mut power=*base;
    while exponent>0 {
        if exponent&1==1 {result=symbolic_mod_mul(field,&result,&power,modulus);}
        exponent>>=1;
        if exponent>0 {power=symbolic_mod_mul(field,&power,&power,modulus);}
    }
    result
}
fn symbolic_sub(field:&Fld,left:&P,right:&P)->P {
    let mut result=pz();result.n=left.n.max(right.n);
    for i in 0..result.n {result.c[i]=field.sub(left.c[i],right.c[i]);}
    ptrim(result)
}

impl Context {
    pub fn symbolic_extension(&self,coefficients:&[u32])
        ->Result<SymbolicExtension<'_>,&'static str> {
        SymbolicExtension::new(&self.field,coefficients)
    }
}
impl<'a> SymbolicExtension<'a> {
    fn new(field:&'a Fld,coefficients:&[u32])->Result<Self,&'static str> {
        let degree=coefficients.len().checked_sub(1).ok_or("empty extension modulus")?;
        if !(2..=4).contains(&degree) {return Err("symbolic extension degree must be 2, 3 or 4");}
        if coefficients.iter().any(|&value|value>=field.size) || coefficients[degree]!=1 {
            return Err("symbolic extension requires monic K modulus");
        }
        let size=(field.size as u64).checked_pow(degree as u32)
            .ok_or("symbolic extension size overflow")?;
        let mut modulus=pz();modulus.n=degree+1;
        modulus.c[..modulus.n].copy_from_slice(coefficients);
        let mut variable=pz();variable.n=2;variable.c[1]=1;
        if symbolic_mod_pow(field,&variable,size,&modulus)!=variable {
            return Err("symbolic extension modulus fails Frobenius closure");
        }
        let proper_exponent=(field.size as u64)
            .checked_pow(if degree==4 {2} else {1})
            .ok_or("symbolic extension proper power overflow")?;
        let proper=symbolic_mod_pow(field,&variable,proper_exponent,&modulus);
        if pgcd(field,&modulus,&symbolic_sub(field,&proper,&variable)).n!=1 {
            return Err("reducible symbolic extension modulus");
        }
        Ok(Self{field,modulus,degree,size})
    }
    pub fn degree(&self)->usize {self.degree}
    pub fn size(&self)->u64 {self.size}
    pub fn modulus(&self)->Vec<u32> {self.modulus.c[..self.modulus.n].to_vec()}
    pub fn element(&self,coefficients:&[u32])->Result<SymbolicElement,&'static str> {
        if coefficients.len()>self.degree || coefficients.iter().any(|&value|value>=self.field.size) {
            return Err("symbolic element outside pinned basis");
        }
        let mut result=[0;4];result[..coefficients.len()].copy_from_slice(coefficients);
        Ok(SymbolicElement{coefficients:result})
    }
    pub fn zero(&self)->SymbolicElement {SymbolicElement{coefficients:[0;4]}}
    pub fn one(&self)->SymbolicElement {SymbolicElement{coefficients:[1,0,0,0]}}
    pub fn variable(&self)->SymbolicElement {SymbolicElement{coefficients:[0,1,0,0]}}
    pub fn add(&self,left:SymbolicElement,right:SymbolicElement)->SymbolicElement {
        let mut coefficients=[0;4];
        for (i,value) in coefficients.iter_mut().enumerate().take(self.degree) {
            *value=self.field.add(left.coefficients[i],right.coefficients[i]);
        }
        SymbolicElement{coefficients}
    }
    pub fn sub(&self,left:SymbolicElement,right:SymbolicElement)->SymbolicElement {
        let mut coefficients=[0;4];
        for (i,value) in coefficients.iter_mut().enumerate().take(self.degree) {
            *value=self.field.sub(left.coefficients[i],right.coefficients[i]);
        }
        SymbolicElement{coefficients}
    }
    pub fn mul(&self,left:SymbolicElement,right:SymbolicElement)->SymbolicElement {
        let mut a=pz();a.n=self.degree;a.c[..self.degree].copy_from_slice(&left.coefficients[..self.degree]);a=ptrim(a);
        let mut b=pz();b.n=self.degree;b.c[..self.degree].copy_from_slice(&right.coefficients[..self.degree]);b=ptrim(b);
        let remainder=symbolic_mod_mul(self.field,&a,&b,&self.modulus);
        let mut coefficients=[0;4];coefficients[..remainder.n].copy_from_slice(&remainder.c[..remainder.n]);
        SymbolicElement{coefficients}
    }
    pub fn power(&self,mut base:SymbolicElement,mut exponent:u64)->SymbolicElement {
        let mut result=self.one();
        while exponent>0 {
            if exponent&1==1 {result=self.mul(result,base);}
            exponent>>=1;
            if exponent>0 {base=self.mul(base,base);}
        }
        result
    }
    pub fn inverse(&self,value:SymbolicElement)->Result<SymbolicElement,&'static str> {
        if value==self.zero() {return Err("zero symbolic inverse");}
        Ok(self.power(value,self.size-2))
    }
    pub fn frobenius(&self,value:SymbolicElement,power:u32)
        ->Result<SymbolicElement,&'static str> {
        let exponent=(self.field.q as u64).checked_pow(power)
            .ok_or("symbolic Frobenius exponent overflow")?;
        Ok(self.power(value,exponent))
    }
    pub fn evaluate(&self,coefficients:&[u32],point:SymbolicElement)
        ->Result<SymbolicElement,&'static str> {
        if coefficients.iter().any(|&value|value>=self.field.size) {
            return Err("invalid symbolic polynomial coefficient");
        }
        let mut result=self.zero();
        for &coefficient in coefficients.iter().rev() {
            result=self.add(self.mul(result,point),self.element(&[coefficient])?);
        }
        Ok(result)
    }
}
