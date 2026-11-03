// Exact K-projective maps sending beta to alpha in a symbolic extension.

impl SymbolicExtension<'_> {
    pub fn projective_root_maps(&self,alpha:SymbolicElement,beta:SymbolicElement,
        maximum_candidates:u64)->Result<Vec<[u32;4]>,&'static str> {
        for element in [alpha,beta] {
            if element.coefficients.iter().any(|&value|value>=self.field.size)
                || element.coefficients[self.degree..].iter().any(|&value|value!=0) {
                return Err("root map element outside symbolic basis");
            }
        }
        let product=self.mul(alpha,beta);
        let one=self.one();
        let minus_product=self.sub(self.zero(),product);
        let minus_alpha=self.sub(self.zero(),alpha);
        let columns=[beta,one,minus_product,minus_alpha];
        let mut rows=vec![[0u32;4];self.degree];
        for (column,element) in columns.iter().enumerate() {
            for (row,entry) in rows.iter_mut().enumerate() {
                entry[column]=element.coefficients[row];
            }
        }
        let field=self.field;
        let mut pivots=Vec::new();
        for column in 0..4 {
            let pivot=(pivots.len()..self.degree).find(|&row|rows[row][column]!=0);
            let Some(pivot)=pivot else {continue};
            rows.swap(pivots.len(),pivot);
            let inverse=field.inv(rows[pivots.len()][column]);
            for entry in &mut rows[pivots.len()] {*entry=field.mul(*entry,inverse);}
            let pivot_row=rows[pivots.len()];
            for (row_index,row) in rows.iter_mut().enumerate() {
                if row_index==pivots.len() {continue;}
                let scale=row[column];
                for j in 0..4 {row[j]=field.sub(row[j],field.mul(scale,pivot_row[j]));}
            }
            pivots.push(column);
            if pivots.len()==self.degree {break;}
        }
        let free=(0..4).filter(|column|!pivots.contains(column)).collect::<Vec<_>>();
        if free.len()>2 {return Err("unexpected root map kernel dimension");}
        let expected=match free.len() {0=>0,1=>1,2=>field.size as u64+1,_=>unreachable!()};
        if expected>maximum_candidates {return Err("root map candidate limit exceeded");}
        let mut maps=Vec::new();
        let mut append=|free_values:&[u32]| -> Result<(),&'static str> {
            let mut vector=[0u32;4];
            for (&column,&value) in free.iter().zip(free_values) {vector[column]=value;}
            for (row,&column) in pivots.iter().enumerate() {
                let mut value=0;
                for &free_column in &free {
                    value=field.add(value,field.mul(rows[row][free_column],vector[free_column]));
                }
                vector[column]=field.neg(value);
            }
            let determinant=field.sub(field.mul(vector[0],vector[3]),
                field.mul(vector[1],vector[2]));
            if determinant==0 {return Ok(());}
            let first=*vector.iter().find(|&&value|value!=0).ok_or("zero root map vector")?;
            for value in &mut vector {*value=field.mul(*value,field.inv(first));}
            let coefficients=vector.map(|value|self.element(&[value])).into_iter().collect::<Result<Vec<_>,_>>()?;
            let residual=self.sub(self.add(self.mul(coefficients[0],beta),coefficients[1]),
                self.add(self.mul(coefficients[2],product),self.mul(coefficients[3],alpha)));
            if residual!=self.zero() {return Err("root map kernel residual mismatch");}
            maps.push(vector);Ok(())
        };
        match free.len() {
            0=>{},
            1=>append(&[1])?,
            2=>{
                for value in 0..field.size {append(&[1,value])?;}
                append(&[0,1])?;
            },
            _=>unreachable!(),
        }
        maps.sort();maps.dedup();
        Ok(maps)
    }
}

impl Context {
    /// Nonrational branch-root contribution to the exceptional structure set.
    /// The caller must also union the complete K-rational-root contribution.
    pub fn nonrational_root_collision_ordinals(&self,form:[u32;5],
        cocycle_indices:&[CocycleIndex],maximum_maps:u64)->Result<Vec<u64>,&'static str> {
        let expected_powers=(self.field.n-1)/2;
        if cocycle_indices.len()!=expected_powers as usize
            || cocycle_indices.iter().enumerate().any(|(i,index)|index.power!=i as u32+1
                || (index.prime,index.degree,index.primitive_polynomial_index)
                    !=(self.field.q,self.field.n,self.field.idx_of[2])) {
            return Err("nonrational cocycle index powers incomplete");
        }
        let roots=self.branch_roots(form)?;
        let Some(extension)=roots.extension.as_ref() else {return Ok(Vec::new())};
        let q=self.field.size as u64;
        let root_degree=|root:SymbolicElement| -> Result<usize,&'static str> {
            let mut conjugate=root;
            for degree in 1..=extension.degree() {
                conjugate=extension.power(conjugate,q);
                if conjugate==root {return Ok(degree);}
            }
            Err("nonrational branch root orbit fails closure")
        };
        let degrees=roots.finite_roots.iter().map(|&root|root_degree(root))
            .collect::<Result<Vec<_>,_>>()?;
        let mut count=0u64;
        let mut ordinals=Vec::new();
        for (power,index) in cocycle_indices.iter().enumerate() {
            for (a,&alpha) in roots.finite_roots.iter().enumerate() {
                if degrees[a]==1 {continue;}
                for (g,&gamma) in roots.finite_roots.iter().enumerate() {
                    if degrees[a]!=degrees[g] {continue;}
                    let beta=extension.frobenius(gamma,power as u32+1)?;
                    let bound=if degrees[a]==2 {q+1} else {1};
                    count=count.checked_add(bound).ok_or("nonrational map count overflow")?;
                    if count>maximum_maps {return Err("nonrational map limit exceeded");}
                    for matrix in extension.projective_root_maps(alpha,beta,bound)? {
                        if let Some(ordinal)=self.cocycle_ordinal(index,matrix)? {
                            ordinals.push(ordinal);
                        }
                    }
                }
            }
        }
        ordinals.sort_unstable();ordinals.dedup();
        Ok(ordinals)
    }
}
