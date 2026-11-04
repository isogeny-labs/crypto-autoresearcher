//! Deterministic prescribed input-cohort preparation, no scientific cover metrics.
#[path="quotient_core.rs"] mod quotient_core;
use quotient_core::Context;
fn array(items:impl IntoIterator<Item=String>)->String { format!("[{}]",items.into_iter().collect::<Vec<_>>().join(",")) }
fn nums(a:&[u32])->String { array(a.iter().map(|v|v.to_string())) }
fn main() {
    let args:Vec<_>=std::env::args().collect();
    let name=args.get(1).map(String::as_str).unwrap_or("");
    let (q,n)=match name {
        "f3-control"=>(3,1),"f5-control"=>(5,1),"f9-control"=>(3,2),
        "q3-n5"=>(3,5),"q5-n3"=>(5,3),"q7-n3"=>(7,3),"q11-n3"=>(11,3),"q13-n3-descriptive"=>(13,3),
        _=>{eprintln!("requires a named prescribed input cohort or software control");std::process::exit(2)}
    };
    if !(args.len()==2 || (args.len()==3 && args[2]=="--field-only")) { eprintln!("named cohort and optional --field-only required");std::process::exit(2); }
    let ctx=Context::new(q,n,2197).unwrap();let id=ctx.identity();
    let field=format!("{{\"prime\":{},\"degree\":{},\"modulus\":{},\"primitive_polynomial_index\":{},\"logarithm_to_polynomial_index\":{}}}",id.prime,id.degree,nums(&id.modulus),id.primitive_polynomial_index,nums(&id.logarithm_to_polynomial_index));
    if args.len()==3 { println!("{}",field);return; }
    let mut reps=Vec::new();let mut covered=0usize;
    let count=ctx.visit_curve_classes(10_000_000,|class| {
        covered+=class.members.len();reps.push(nums(&class.representative.map(|x|ctx.encoding()[x as usize])));Ok(())
    }).unwrap();
    println!("{{\"schema\":\"pext.compact-class-inputs/v1\",\"cohort\":\"{}\",\"field\":{},\"candidate_models\":{},\"normalized_models\":{},\"class_count\":{},\"representatives\":{}}}",name,field,ctx.curve_model_domain_size(),covered,count,array(reps));
}
