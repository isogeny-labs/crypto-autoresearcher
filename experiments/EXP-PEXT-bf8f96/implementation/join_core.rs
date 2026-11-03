//! Streaming supplied-model x canonical-T-class x projective-structure join.
//! The caller must bind the supplied ordered models to verified cohort bytes.
use crate::quotient_core::{Context,Point};
use std::collections::BTreeSet;

#[derive(Debug)]
pub struct PlannedClass {
    pub model:[u32;3],
    pub targets:Vec<Point>,
    pub offset:u64,
}
pub struct JoinPlan<'a> {
    context:&'a Context,
    classes:Vec<PlannedClass>,
    structures:u64,
    total:u64,
}
#[derive(Debug,PartialEq,Eq)]
pub struct JoinedRow {
    pub ordinal:u64,
    pub class_index:usize,
    pub coset_index:usize,
    pub structure_index:u64,
    pub model:[u32;3],
    pub target:Point,
    pub matrix:[u32;4],
    pub cocycle:[u32;4],
    pub original_form:[u32;5],
    pub transformed_form:[u32;5],
    pub conjugates:Vec<[u32;5]>,
}
impl<'a> JoinPlan<'a> {
    /// Construct the exact plan for this supplied ordered model slice. No
    /// assertion of cohort completeness is made by this arithmetic layer.
    pub fn new(context:&'a Context,models:&[[u32;3]],maximum_models:usize)->Result<Self,&'static str> {
        if models.is_empty() || models.len()>maximum_models { return Err("join model count limit"); }
        let structures=context.structure_count()?;
        let mut seen=BTreeSet::new();
        // Validate the whole slice before constructing point/coset sets.
        for &model in models {
            if !seen.insert(model) { return Err("duplicate join model"); }
            context.curve(model[0],model[1],model[2])?;
        }
        let mut classes=Vec::new();let mut total=0u64;
        for &model in models {
            let curve=context.curve(model[0],model[1],model[2])?;
            let targets=curve.quotient_classes()?.iter().map(|c|c.representative).collect::<Vec<_>>();
            let rows=structures.checked_mul(targets.len() as u64).ok_or("join row count overflow")?;
            let offset=total;total=total.checked_add(rows).ok_or("join row count overflow")?;
            classes.push(PlannedClass{model,targets,offset});
        }
        Ok(Self{context,classes,structures,total})
    }
    pub fn classes(&self)->&[PlannedClass] { &self.classes }
    pub fn structures(&self)->u64 { self.structures }
    pub fn total(&self)->u64 { self.total }
    /// Exact half-open ordinal interval. Empty intervals are valid; caps,
    /// invalid bounds and callback errors never silently truncate a shard.
    pub fn visit_range<F>(&self,start:u64,end:u64,maximum_emitted:u64,mut body:F)->Result<u64,&'static str>
    where F:FnMut(JoinedRow)->Result<(),&'static str> {
        if start>end || end>self.total { return Err("invalid join range"); }
        if end-start>maximum_emitted { return Err("join emission limit exceeded"); }
        if start==end { return Ok(0); }
        let mut emitted=0u64;
        for (class_index,class) in self.classes.iter().enumerate() {
            let class_end=class.offset+(class.targets.len() as u64)*self.structures;
            if class_end<=start {continue;} if class.offset>=end {break;}
            let curve=self.context.curve(class.model[0],class.model[1],class.model[2])?;
            for (coset_index,&target) in class.targets.iter().enumerate() {
                let offset=class.offset+(coset_index as u64)*self.structures;
                let lo=start.max(offset);let hi=end.min(offset+self.structures);
                if lo>=hi {continue;}
                let original_form=curve.quotient_form(target)?;
                let mut ordinal=lo;
                self.context.visit_structures_range(lo-offset,hi-offset,hi-lo,|matrix| {
                    let transformed_form=self.context.transform_form(original_form,matrix)?;
                    let row=JoinedRow{ordinal,class_index,coset_index,structure_index:ordinal-offset,
                        model:class.model,target,matrix,cocycle:self.context.structure_cocycle(matrix)?,
                        original_form,transformed_form,conjugates:self.context.conjugate_forms(transformed_form)?};
                    body(row)?;ordinal+=1;emitted+=1;Ok(())
                })?;
                if ordinal!=hi {return Err("join shard cardinality mismatch");}
            }
        }
        if emitted!=end-start {return Err("join coverage mismatch");} Ok(emitted)
    }
}
