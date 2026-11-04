// Exact K-projective maps sending beta to alpha in a symbolic extension.

pub struct ExceptionalCandidateSummary {
    pub rational_count: usize,
    pub nonrational_count: usize,
    pub duplicate_count: usize,
    /// Sorted exact structure ordinal and independently checked support geometry.
    pub exceptional: Vec<(u64,SupportGeometry)>,
    /// Half-open intervals partitioning the generic complement.
    pub generic_intervals: Vec<(u64,u64)>,
    pub structures: u64,
}

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
    pub fn checked_exceptional_candidates(&self,form:[u32;5],
        image_index:&RationalImageIndex,cocycle_indices:&[CocycleIndex],
        maximum_rational_candidates:u64,maximum_nonrational_maps:u64,
        maximum_total_candidates:u64)->Result<ExceptionalCandidateSummary,&'static str> {
        let first=cocycle_indices.first().ok_or("missing first cocycle index")?;
        let rational=self.rational_root_collision_ordinals(form,image_index,cocycle_indices,
            maximum_rational_candidates)?;
        let nonrational=self.nonrational_root_collision_ordinals(form,cocycle_indices,
            maximum_nonrational_maps)?;
        let mut ordinals=rational.clone();ordinals.extend_from_slice(&nonrational);
        ordinals.sort_unstable();ordinals.dedup();
        if ordinals.len() as u64>maximum_total_candidates {
            return Err("checked candidate limit exceeded");
        }
        let structures=self.structure_count()?;
        let mut exceptional=Vec::with_capacity(ordinals.len());
        let mut generic_intervals=Vec::new();
        let mut cursor=0u64;
        for ordinal in ordinals {
            if ordinal>=structures {return Err("candidate ordinal outside structure coverage");}
            if cursor<ordinal {generic_intervals.push((cursor,ordinal));}
            let matrix=self.structure_matrix(first,ordinal)?;
            let transformed=self.transform_form(form,matrix)?;
            let geometry=self.support_geometry(&self.conjugate_forms(transformed)?)?;
            if geometry.pairwise_disjoint {
                return Err("generated exceptional candidate has disjoint support");
            }
            exceptional.push((ordinal,geometry));
            cursor=ordinal+1;
        }
        if cursor<structures {generic_intervals.push((cursor,structures));}
        let covered=generic_intervals.iter().try_fold(exceptional.len() as u64,
            |sum,(start,end)|sum.checked_add(end-start))
            .ok_or("candidate coverage count overflow")?;
        if covered!=structures {return Err("candidate complement coverage mismatch");}
        Ok(ExceptionalCandidateSummary{
            rational_count:rational.len(),nonrational_count:nonrational.len(),
            duplicate_count:rational.len()+nonrational.len()-exceptional.len(),
            exceptional,generic_intervals,structures,
        })
    }

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
