//! Prospective degree-two quotient construction; no experiment entry point.
//! Reuses the committed census arithmetic without modifying or invoking its main.
//! Source SHA256: 0336e5c594fc7f27d56a27ed957e281af7e9af9d0b15df4797a12bf8e86d5251.
//! Field elements are the source's logarithmic encoding, NOT integer residues.
#![allow(dead_code)]

mod implementation {
    include!("../../EXP-PEXT-212d5c/implementation/cover_census_n7.rs");
    use std::collections::{BTreeSet, BTreeMap as OrderedMap};

    #[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord)]
    pub enum Point { Infinity, Affine { x: u32, y: u32 } }
    #[derive(Clone, Copy, Debug, PartialEq, Eq)]
    pub enum QuarticPoint { PlusInfinity, MinusInfinity, Affine { t: u32, w: u32 } }
    #[derive(Debug)]
    pub struct Coset {
        pub representative: Point,
        /// Each (P,Q) certifies P = representative + 2Q.
        pub members: Vec<(Point, Point)>,
    }
    #[derive(Clone, Debug)]
    pub struct ModelWitness {
        pub model: [u32;3],
        /// old x = u^2 * new x + r, old y = u^3 * new y.
        pub u: u32,
        pub r: u32,
    }
    #[derive(Debug)]
    pub struct CurveClass {
        pub representative: [u32;3],
        /// Every nonsingular normalized model in this isomorphism orbit.
        pub members: Vec<ModelWitness>,
    }
    pub struct Context { field: Fld }
    pub struct Curve<'a> { f: &'a Fld, model: Cv }
    #[derive(Debug, PartialEq, Eq)]
    pub struct FieldIdentity {
        pub prime: u32,
        pub degree: u32,
        /// Low-to-high coefficients, including monic leading coefficient.
        pub modulus: Vec<u32>,
        pub primitive_polynomial_index: u32,
        pub logarithm_to_polynomial_index: Vec<u32>,
    }
    #[derive(Debug)]
    pub struct SquareClasses {
        pub geometric_rank: usize,
        pub arithmetic_rank: usize,
        pub contains_nonsquare_constant: bool,
        pub relations: Vec<(u8,bool)>,
    }
    #[derive(Debug, PartialEq, Eq)]
    pub struct SupportGeometry {
        pub pairwise_disjoint: bool,
        pub geometric_rank: usize,
        pub branch_points: usize,
        pub geometric_genus: usize,
    }
    pub struct CocycleIndex {
        prime:u32,
        degree:u32,
        primitive_polynomial_index:u32,
        power:u32,
        nonrational_reps:Vec<u32>,
        entries:HashMap<[u32;4],u64>,
    }
    impl CocycleIndex {
        pub fn len(&self)->usize {self.entries.len()}
        pub fn power(&self)->u32 {self.power}
    }
    pub struct RationalImageIndex {
        prime:u32,
        degree:u32,
        primitive_polynomial_index:u32,
        by_root:Vec<Vec<u64>>,
        entries:u64,
    }
    impl RationalImageIndex {
        pub fn entries(&self)->u64 {self.entries}
        pub fn roots(&self)->usize {self.by_root.len()}
    }

    impl Context {
        pub fn new(q: u32, n: u32, maximum_field_elements: u32) -> Result<Self, &'static str> {
            // The borrowed builder uses u32 polynomial arithmetic. Limit q to
            // the declared design domain and sizes so a+b cannot overflow.
            if ![3,5,7,11,13].contains(&q) || n == 0 {
                return Err("requires declared prime q in {3,5,7,11,13} and positive degree");
            }
            let size = q.checked_pow(n).ok_or("field size overflow")?;
            if size > maximum_field_elements || size > u32::MAX/2 { return Err("field allocation or arithmetic limit exceeded"); }
            Ok(Self { field: Fld::build(q, n) })
        }
        pub fn integer(&self, value: i64) -> u32 { self.field.int(value) }
        pub fn size(&self) -> u32 { self.field.size }
        /// Exact polynomial-basis index for each logarithmically encoded element.
        pub fn encoding(&self) -> &[u32] { &self.field.idx_of }
        pub fn identity(&self) -> FieldIdentity {
            let f=&self.field;
            let mut modulus=vec![0;f.n as usize+1];
            if f.n>1 {
                // The polynomial-basis element X has index q. Recover the
                // defining relation X^n=-sum(modulus[i]*X^i) from its power.
                let x=f.el_of[f.q as usize];
                let mut index=f.idx_of[f.pow(x,f.n as u64) as usize];
                for a in modulus.iter_mut().take(f.n as usize) { *a=(f.q-index%f.q)%f.q; index/=f.q; }
                assert_eq!(index,0);
            }
            modulus[f.n as usize]=1;
            FieldIdentity{prime:f.q,degree:f.n,modulus,
                primitive_polynomial_index:f.idx_of[2],
                logarithm_to_polynomial_index:f.idx_of.clone()}
        }
        pub fn curve(&self, a2: u32, a4: u32, a6: u32) -> Result<Curve<'_>, &'static str> {
            if [a2,a4,a6].iter().any(|&a| a >= self.field.size) { return Err("invalid coefficient encoding"); }
            let model = Cv { a2, a4, a6 };
            if disc(&self.field, &model) == 0 { return Err("singular curve"); }
            Ok(Curve { f: &self.field, model })
        }

        /// All geometric square relations among <=7 squarefree binary quartics.
        /// A returned (mask,false) is a nonsquare-constant relation, not a square.
        /// This certifies K(t) square classes; it does NOT certify F_q descent.
        pub fn square_relations(&self, forms: &[[u32;5]]) -> Result<Vec<(u8,bool)>, &'static str> {
            if forms.len() > 7 { return Err("at most seven conjugate forms"); }
            let f = &self.field;
            let mut entries = Vec::new();
            for form in forms {
                if form.iter().any(|&a| a >= f.size) { return Err("invalid form coefficient"); }
                let degree = form.iter().rposition(|&a| a != 0).ok_or("zero form")?;
                if degree < 3 { return Err("multiple root at projective infinity"); }
                let set = set_of(f, form);
                let mut derivative = pz();
                derivative.n = degree;
                for i in 1..=degree { derivative.c[i-1] = f.mul(f.int(i as i64), form[i]); }
                if pgcd(f, &set.p, &ptrim(derivative)).n != 1 { return Err("repeated branch root"); }
                entries.push((set, f.is_sq(form[degree])));
            }
            let mut relations = Vec::new();
            for mask in 0u8..(1u16 << forms.len()) as u8 {
                let mut parity = Set { p: { let mut p=pz(); p.n=1; p.c[0]=1; p }, inf:false };
                let mut constant_square = true;
                for (i, (set, square)) in entries.iter().enumerate() {
                    if mask & (1<<i) != 0 {
                        parity=sdiff(f,&parity,set);
                        if !square { constant_square = !constant_square; }
                    }
                }
                if parity.p.n == 1 && !parity.inf { relations.push((mask,constant_square)); }
            }
            Ok(relations)
        }
        pub fn square_classes(&self,forms:&[[u32;5]]) -> Result<SquareClasses,&'static str> {
            let relations=self.square_relations(forms)?;
            let squares=relations.iter().filter(|(_,square)|*square).count();
            if !relations.len().is_power_of_two() || !squares.is_power_of_two() {
                return Err("relation kernel is not a binary subspace");
            }
            Ok(SquareClasses{geometric_rank:forms.len()-relations.len().ilog2() as usize,
                arithmetic_rank:forms.len()-squares.ilog2() as usize,
                contains_nonsquare_constant:relations.iter().any(|(_,square)|!square),relations})
        }
        /// Exact geometric support arithmetic for a complete Frobenius orbit
        /// of squarefree quartics. Coefficient classes and descent are separate.
        pub fn support_geometry(&self, forms:&[[u32;5]]) -> Result<SupportGeometry,&'static str> {
            let f=&self.field;
            if ![3,5,7].contains(&f.n) || forms.len()!=f.n as usize {
                return Err("requires complete degree-3/5/7 conjugate orbit");
            }
            let mut supports=Vec::with_capacity(forms.len());
            for (i,form) in forms.iter().enumerate() {
                if form.iter().any(|&a|a>=f.size) {return Err("invalid form coefficient");}
                let degree=form.iter().rposition(|&a|a!=0).ok_or("zero form")?;
                if degree<3 {return Err("multiple root at projective infinity");}
                let set=set_of(f,form);
                let mut derivative=pz(); derivative.n=degree;
                for j in 1..=degree {derivative.c[j-1]=f.mul(f.int(j as i64),form[j]);}
                if pgcd(f,&set.p,&ptrim(derivative)).n!=1 {return Err("repeated branch root");}
                if forms[(i+1)%forms.len()]!=form.map(|a|f.frob(a)) {
                    return Err("Frobenius conjugate sequence mismatch");
                }
                supports.push(set);
            }
            let disjoint=(0..supports.len()).all(|i|
                (i+1..supports.len()).all(|j|!meets(f,&supports[i],&supports[j])));
            if disjoint {
                let n=forms.len();
                return Ok(SupportGeometry{pairwise_disjoint:true,geometric_rank:n,
                    branch_points:4*n,geometric_genus:(n-1)*(1<<n)+1});
            }
            let one=Set{p:{let mut p=pz();p.n=1;p.c[0]=1;p},inf:false};
            let mut span=vec![one];let mut total=one;
            for support in &supports {
                total=union(f,&total,support);
                if span.contains(support) {continue;}
                let add:Vec<Set>=span.iter().map(|v|sdiff(f,v,support)).collect();
                span.extend(add);
            }
            if !span.len().is_power_of_two() {return Err("support span cardinality");}
            let rank=span.len().ilog2() as usize;
            let branches=size(&total);
            if rank==0 || branches<4 {return Err("invalid branch rank or count");}
            if span.iter().skip(1).any(|v|size(v)<2 || size(v)%2!=0) {
                return Err("invalid character branch parity");
            }
            let genus=if rank==1 {(branches-2)/2}
                else {1+(1<<(rank-2))*(branches-4)};
            let character_sum:usize=span.iter().skip(1).map(|v|(size(v)-2)/2).sum();
            if genus!=character_sum {return Err("support genus character-sum mismatch");}
            Ok(SupportGeometry{pairwise_disjoint:false,geometric_rank:rank,
                branch_points:branches,geometric_genus:genus})
        }
        /// Explicit pointed K-isomorphism, retaining the actual curve model.
        pub fn transform_model(&self,model:[u32;3],u:u32,r:u32)->Result<[u32;3],&'static str> {
            self.curve(model[0],model[1],model[2])?;
            let f=&self.field;
            if u==0 || u>=f.size || r>=f.size { return Err("invalid model isomorphism parameters"); }
            let [a2,a4,a6]=model; let r2=f.mul(r,r);
            let output=[f.div(f.add(f.mul(f.int(3),r),a2),f.pow(u,2)),
                f.div(f.add(f.add(f.mul(f.int(3),r2),f.mul(f.int(2),f.mul(a2,r))),a4),f.pow(u,4)),
                f.div(cubic(f,&Cv{a2,a4,a6},r),f.pow(u,6))];
            self.curve(output[0],output[1],output[2])?;
            Ok(output)
        }
        /// A witness from any nonsingular long model to the chosen family.
        pub fn normalize_model(&self,model:[u32;3])->Result<ModelWitness,&'static str> {
            self.curve(model[0],model[1],model[2])?;
            let f=&self.field;
            let r=if f.q!=3 { f.neg(f.div(model[0],f.int(3))) }
                else if model[0]!=0 { f.neg(f.div(model[1],f.mul(f.int(2),model[0]))) }
                else { 0 };
            Ok(ModelWitness{model:self.transform_model(model,1,r)?,u:1,r})
        }
        pub fn curve_model_domain_size(&self)->u64 {
            let size=self.field.size as u64;
            if self.field.q==3 { 2*size*size-size } else { size*size }
        }
        /// All pointed K-isomorphism classes in complete normalized families.
        /// A count ceiling is enforced before allocating the coverage set.
        /// Class order is family A then B in char3, otherwise coefficient order.
        pub fn visit_curve_classes<F>(&self,maximum_models:u64,mut body:F)->Result<u64,&'static str>
        where F:FnMut(CurveClass)->Result<(),&'static str> {
            if self.curve_model_domain_size()>maximum_models { return Err("curve model domain limit exceeded"); }
            let f=&self.field; let mut covered=BTreeSet::new(); let mut count=0u64;
            let mut emit=|model:[u32;3]|->Result<(),&'static str> {
                if covered.contains(&model)||self.curve(model[0],model[1],model[2]).is_err() { return Ok(()); }
                let mut witnesses=OrderedMap::new();
                for u in 1..f.size {
                    let shifts=if f.q==3 && model[0]==0 { f.size } else { 1 };
                    for r in 0..shifts {
                        let image=self.transform_model(model,u,r)?;
                        witnesses.entry(image).or_insert(ModelWitness{model:image,u,r});
                    }
                }
                for image in witnesses.keys() {
                    if !covered.insert(*image) { return Err("overlapping curve isomorphism classes"); }
                }
                body(CurveClass{representative:model,members:witnesses.into_values().collect()})?;
                count+=1; Ok(())
            };
            if f.q==3 { for a2 in 1..f.size { for a6 in 0..f.size { emit([a2,0,a6])?; } } }
            for a4 in 0..f.size { for a6 in 0..f.size { emit([0,a4,a6])?; } }
            Ok(count)
        }
        /// Move zeros by N using the literal adjugate substitution. No monic
        /// normalization: F(dX-bZ,-cX+aZ) retains the curve's scalar class.
        pub fn transform_form(&self, form:[u32;5], matrix:[u32;4])->Result<[u32;5],&'static str> {
            self.normalize_matrix(matrix)?;
            if form.iter().any(|&a|a>=self.field.size) { return Err("invalid form coefficient"); }
            Ok(mob(&self.field,&form,&matrix))
        }
        pub fn normalize_matrix(&self,matrix:[u32;4])->Result<[u32;4],&'static str> {
            let f=&self.field;
            if matrix.iter().any(|&a|a>=f.size) { return Err("invalid matrix coefficient"); }
            if f.mul(matrix[0],matrix[3])==f.mul(matrix[1],matrix[2]) { return Err("singular projective matrix"); }
            let first=*matrix.iter().find(|&&a|a!=0).unwrap();
            Ok(matrix.map(|a|f.div(a,first)))
        }
        /// tau=N^-1 sigma N; returns the normalized linear part N^-1 sigma(N).
        pub fn structure_cocycle(&self,matrix:[u32;4])->Result<[u32;4],&'static str> {
            let m=self.normalize_matrix(matrix)?; let f=&self.field;
            let adj=[m[3],f.neg(m[1]),f.neg(m[2]),m[0]];
            self.normalize_matrix(mmul(f,&adj,&mfrob(f,&m)))
        }
        /// N^-1 sigma^k(N), normalized in the repository's left-coset order.
        pub fn structure_cocycle_power(&self,matrix:[u32;4],k:u32)->Result<[u32;4],&'static str> {
            if ![3,5,7].contains(&self.field.n) || k==0 || k>=self.field.n {
                return Err("invalid nontrivial Frobenius power");
            }
            let m=self.normalize_matrix(matrix)?; let f=&self.field;
            let adj=[m[3],f.neg(m[1]),f.neg(m[2]),m[0]];
            let mut conjugate=m;
            for _ in 0..k {conjugate=mfrob(f,&conjugate);}
            self.normalize_matrix(mmul(f,&adj,&conjugate))
        }
        /// One-time complete cocycle-to-ordinal table for a specified k.
        /// A duplicate would contradict the left-coset transversal contract.
        pub fn cocycle_index(&self,k:u32,maximum_entries:u64)->Result<CocycleIndex,&'static str> {
            if ![3,5,7].contains(&self.field.n) || k==0 || k>=self.field.n {
                return Err("invalid nontrivial Frobenius power");
            }
            let expected=self.structure_count()?;
            if expected>maximum_entries {return Err("cocycle index entry limit exceeded");}
            let capacity=usize::try_from(expected).map_err(|_|"cocycle index allocation limit")?;
            let mut entries=HashMap::with_capacity(capacity);let mut ordinal=0u64;
            self.visit_structures(expected,|matrix| {
                let key=self.structure_cocycle_power(matrix,k)?;
                if entries.insert(key,ordinal).is_some() {return Err("duplicate projective cocycle");}
                ordinal+=1;Ok(())
            })?;
            if ordinal!=expected || entries.len()!=capacity {return Err("incomplete cocycle index");}
            let nonrational_reps=trans(&self.field).rep_b;
            let group=(self.field.q as u64).pow(3)-self.field.q as u64;
            if (nonrational_reps.len() as u64).checked_mul(group)
                !=Some(self.field.size as u64-self.field.q as u64) {
                return Err("nonrational point orbit coverage mismatch");
            }
            Ok(CocycleIndex{prime:self.field.q,degree:self.field.n,
                primitive_polynomial_index:self.field.idx_of[2],power:k,
                nonrational_reps,entries})
        }
        pub fn cocycle_ordinal(&self,index:&CocycleIndex,cocycle:[u32;4])
            ->Result<Option<u64>,&'static str> {
            if (index.prime,index.degree,index.primitive_polynomial_index)
                !=(self.field.q,self.field.n,self.field.idx_of[2]) {
                return Err("cocycle index field mismatch");
            }
            let key=self.normalize_matrix(cocycle)?;
            Ok(index.entries.get(&key).copied())
        }
        /// Once-per-field exact index for N(alpha) in P^1(F_q). The projective
        /// root encoding is 0..Q-1 for finite points and Q for infinity.
        pub fn rational_image_index(&self,maximum_entries:u64)
            ->Result<RationalImageIndex,&'static str> {
            let f=&self.field;let structures=self.structure_count()?;
            let fq=(0..f.size).filter(|&x|f.in_fq(x)).collect::<Vec<_>>();
            if fq.len()!=f.q as usize {return Err("base field point count mismatch");}
            let total=structures.checked_mul(f.q as u64+1).ok_or("rational image count overflow")?;
            if total>maximum_entries {return Err("rational image entry limit exceeded");}
            let roots=f.size as usize+1;
            let per_root=usize::try_from(total/(roots as u64)).map_err(|_|"rational image allocation limit")?;
            if total%(roots as u64)!=0 {return Err("nonintegral rational image bucket size");}
            let mut by_root=(0..roots).map(|_|Vec::with_capacity(per_root)).collect::<Vec<_>>();
            let mut ordinal=0u64;
            self.visit_structures(structures,|matrix| {
                let adj=[matrix[3],f.neg(matrix[1]),f.neg(matrix[2]),matrix[0]];
                for &image in fq.iter().chain(std::iter::once(&f.size)) {
                    let root=apply(f,&adj,image,f.size);
                    by_root[root as usize].push(ordinal);
                }
                ordinal+=1;Ok(())
            })?;
            if ordinal!=structures || by_root.iter().any(|bucket|bucket.len()!=per_root) {
                return Err("rational image index coverage mismatch");
            }
            Ok(RationalImageIndex{prime:f.q,degree:f.n,
                primitive_polynomial_index:f.idx_of[2],by_root,entries:total})
        }
        pub fn rational_image_ordinals<'a>(&self,index:&'a RationalImageIndex,root:u32)
            ->Result<&'a [u64],&'static str> {
            if (index.prime,index.degree,index.primitive_polynomial_index)
                !=(self.field.q,self.field.n,self.field.idx_of[2]) {
                return Err("rational image index field mismatch");
            }
            index.by_root.get(root as usize).map(Vec::as_slice).ok_or("invalid projective root")
        }
        /// Exact collision indices for an ordered distinct pair of K-rational
        /// branch roots. Shared nonrational images are normalized by the left
        /// PGL2(F_q) action; the output is in the frozen structure order.
        pub fn rational_pair_collision_ordinals(&self,index:&CocycleIndex,
            alpha:u32,gamma:u32,maximum_candidates:u64)->Result<Vec<u64>,&'static str> {
            let f=&self.field;let inf=f.size;
            if alpha>inf || gamma>inf || alpha==gamma {return Err("invalid distinct rational root pair");}
            if (index.prime,index.degree,index.primitive_polynomial_index)
                !=(f.q,f.n,f.idx_of[2]) {return Err("cocycle index field mismatch");}
            let k=index.power;
            if k==0 || k>=f.n {return Err("invalid cocycle power");}
            let expected=(index.nonrational_reps.len() as u64).checked_mul(f.size as u64-1)
                .ok_or("rational pair candidate count overflow")?;
            if expected>maximum_candidates {return Err("rational pair candidate limit exceeded");}
            let delta=(0..=inf).find(|&v|v!=alpha && v!=gamma).ok_or("missing third source point")?;
            let source=from_triple(f,alpha,gamma,delta,inf);
            let source_adj=[source[3],f.neg(source[1]),f.neg(source[2]),source[0]];
            let mut ordinals=Vec::with_capacity(expected as usize);
            for &x in &index.nonrational_reps {
                let mut y=x;
                for _ in 0..f.n-k {y=f.frob(y);}
                if y==x {return Err("nonrational orbit representative fixed by Frobenius");}
                for z in 0..=inf {
                    if z==x || z==y {continue;}
                    let destination=from_triple(f,x,y,z,inf);
                    let matrix=self.normalize_matrix(mmul(f,&destination,&source_adj))?;
                    let cocycle=self.structure_cocycle_power(matrix,k)?;
                    let ordinal=self.cocycle_ordinal(index,cocycle)?
                        .ok_or("rational pair cocycle absent from complete index")?;
                    ordinals.push(ordinal);
                }
            }
            ordinals.sort_unstable();ordinals.dedup();
            if ordinals.len()!=expected as usize {return Err("duplicate rational pair candidate");}
            Ok(ordinals)
        }
        /// K-rational projective roots of a squarefree binary quartic.
        pub fn rational_branch_roots(&self,form:[u32;5])->Result<Vec<u32>,&'static str> {
            let f=&self.field;
            if form.iter().any(|&a|a>=f.size) {return Err("invalid form coefficient");}
            let degree=form.iter().rposition(|&a|a!=0).ok_or("zero form")?;
            if degree<3 {return Err("multiple root at projective infinity");}
            let set=set_of(f,&form);let mut derivative=pz();derivative.n=degree;
            for i in 1..=degree {derivative.c[i-1]=f.mul(f.int(i as i64),form[i]);}
            if pgcd(f,&set.p,&ptrim(derivative)).n!=1 {return Err("repeated branch root");}
            let mut roots=Vec::new();
            for x in 0..f.size {
                let value=form.iter().rev().fold(0,|acc,&coefficient|
                    f.add(f.mul(acc,x),coefficient));
                if value==0 {roots.push(x);}
            }
            if degree==3 {roots.push(f.size);}
            Ok(roots)
        }
        /// Complete degree-one-root contribution to the exceptional ordinal
        /// set. Other root degrees must be generated separately before the
        /// generic complement is certified.
        pub fn rational_root_collision_ordinals(&self,form:[u32;5],
            image_index:&RationalImageIndex,cocycle_indices:&[CocycleIndex],
            maximum_candidates:u64)->Result<Vec<u64>,&'static str> {
            let n=self.field.n as usize;
            if ![3,5,7].contains(&n) || cocycle_indices.len()!=(n-1)/2 {
                return Err("incomplete collision Frobenius powers");
            }
            for (i,index) in cocycle_indices.iter().enumerate() {
                if index.power!=(i+1) as u32 {return Err("collision Frobenius power order mismatch");}
                if (index.prime,index.degree,index.primitive_polynomial_index)
                    !=(self.field.q,self.field.n,self.field.idx_of[2]) {
                    return Err("cocycle index field mismatch");
                }
            }
            if (image_index.prime,image_index.degree,image_index.primitive_polynomial_index)
                !=(self.field.q,self.field.n,self.field.idx_of[2]) {
                return Err("rational image index field mismatch");
            }
            let roots=self.rational_branch_roots(form)?;
            let self_count=if roots.is_empty() {0} else {
                self.rational_image_ordinals(image_index,roots[0])?.len() as u64
            };
            let pair_count=(cocycle_indices[0].nonrational_reps.len() as u64)
                .checked_mul(self.field.size as u64-1).ok_or("pair count overflow")?;
            let r=roots.len() as u64;
            let bound=r.checked_mul(self_count)
                .and_then(|x|r.checked_mul(r.saturating_sub(1))
                    .and_then(|pairs|pairs.checked_mul(cocycle_indices.len() as u64))
                    .and_then(|pairs|pairs.checked_mul(pair_count))
                    .and_then(|pairs|x.checked_add(pairs)))
                .ok_or("rational root candidate count overflow")?;
            if bound>maximum_candidates {return Err("rational root candidate limit exceeded");}
            let capacity=usize::try_from(bound).map_err(|_|"rational root allocation limit")?;
            let mut ordinals=Vec::with_capacity(capacity);
            for &root in &roots {ordinals.extend_from_slice(self.rational_image_ordinals(image_index,root)?);}
            for index in cocycle_indices {
                for &alpha in &roots {for &gamma in &roots {
                    if alpha!=gamma {
                        ordinals.extend(self.rational_pair_collision_ordinals(index,alpha,gamma,pair_count)?);
                    }
                }}
            }
            ordinals.sort_unstable();ordinals.dedup();
            Ok(ordinals)
        }
        /// Exact count of left PGL2(Fq) cosets, before any transversal allocation.
        pub fn structure_count(&self)->Result<u64,&'static str> {
            if ![1,3,5,7].contains(&self.field.n) { return Err("transversal requires degree one or odd prime 3,5,7"); }
            let q=self.field.q as u128; let size=self.field.size as u128;
            u64::try_from((size*size*size-size)/(q*q*q-q)).map_err(|_|"structure count overflow")
        }
        /// Complete left-coset traversal with a pre-allocation count ceiling.
        pub fn visit_structures<F>(&self,maximum:u64,body:F)->Result<u64,&'static str>
        where F:FnMut([u32;4])->Result<(),&'static str> {
            self.visit_structures_range(0,self.structure_count()?,maximum,body)
        }
        /// Half-open slice of the same frozen transversal order. Arithmetic
        /// unranking skips the prefix without constructing or visiting it.
        pub fn visit_structures_range<F>(&self,start:u64,end:u64,maximum_emitted:u64,mut body:F)->Result<u64,&'static str>
        where F:FnMut([u32;4])->Result<(),&'static str> {
            let expected=self.structure_count()?;
            if start>end || end>expected { return Err("invalid structure range"); }
            if end-start>maximum_emitted { return Err("structure traversal limit exceeded"); }
            if start==end { return Ok(0); }
            let f=&self.field;let t=trans(f);let q=f.size as u64;
            let first=t.rep_a1.len() as u64;
            let second=(t.rep_a2.len() as u64)*(q-1);
            if t.total!=expected || first+second+(t.rep_b.len() as u64)*q*(q-1)!=expected {
                return Err("transversal cardinality mismatch");
            }
            // Rank in [0,Q] with one/two forbidden entries, in numeric order.
            let omit_one=|rank:u64,excluded:u32|->u32 {
                let x=rank as u32;if x>=excluded {x+1} else {x}
            };
            for index in start..end {
                let (a,b,c)=if index<first {
                    (t.inf,0,t.rep_a1[index as usize])
                } else if index<first+second {
                    let offset=index-first;let b=t.rep_a2[(offset/(q-1)) as usize];
                    (t.inf,b,omit_one(offset%(q-1),b))
                } else {
                    let offset=index-first-second;let a=t.rep_b[(offset/(q*(q-1))) as usize];
                    let tail=offset%(q*(q-1));let b=omit_one(tail/(q-1),a);
                    let low=a.min(b);let high=a.max(b);let mut c=(tail%(q-1)) as u32;
                    if c>=low {c+=1;} if c>=high {c+=1;} (a,b,c)
                };
                body(self.normalize_matrix(from_triple(f,a,b,c,t.inf))?)?;
            }
            Ok(end-start)
        }
        pub fn conjugate_forms(&self,form:[u32;5])->Result<Vec<[u32;5]>,&'static str> {
            if self.field.n>7 || form.iter().any(|&a|a>=self.field.size) {
                return Err("conjugate form outside supported domain");
            }
            let mut result=Vec::new(); let mut current=form;
            for _ in 0..self.field.n { result.push(current); current=current.map(|a|self.field.frob(a)); }
            if current!=form { return Err("Frobenius orbit does not close"); }
            Ok(result)
        }
    }

    impl Curve<'_> {
        pub fn contains(&self, point: Point) -> bool {
            match point {
                Point::Infinity => true,
                Point::Affine{x,y} => x < self.f.size && y < self.f.size && self.f.mul(y,y)==cubic(self.f,&self.model,x),
            }
        }
        pub fn points(&self) -> Vec<Point> {
            let f=self.f;
            let mut points=vec![Point::Infinity];
            for x in 0..f.size {
                let rhs=cubic(f,&self.model,x);
                if rhs==0 { points.push(Point::Affine{x,y:0}); }
                else if f.is_sq(rhs) {
                    let y=(rhs-1)/2+1;
                    points.push(Point::Affine{x,y}); points.push(Point::Affine{x,y:f.neg(y)});
                }
            }
            points.sort(); points
        }
        pub fn negate(&self, p: Point) -> Result<Point,&'static str> {
            if !self.contains(p) { return Err("point is not on this curve"); }
            Ok(match p { Point::Infinity=>p, Point::Affine{x,y}=>Point::Affine{x,y:self.f.neg(y)} })
        }
        pub fn add(&self, p: Point, q: Point) -> Result<Point,&'static str> {
            if !self.contains(p) || !self.contains(q) { return Err("point is not on this curve"); }
            let (x,y,u,v)=match (p,q) {
                (Point::Infinity,_)=>return Ok(q), (_,Point::Infinity)=>return Ok(p),
                (Point::Affine{x,y},Point::Affine{x:u,y:v})=>(x,y,u,v),
            };
            let f=self.f;
            if x==u && f.add(y,v)==0 { return Ok(Point::Infinity); }
            let slope=if x==u { f.div(dcubic(f,&self.model,x),f.mul(f.int(2),y)) }
                      else { f.div(f.sub(v,y),f.sub(u,x)) };
            let nx=f.sub(f.sub(f.sub(f.mul(slope,slope),self.model.a2),x),u);
            let ny=f.sub(f.mul(slope,f.sub(x,nx)),y);
            let result=Point::Affine{x:nx,y:ny};
            if !self.contains(result) { return Err("group-law result off curve"); }
            Ok(result)
        }
        pub fn quotient_classes(&self) -> Result<Vec<Coset>, &'static str> {
            let points=self.points();
            let mut halves=OrderedMap::new();
            for &p in &points { halves.entry(self.add(p,p)?).or_insert(p); }
            let mut covered=BTreeSet::new(); let mut result=Vec::new();
            for &representative in &points {
                if covered.contains(&representative) { continue; }
                let mut members=Vec::new();
                for (&double,&half) in &halves {
                    let point=self.add(representative,double)?;
                    if !covered.insert(point) { return Err("overlapping quotient cosets"); }
                    members.push((point,half));
                }
                result.push(Coset{representative,members});
            }
            if covered.len()!=points.len() || result.len()!=1+roots(self.f,&self.model).len() {
                return Err("quotient coverage or two-torsion cardinality mismatch");
            }
            Ok(result)
        }
        pub fn quotient_form(&self, target: Point) -> Result<[u32;5], &'static str> {
            if !self.contains(target) { return Err("target is off curve"); }
            let (u,v)=match target { Point::Infinity=>return Ok(b0form(&self.model)), Point::Affine{x,y}=>(x,y) };
            let f=self.f; let a2=self.model.a2;
            let c0=f.sub(f.sub(f.sub(f.mul(a2,a2),f.mul(f.int(2),f.mul(a2,u))),f.mul(f.int(3),f.mul(u,u))),f.mul(f.int(4),self.model.a4));
            Ok([c0,f.neg(f.mul(f.int(8),v)),f.neg(f.mul(f.int(2),f.add(a2,f.mul(f.int(3),u)))),0,1])
        }
        pub fn forward(&self, target: Point, point: Point) -> Result<QuarticPoint,&'static str> {
            let (u,v)=match target { Point::Infinity=>return Err("T=O uses the baseline cubic chart"),Point::Affine{x,y}=>(x,y) };
            if !self.contains(target)||!self.contains(point) { return Err("point or target off curve"); }
            if point==Point::Infinity { return Ok(QuarticPoint::PlusInfinity); }
            if point==target { return Ok(QuarticPoint::MinusInfinity); }
            let (x,y)=match point { Point::Affine{x,y}=>(x,y),_=>unreachable!() };
            let f=self.f;
            let t=if x==u {
                if v==0 { return Err("order-two pole not handled"); }
                f.neg(f.div(dcubic(f,&self.model,u),f.mul(f.int(2),v)))
            } else { f.div(f.add(y,v),f.sub(x,u)) };
            let w=f.sub(f.add(f.add(f.mul(f.int(2),x),self.model.a2),u),f.mul(t,t));
            Ok(QuarticPoint::Affine{t,w})
        }
        pub fn inverse(&self,target:Point,point:QuarticPoint)->Result<Point,&'static str> {
            let form=self.quotient_form(target)?;
            let (u,v)=match target { Point::Infinity=>return Err("T=O uses baseline chart"),Point::Affine{x,y}=>(x,y) };
            let (t,w)=match point { QuarticPoint::PlusInfinity=>return Ok(Point::Infinity),QuarticPoint::MinusInfinity=>return Ok(target),QuarticPoint::Affine{t,w}=>(t,w) };
            let f=self.f;
            if t>=f.size||w>=f.size { return Err("invalid quartic coordinate"); }
            let value=form.iter().rev().fold(0,|a,&b|f.add(f.mul(a,t),b));
            if f.mul(w,w)!=value { return Err("point off quotient quartic"); }
            let x=f.div(f.add(f.sub(f.sub(f.mul(t,t),self.model.a2),u),w),f.int(2));
            let result=Point::Affine{x,y:f.sub(f.mul(t,f.sub(x,u)),v)};
            if !self.contains(result) { return Err("inverse off source curve"); }
            Ok(result)
        }
    }

    #[cfg(test)]
    mod tests {
        use super::*;
        #[test]
        fn quotient_witnesses_and_projective_charts() {
            // Fixed software fixtures, with hand-counted orders; no census/minimum data.
            for (q,a2,a4,a6,order,classes) in [(5,0,1,1,9,1),(5,0,0,1,6,2),(5,0,1,0,4,4),(3,1,0,1,6,2)] {
                let ctx=Context::new(q,1,5).unwrap();
                let c=ctx.curve(ctx.integer(a2),ctx.integer(a4),ctx.integer(a6)).unwrap();
                let points=c.points(); assert_eq!(points.len(),order);
                let cosets=c.quotient_classes().unwrap(); assert_eq!(cosets.len(),classes);
                for coset in cosets { for (p,h) in coset.members { assert_eq!(c.add(coset.representative,c.add(h,h).unwrap()).unwrap(),p); } }
                for &target in points.iter().skip(1) { for &p in &points {
                    let image=c.forward(target,p).unwrap();
                    assert_eq!(c.inverse(target,image).unwrap(),p);
                    let conjugate=match image { QuarticPoint::PlusInfinity=>QuarticPoint::MinusInfinity,QuarticPoint::MinusInfinity=>QuarticPoint::PlusInfinity,QuarticPoint::Affine{t,w}=>QuarticPoint::Affine{t,w:ctx.field.neg(w)} };
                    assert_eq!(c.inverse(target,conjugate).unwrap(),c.add(target,c.negate(p).unwrap()).unwrap());
                }}
            }
        }
        #[test]
        fn constant_twist_relations_are_retained() {
            let ctx=Context::new(5,1,5).unwrap();
            let c=ctx.curve(0,ctx.integer(1),ctx.integer(1)).unwrap();
            let form=c.quotient_form(Point::Infinity).unwrap();
            let twist=form.map(|v|ctx.field.mul(ctx.integer(2),v)); // 2 nonsquare in F5
            assert_eq!(ctx.square_relations(&[form,form]).unwrap(),vec![(0,true),(3,true)]);
            assert_eq!(ctx.square_relations(&[form,twist]).unwrap(),vec![(0,true),(3,false)]);
            let classes=ctx.square_classes(&[form,twist]).unwrap();
            assert_eq!((classes.geometric_rank,classes.arithmetic_rank),(1,2));
            assert!(classes.contains_nonsquare_constant);
            assert_eq!(ctx.square_relations(&[form;7]).unwrap().len(),64);
            assert!(ctx.square_relations(&[form;8]).is_err());
            assert!(ctx.square_relations(&[[0,0,0,0,1]]).is_err());
        }
        #[test]
        fn fixed_f27_support_geometry_matches_independent_relations() {
            let ctx=Context::new(3,3,27).unwrap();
            let curve=ctx.curve(ctx.integer(1),0,ctx.integer(1)).unwrap();
            let mut generic=0usize;let mut exceptional=OrderedMap::new();
            for coset in curve.quotient_classes().unwrap() {
                let form=curve.quotient_form(coset.representative).unwrap();
                ctx.visit_structures(819,|matrix| {
                    let image=ctx.transform_form(form,matrix)?;
                    let orbit=ctx.conjugate_forms(image)?;
                    let geometry=ctx.support_geometry(&orbit)?;
                    if geometry.pairwise_disjoint {generic+=1;}
                    else {
                        let key=(geometry.geometric_rank,geometry.branch_points,geometry.geometric_genus);
                        *exceptional.entry(key).or_insert(0usize)+=1;
                        let relations=ctx.square_classes(&orbit)?;
                        assert_eq!(relations.geometric_rank,geometry.geometric_rank);
                    }
                    Ok(())
                }).unwrap();
            }
            assert_eq!(generic,1358);
            assert_eq!(exceptional,[( (1,4,1),2),((3,8,9),18),((3,9,11),52),((3,10,13),208)]
                .into_iter().collect());
        }
        #[test]
        fn support_geometry_validates_orbit_and_rank_one_n5() {
            let ctx=Context::new(3,5,243).unwrap();
            let form=[1,1,0,1,0];
            let repeated=[form;5];
            let geometry=ctx.support_geometry(&repeated).unwrap();
            assert_eq!(geometry,SupportGeometry{pairwise_disjoint:false,
                geometric_rank:1,branch_points:4,geometric_genus:1});
            let mut broken=repeated;broken[1][0]=2;
            assert!(ctx.support_geometry(&broken).is_err());
            assert!(ctx.support_geometry(&repeated[..4]).is_err());
            assert!(ctx.support_geometry(&[[0,0,1,0,1];5]).is_err());
        }
        #[test]
        fn complete_cocycle_index_replays_structure_ordinals() {
            for (q,n,k,limit) in [(3,3,1,27),(3,5,2,243)] {
                let ctx=Context::new(q,n,limit).unwrap();
                let count=ctx.structure_count().unwrap();
                if n==5 {assert_eq!(count,597861);}
                assert!(ctx.cocycle_index(k,count-1).is_err());
                let index=ctx.cocycle_index(k,count).unwrap();
                assert_eq!(index.len() as u64,count);
                assert_eq!(index.power(),k);
                for ordinal in [0,count/2,count-1] {
                    ctx.visit_structures_range(ordinal,ordinal+1,1,|matrix| {
                        let cocycle=ctx.structure_cocycle_power(matrix,k)?;
                        assert_eq!(ctx.cocycle_ordinal(&index,cocycle)?,Some(ordinal));
                        let scaled=cocycle.map(|a|ctx.field.mul(a,ctx.integer(2)));
                        assert_eq!(ctx.cocycle_ordinal(&index,scaled)?,Some(ordinal));
                        Ok(())
                    }).unwrap();
                }
                assert!(ctx.cocycle_index(0,count).is_err());
                assert!(ctx.cocycle_index(n,count).is_err());
            }
            let q3=Context::new(3,3,27).unwrap();
            let q5=Context::new(5,3,125).unwrap();
            let index=q3.cocycle_index(1,819).unwrap();
            assert!(q5.cocycle_ordinal(&index,[1,0,0,1]).is_err());
            assert!(q3.cocycle_ordinal(&index,[1,0,0,0]).is_err());
        }
        #[test]
        fn rational_image_index_matches_direct_full_f27_scan() {
            let ctx=Context::new(3,3,27).unwrap();let f=&ctx.field;
            assert!(ctx.rational_image_index(3275).is_err());
            let index=ctx.rational_image_index(3276).unwrap();
            assert_eq!(index.entries(),3276);
            assert_eq!(index.roots(),28);
            for root in [0,1,2,7,26,27] {
                let expected=ctx.rational_image_ordinals(&index,root).unwrap();
                assert_eq!(expected.len(),117);
                assert!(expected.windows(2).all(|pair|pair[0]<pair[1]));
                let mut direct=Vec::new();let mut ordinal=0;
                ctx.visit_structures(819,|matrix| {
                    let image=apply(f,&matrix,root,f.size);
                    if image==f.size || f.in_fq(image) {direct.push(ordinal);}
                    ordinal+=1;Ok(())
                }).unwrap();
                assert_eq!(expected,direct);
            }
            assert!(ctx.rational_image_ordinals(&index,28).is_err());
            let ctx5=Context::new(3,5,243).unwrap();
            let count=ctx5.structure_count().unwrap();
            let index5=ctx5.rational_image_index(count*4).unwrap();
            assert_eq!(index5.roots(),244);
            assert_eq!(index5.entries(),2391444);
            assert_eq!(ctx5.rational_image_ordinals(&index5,0).unwrap().len(),9801);
            assert!(ctx5.rational_image_ordinals(&index5,243).unwrap().len()==9801);
            assert!(ctx5.rational_image_ordinals(&index,0).is_err());
        }
        #[test]
        fn rational_pair_generator_matches_direct_full_f27_collision() {
            let ctx=Context::new(3,3,27).unwrap();let f=&ctx.field;
            let index=ctx.cocycle_index(1,819).unwrap();
            for (alpha,gamma) in [(0,1),(27,0),(2,27)] {
                assert!(ctx.rational_pair_collision_ordinals(&index,alpha,gamma,25).is_err());
                let generated=ctx.rational_pair_collision_ordinals(&index,alpha,gamma,26).unwrap();
                assert_eq!(generated.len(),26);
                let mut direct=Vec::new();let mut ordinal=0;
                ctx.visit_structures(819,|matrix| {
                    let a=apply(f,&matrix,alpha,f.size);
                    let b=apply(f,&matrix,gamma,f.size);
                    let frob_b=if b==f.size {b} else {f.frob(b)};
                    if a==frob_b {direct.push(ordinal);}
                    ordinal+=1;Ok(())
                }).unwrap();
                assert_eq!(generated,direct);
            }
            assert!(ctx.rational_pair_collision_ordinals(&index,0,0,26).is_err());
            assert!(ctx.rational_pair_collision_ordinals(&index,28,0,26).is_err());
            let ctx5=Context::new(3,5,243).unwrap();
            let index5=ctx5.cocycle_index(2,ctx5.structure_count().unwrap()).unwrap();
            let generated=ctx5.rational_pair_collision_ordinals(&index5,0,1,2420).unwrap();
            assert_eq!(generated.len(),2420);
            assert!(generated.windows(2).all(|pair|pair[0]<pair[1]));
        }
        #[test]
        fn complete_rational_root_set_matches_direct_f27_support_collision() {
            let ctx=Context::new(3,3,27).unwrap();let f=&ctx.field;
            let cocycles=[ctx.cocycle_index(1,819).unwrap()];
            let images=ctx.rational_image_index(3276).unwrap();
            let mut forms=Vec::new();
            let curve=ctx.curve(ctx.integer(1),0,ctx.integer(1)).unwrap();
            for coset in curve.quotient_classes().unwrap() {
                forms.push(curve.quotient_form(coset.representative).unwrap());
            }
            for finite_roots in [&[0,1,2][..],&[0,1,2,3][..]] {
                let mut polynomial=pz();polynomial.n=1;polynomial.c[0]=1;
                for &root in finite_roots {
                    let mut linear=pz();linear.n=2;linear.c[0]=f.neg(root);linear.c[1]=1;
                    polynomial=pmul(f,&polynomial,&linear);
                }
                let mut form=[0;5];form[..polynomial.n].copy_from_slice(&polynomial.c[..polynomial.n]);
                forms.push(form);
            }
            for form in forms {
                let roots=ctx.rational_branch_roots(form).unwrap();
                if !roots.is_empty() {
                    assert!(ctx.rational_root_collision_ordinals(form,&images,&cocycles,0).is_err());
                }
                let generated=ctx.rational_root_collision_ordinals(form,&images,&cocycles,1000).unwrap();
                let mut direct=Vec::new();let mut ordinal=0;
                ctx.visit_structures(819,|matrix| {
                    let transformed=roots.iter().map(|&root|apply(f,&matrix,root,f.size)).collect::<Vec<_>>();
                    let hit=transformed.iter().any(|&left|transformed.iter().any(|&right|
                        left==if right==f.size {right} else {f.frob(right)}));
                    if hit {direct.push(ordinal);}
                    ordinal+=1;Ok(())
                }).unwrap();
                assert_eq!(generated,direct);
            }
            assert!(ctx.rational_branch_roots([0,0,1,0,1]).is_err());
        }
        #[test]
        fn extension_encoding_and_charts() {
            // Fixed embedded curves: orders obtained from t_2=t_1^2-2q
            // and t_3=t_1^3-3qt_1, respectively. No parameter sweep.
            for (q,n,a2,a4,a6,expected) in [(3,2,1,0,1,12),(5,3,0,1,1,108)] {
                let ctx=Context::new(q,n,125).unwrap();
                let identity=ctx.identity(); let f=&ctx.field;
                let x=f.el_of[q as usize];
                let value=identity.modulus.iter().rev().fold(0,|a,&b|f.add(f.mul(a,x),f.int(b as i64)));
                assert_eq!(value,0);
                let mut indices=identity.logarithm_to_polynomial_index.clone(); indices.sort();
                assert_eq!(indices,(0..f.size).collect::<Vec<_>>());
                let c=ctx.curve(ctx.integer(a2),ctx.integer(a4),ctx.integer(a6)).unwrap();
                let points=c.points(); assert_eq!(points.len(),expected);
                let cosets=c.quotient_classes().unwrap();
                assert_eq!(cosets.iter().map(|s|s.members.len()).sum::<usize>(),expected);
                for target in cosets.iter().map(|s|s.representative).filter(|&p|p!=Point::Infinity) {
                    for &p in &points { assert_eq!(c.inverse(target,c.forward(target,p).unwrap()).unwrap(),p); }
                }
            }
        }
        #[test]
        fn structure_unranking_matches_nested_reference() {
            for (q,n) in [(3,1),(3,3),(5,3)] {
                let ctx=Context::new(q,n,125).unwrap();let f=&ctx.field;let t=trans(f);
                let mut reference=Vec::new();
                let mut emit=|a,b,c|reference.push(ctx.normalize_matrix(from_triple(f,a,b,c,t.inf)).unwrap());
                for &c in &t.rep_a1 {emit(t.inf,0,c);}
                for &b in &t.rep_a2 {for c in 0..f.size {if c!=b {emit(t.inf,b,c);}}}
                for &a in &t.rep_b {for b in 0..=f.size {if b==a {continue;}
                    for c in 0..=f.size {if c!=a && c!=b {emit(a,b,c);}}
                }}
                let count=reference.len() as u64;assert_eq!(count,ctx.structure_count().unwrap());
                // Every index includes every A1/A2/B boundary and skipped value.
                let mut actual=Vec::new();ctx.visit_structures(count,|m|{actual.push(m);Ok(())}).unwrap();
                assert_eq!(actual,reference);
                let mut joined=Vec::new();let mut start=0;
                while start<count {let end=(start+17).min(count);
                    ctx.visit_structures_range(start,end,17,|m|{joined.push(m);Ok(())}).unwrap();start=end;
                }
                assert_eq!(joined,reference);
                assert_eq!(ctx.visit_structures_range(count,count,0,|_|panic!("empty")),Ok(0));
                assert!(ctx.visit_structures_range(count,count+1,1,|_|panic!("bounds")).is_err());
                assert!(ctx.visit_structures_range(1,0,0,|_|panic!("reverse")).is_err());
            }
            // Direct suffix access in the largest prescribed field: no prefix traversal.
            let ctx=Context::new(13,3,2197).unwrap();let count=ctx.structure_count().unwrap();let mut calls=0;
            ctx.visit_structures_range(count-1,count,1,|m|{assert_eq!(ctx.normalize_matrix(m)?,m);calls+=1;Ok(())}).unwrap();
            assert_eq!(calls,1);
        }
        #[test]
        fn structure_bounds_and_exact_scalar_transport() {
            let even=Context::new(3,2,9).unwrap();
            assert!(even.structure_count().is_err());
            let ctx=Context::new(3,3,27).unwrap(); let f=&ctx.field;
            assert_eq!(ctx.structure_count().unwrap(),819);
            assert!(ctx.visit_structures(818,|_|panic!("must reject before callback")).is_err());
            let mut calls=0;
            assert_eq!(ctx.visit_structures(819,|_|{calls+=1;Err("callback stop")}),Err("callback stop"));
            assert_eq!(calls,1);
            let form=[1,1,0,1,0];
            for matrix in [[1,0,0,1],[0,1,1,0],[1,2,3,1]] {
                let det=f.sub(f.mul(matrix[0],matrix[3]),f.mul(matrix[1],matrix[2]));
                assert_ne!(det,0);
                let adj=[matrix[3],f.neg(matrix[1]),f.neg(matrix[2]),matrix[0]];
                let image=ctx.transform_form(form,matrix).unwrap();
                let restored=ctx.transform_form(image,adj).unwrap();
                assert_eq!(restored,form.map(|x|f.mul(x,f.pow(det,4))));
                let scaled=matrix.map(|x|f.mul(2,x));
                assert_eq!(ctx.transform_form(form,scaled).unwrap(),image.map(|x|f.mul(x,f.pow(2,4))));
            }
            assert!(ctx.transform_form(form,[1,1,1,1]).is_err());
            assert!(ctx.transform_form(form,[27,0,0,1]).is_err());
        }
        #[test]
        fn curve_model_normalization_and_orbits() {
            for (q,n) in [(3,1),(5,1),(3,2)] {
                let ctx=Context::new(q,n,9).unwrap(); let f=&ctx.field;
                let mut covered=BTreeSet::new();
                let count=ctx.visit_curve_classes(153,|class| {
                    for witness in class.members {
                        assert_eq!(ctx.transform_model(class.representative,witness.u,witness.r).unwrap(),witness.model);
                        assert!(covered.insert(witness.model));
                    }
                    Ok(())
                }).unwrap();
                if (q,n)==(3,1) { assert_eq!(count,8); }
                if (q,n)==(5,1) { assert_eq!(count,12); }
                for a2 in 0..f.size { for a4 in 0..f.size { for a6 in 0..f.size {
                    let Ok(source)=ctx.curve(a2,a4,a6) else { continue; };
                    let witness=ctx.normalize_model([a2,a4,a6]).unwrap();
                    assert!(covered.contains(&witness.model));
                    let target=ctx.curve(witness.model[0],witness.model[1],witness.model[2]).unwrap();
                    let images: BTreeSet<_>=source.points().iter().map(|&point| match point {
                        Point::Infinity=>point,
                        Point::Affine{x,y}=>Point::Affine{x:f.div(f.sub(x,witness.r),f.pow(witness.u,2)),y:f.div(y,f.pow(witness.u,3))},
                    }).collect();
                    assert_eq!(images,target.points().into_iter().collect());
                } } }
                assert!(ctx.visit_curve_classes(ctx.curve_model_domain_size()-1,|_|panic!("cap before callback")).is_err());
                let mut calls=0;
                assert_eq!(ctx.visit_curve_classes(153,|_|{calls+=1;Err("stop classes")}),Err("stop classes"));
                assert_eq!(calls,1);
                assert!(ctx.transform_model([0,1,1],0,0).is_err());
                assert!(ctx.transform_model([0,1,1],1,f.size).is_err());
                assert!(ctx.normalize_model([0,0,0]).is_err());
            }
        }
        #[test]
        fn rejects_invalid_domains() {
            assert!(Context::new(9,1,9).is_err());
            assert!(Context::new(5,3,124).is_err());
            let ctx=Context::new(5,1,5).unwrap();
            assert!(ctx.curve(0,0,0).is_err());
            assert!(ctx.curve(5,0,1).is_err());
        }
    }
}
pub use implementation::{Context,Curve,Point,QuarticPoint,Coset,FieldIdentity,SquareClasses,SupportGeometry,CocycleIndex,RationalImageIndex,CurveClass,ModelWitness};
