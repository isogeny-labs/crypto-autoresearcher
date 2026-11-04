// Exact factorization of a squarefree projective quartic over pinned K.
// No extension-element table or unbounded randomized splitting is used.

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct BranchFactorization {
    pub infinity: bool,
    /// Monic irreducible finite factors, coefficient order low to high.
    pub finite_factors: Vec<Vec<u32>>,
}
impl BranchFactorization {
    pub fn pattern(&self)->Vec<usize> {
        let mut degrees=self.finite_factors.iter().map(|factor|factor.len()-1).collect::<Vec<_>>();
        if self.infinity {degrees.push(1);}
        degrees.sort_unstable();degrees
    }
}

fn branch_difference(field:&Fld,left:&P,right:&P)->P {
    let mut value=pz();value.n=left.n.max(right.n);
    for i in 0..value.n {value.c[i]=field.sub(left.c[i],right.c[i]);}
    ptrim(value)
}
fn branch_sum(field:&Fld,left:&P,right:&P)->P {
    let mut value=pz();value.n=left.n.max(right.n);
    for i in 0..value.n {value.c[i]=field.add(left.c[i],right.c[i]);}
    ptrim(value)
}
fn branch_factor_vec(factor:P)->Vec<u32> {factor.c[..factor.n].to_vec()}

fn split_two_quadratics(field:&Fld,quartic:&P)->Result<(P,P),&'static str> {
    let mut x=pz();x.n=2;x.c[1]=1;
    let xq=symbolic_mod_pow(field,&x,field.size as u64,quartic);
    let trace=branch_sum(field,&x,&xq);
    let norm=symbolic_mod_mul(field,&x,&xq,quartic);
    // On either quadratic factor, trace and norm are elements of K.
    // If the two factors shared both, their monic quadratics would coincide.
    for invariant in [trace,norm] {
        for value in 0..field.size {
            let mut constant=pz();constant.n=1;constant.c[0]=value;
            let difference=branch_difference(field,&invariant,&constant);
            let left=pgcd(field,quartic,&difference);
            if left.n==3 {
                let (right,remainder)=pdivrem(field,quartic,&left);
                if remainder.n!=0 || right.n!=3 {return Err("quadratic split division failed");}
                return Ok((left,pmonic(field,right)));
            }
        }
    }
    Err("distinct quadratic trace and norm failed to split")
}

impl Context {
    pub fn factor_branch_form(&self,form:[u32;5])->Result<BranchFactorization,&'static str> {
        let rational=self.rational_branch_roots(form)?;
        let field=&self.field;
        let mut remaining=set_of(field,&form).p;
        let mut finite_factors=Vec::new();
        for &root in &rational {
            if root==field.size {continue;}
            let mut linear=pz();linear.n=2;linear.c[0]=field.neg(root);linear.c[1]=1;
            let (quotient,remainder)=pdivrem(field,&remaining,&linear);
            if remainder.n!=0 {return Err("rational branch division failed");}
            remaining=quotient;
            finite_factors.push(branch_factor_vec(linear));
        }
        match remaining.n.saturating_sub(1) {
            0=>{},
            1=>return Err("unremoved rational branch root"),
            2|3=>{
                let coefficients=branch_factor_vec(remaining);
                self.symbolic_extension(&coefficients)?;
                finite_factors.push(coefficients);
            },
            4=>{
                let mut x=pz();x.n=2;x.c[1]=1;
                let xq2=symbolic_mod_pow(field,&x,(field.size as u64).pow(2),&remaining);
                let low=pgcd(field,&remaining,&branch_difference(field,&xq2,&x));
                if low.n==1 {
                    let coefficients=branch_factor_vec(remaining);
                    self.symbolic_extension(&coefficients)?;
                    finite_factors.push(coefficients);
                } else if low.n==5 {
                    let (left,right)=split_two_quadratics(field,&remaining)?;
                    for factor in [left,right] {
                        let coefficients=branch_factor_vec(factor);
                        self.symbolic_extension(&coefficients)?;
                        finite_factors.push(coefficients);
                    }
                } else {return Err("unexpected degree-one or degree-two factor split");}
            },
            _=>return Err("invalid finite branch degree"),
        }
        finite_factors.sort();
        let mut reconstructed=pz();reconstructed.n=1;reconstructed.c[0]=1;
        for factor in &finite_factors {
            let mut polynomial=pz();polynomial.n=factor.len();
            polynomial.c[..factor.len()].copy_from_slice(factor);
            reconstructed=pmul(field,&reconstructed,&polynomial);
        }
        if reconstructed!=set_of(field,&form).p {return Err("branch factor product mismatch");}
        let result=BranchFactorization{infinity:rational.contains(&field.size),finite_factors};
        if result.pattern().iter().sum::<usize>()!=4 {return Err("branch degree count mismatch");}
        Ok(result)
    }
}
