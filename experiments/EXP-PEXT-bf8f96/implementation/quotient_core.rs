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
        fn rejects_invalid_domains() {
            assert!(Context::new(9,1,9).is_err());
            assert!(Context::new(5,3,124).is_err());
            let ctx=Context::new(5,1,5).unwrap();
            assert!(ctx.curve(0,0,0).is_err());
            assert!(ctx.curve(5,0,1).is_err());
        }
    }
}
pub use implementation::{Context,Curve,Point,QuarticPoint,Coset,FieldIdentity,SquareClasses};
