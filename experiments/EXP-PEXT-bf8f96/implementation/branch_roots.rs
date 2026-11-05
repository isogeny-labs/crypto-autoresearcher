// All finite roots of a squarefree binary quartic in one explicit K extension.

pub struct BranchRoots<'a> {
    pub factorization: BranchFactorization,
    pub extension: Option<SymbolicExtension<'a>>,
    pub finite_roots: Vec<SymbolicElement>,
}

fn embed_second_quadratic(field:&Fld,extension:&SymbolicExtension<'_>,
    first:&[u32],second:&[u32])->Result<SymbolicElement,&'static str> {
    let four=field.int(4);
    let two=field.int(2);
    let discriminant=|factor:&[u32]| field.sub(field.mul(factor[1],factor[1]),field.mul(four,factor[0]));
    let first_discriminant=discriminant(first);
    let second_discriminant=discriminant(second);
    if first_discriminant==0 || second_discriminant==0 {
        return Err("repeated quadratic root");
    }
    let ratio=field.mul(second_discriminant,field.inv(first_discriminant));
    let slope=(0..field.size).find(|&value|field.mul(value,value)==ratio)
        .ok_or("quadratic discriminant ratio has no K square root")?;
    if slope==0 {return Err("quadratic embedding has zero slope");}
    // If u has trace -a1, write r=c+slope*u with trace -a2.
    let first_trace=field.neg(first[1]);
    let intercept=field.mul(field.sub(field.neg(second[1]),field.mul(slope,first_trace)),field.inv(two));
    let root=extension.add(extension.element(&[intercept])?,
        extension.mul(extension.element(&[slope])?,extension.variable()));
    if extension.evaluate(second,root)?!=extension.zero() {
        return Err("quadratic embedding does not annihilate target factor");
    }
    Ok(root)
}

impl Context {
    pub fn branch_roots(&self,form:[u32;5])->Result<BranchRoots<'_>,&'static str> {
        let factorization=self.factor_branch_form(form)?;
        let field=&self.field;
        let high=factorization.finite_factors.iter().filter(|factor|factor.len()>2).collect::<Vec<_>>();
        let extension=if high.is_empty() {None} else {Some(self.symbolic_extension(high[0])?)};
        let mut finite_roots=Vec::new();
        for factor in &factorization.finite_factors {
            let degree=factor.len()-1;
            if degree==1 {
                let root=field.neg(factor[0]);
                finite_roots.push(match &extension {
                    Some(ext)=>ext.element(&[root])?,
                    None=>SymbolicElement{coefficients:[root,0,0,0]},
                });
            } else {
                let ext=extension.as_ref().ok_or("missing symbolic root extension")?;
                let root=if factor==high[0] {ext.variable()}
                    else if degree==2 && ext.degree()==2 {
                        embed_second_quadratic(field,ext,high[0],factor)?
                    } else {return Err("unsupported mixed nonrational factor degrees");};
                let mut conjugate=root;
                for _ in 0..degree {
                    if ext.evaluate(factor,conjugate)?!=ext.zero() {
                        return Err("branch conjugate does not annihilate its factor");
                    }
                    finite_roots.push(conjugate);
                    conjugate=ext.power(conjugate,field.size as u64);
                }
                if conjugate!=root {return Err("branch conjugate orbit length mismatch");}
            }
        }
        finite_roots.sort_by_key(SymbolicElement::coefficients);
        finite_roots.dedup();
        if finite_roots.len()+factorization.infinity as usize!=4 {
            return Err("branch root count or distinctness mismatch");
        }
        for &root in &finite_roots {
            let zero=match &extension {
                Some(ext)=>ext.evaluate(&form,root)?==ext.zero(),
                None=>form.iter().rev().fold(0,|acc,&coefficient|
                    field.add(field.mul(acc,root.coefficients[0]),coefficient))==0,
            };
            if !zero {return Err("branch root does not annihilate quartic");}
        }
        Ok(BranchRoots{factorization,extension,finite_roots})
    }
}
