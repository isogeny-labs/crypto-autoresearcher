//! Fixed software-control join certificates; no prescribed scientific cohort CLI.
#[path="quotient_core.rs"] mod quotient_core;
#[path="join_core.rs"] mod join_core;
use quotient_core::{Context,Point};
use join_core::JoinPlan;
fn array(a:impl IntoIterator<Item=String>)->String {format!("[{}]",a.into_iter().collect::<Vec<_>>().join(","))}
fn nums(a:&[u32])->String {array(a.iter().map(|x|x.to_string()))}
fn main() {
 let args:Vec<_>=std::env::args().collect();
 let (q,n)=match args.get(1).map(String::as_str) {
  Some("f3-classes")=>(3,1),Some("f5-classes")=>(5,1),Some("f27-char3")=>(3,3),
  _=>{eprintln!("fixed software fixture required");std::process::exit(2)}
 };
 if args.len()!=2 && args.len()!=4 {eprintln!("fixture [start end]");std::process::exit(2)}
 let ctx=Context::new(q,n,27).unwrap();let mut models=Vec::new();
 if n==1 {ctx.visit_curve_classes(50,|c|{models.push(c.representative);Ok(())}).unwrap();}
 else {models.push([ctx.integer(1),0,ctx.integer(1)]);}
 let plan=JoinPlan::new(&ctx,&models,12).unwrap();
 let range=if args.len()==4 {match (args[2].parse::<u64>(),args[3].parse::<u64>()) {
  (Ok(a),Ok(b))=>(a,b),_=>{eprintln!("invalid integer range");std::process::exit(2)}
 }} else {(0,plan.total())};
 let id=ctx.identity();let field=format!("{{\"prime\":{},\"degree\":{},\"modulus\":{},\"primitive_polynomial_index\":{},\"logarithm_to_polynomial_index\":{}}}",id.prime,id.degree,nums(&id.modulus),id.primitive_polynomial_index,nums(&id.logarithm_to_polynomial_index));
 let encode=|a:&[u32]|nums(&a.iter().map(|&x|ctx.encoding()[x as usize]).collect::<Vec<_>>());
 let point=|p:Point|match p {Point::Infinity=>"null".into(),Point::Affine{x,y}=>encode(&[x,y])};
 let classes=array(plan.classes().iter().map(|c|format!("{{\"model\":{},\"targets\":{},\"offset\":{}}}",encode(&c.model),array(c.targets.iter().map(|&p|point(p))),c.offset)));
 let mut rows=Vec::new();
 if let Err(e)=plan.visit_range(range.0,range.1,10000,|r| {
  rows.push(format!("{{\"ordinal\":{},\"class_index\":{},\"coset_index\":{},\"structure_index\":{},\"model\":{},\"target\":{},\"matrix\":{},\"cocycle\":{},\"original_form\":{},\"transformed_form\":{},\"conjugates\":{}}}",r.ordinal,r.class_index,r.coset_index,r.structure_index,encode(&r.model),point(r.target),encode(&r.matrix),encode(&r.cocycle),encode(&r.original_form),encode(&r.transformed_form),array(r.conjugates.iter().map(|x|encode(x)))));Ok(())
 }) {eprintln!("{}",e);std::process::exit(2)}
 println!("{{\"schema\":\"pext.join-software-certificate/v1\",\"fixture\":\"{}\",\"order\":\"log-point-coset-transversal/v1\",\"field\":{},\"classes\":{},\"structures\":{},\"total\":{},\"start\":{},\"end\":{},\"rows\":{}}}",args[1],field,classes,plan.structures(),plan.total(),range.0,range.1,array(rows));
}

#[cfg(test)]
mod tests {
 use super::*;
 #[test]
 fn exact_ranges_and_rejection() {
  let ctx=Context::new(3,3,27).unwrap();let model=[ctx.integer(1),0,ctx.integer(1)];
  let plan=JoinPlan::new(&ctx,&[model],1).unwrap();let mut full=Vec::new();
  plan.visit_range(0,plan.total(),plan.total(),|r|{full.push(r);Ok(())}).unwrap();
  let mut combined=Vec::new();let mut start=0;
  while start<plan.total() {let end=(start+113).min(plan.total());
   plan.visit_range(start,end,113,|r|{combined.push(r);Ok(())}).unwrap();start=end;
  }
  assert_eq!(combined,full);
  assert_eq!(plan.visit_range(plan.total(),plan.total(),0,|_|panic!("empty")),Ok(0));
  assert!(plan.visit_range(0,plan.total(),plan.total()-1,|_|panic!("cap")).is_err());
  assert!(plan.visit_range(1,0,0,|_|panic!("reverse")).is_err());
  assert!(plan.visit_range(0,plan.total()+1,plan.total()+1,|_|panic!("bounds")).is_err());
  let mut calls=0;assert_eq!(plan.visit_range(0,plan.total(),plan.total(),|_|{calls+=1;Err("stop")}),Err("stop"));assert_eq!(calls,1);
  assert!(JoinPlan::new(&ctx,&[model,model],2).is_err());
  assert!(JoinPlan::new(&ctx,&[model],0).is_err());assert!(JoinPlan::new(&ctx,&[],1).is_err());
  assert!(JoinPlan::new(&ctx,&[[0,0,0]],1).is_err());
  assert!(JoinPlan::new(&ctx,&[[ctx.size(),0,1]],1).is_err());
  let even=Context::new(3,2,9).unwrap();assert!(JoinPlan::new(&even,&[model],1).is_err());
 }
 #[test]
 fn exact_support_partition_and_shard_replay() {
  let ctx=Context::new(3,3,27).unwrap();let model=[ctx.integer(1),0,ctx.integer(1)];
  let plan=JoinPlan::new(&ctx,&[model],1).unwrap();
  let mut full=Vec::new();
  let summary=plan.visit_support_range(0,plan.total(),plan.total(),|row|{
   assert!(!row.geometry.pairwise_disjoint);
   assert_eq!(row.geometry.geometric_rank,ctx.square_classes(&row.joined.conjugates)?.geometric_rank);
   full.push((row.joined.ordinal,row.geometry.geometric_genus));Ok(())
  }).unwrap();
  assert_eq!((summary.visited,summary.generic_disjoint,summary.exceptional),(1638,1358,280));
  assert_eq!(full.len(),280);
  assert!(full.windows(2).all(|pair|pair[0].0<pair[1].0));
  let mut replay=Vec::new();let mut covered=0;let mut start=0;
  while start<plan.total() {let end=(start+113).min(plan.total());
   let part=plan.visit_support_range(start,end,113,|row|{
    replay.push((row.joined.ordinal,row.geometry.geometric_genus));Ok(())
   }).unwrap();
   assert_eq!(part.visited,end-start);covered+=part.visited;start=end;
  }
  assert_eq!(covered,plan.total());assert_eq!(replay,full);
  assert_eq!(plan.visit_support_range(plan.total(),plan.total(),0,|_|panic!("empty")),
   Ok(join_core::SupportSummary{visited:0,generic_disjoint:0,exceptional:0}));
  assert!(plan.visit_support_range(0,plan.total(),plan.total()-1,|_|panic!("cap")).is_err());
  assert!(plan.visit_support_range(1,0,0,|_|panic!("reverse")).is_err());
  assert!(plan.visit_support_range(0,plan.total()+1,plan.total()+1,|_|panic!("bounds")).is_err());
 }
}
