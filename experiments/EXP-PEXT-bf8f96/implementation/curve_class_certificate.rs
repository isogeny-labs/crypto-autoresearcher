//! Named curve-class software fixtures; no cover/genus census entrypoint.
#[path="quotient_core.rs"] mod quotient_core;
use quotient_core::Context;
fn array(items:impl IntoIterator<Item=String>)->String { format!("[{}]",items.into_iter().collect::<Vec<_>>().join(",")) }
fn nums(a:&[u32])->String { array(a.iter().map(|v|v.to_string())) }
fn main() {
    let args:Vec<_>=std::env::args().collect();
    let (q,n)=match args.get(1).map(String::as_str) {
        Some("f3-classes") if args.len()==2=>(3,1),
        Some("f5-classes") if args.len()==2=>(5,1),
        Some("f9-classes") if args.len()==2=>(3,2),
        _=>{eprintln!("required software fixture f3-classes|f5-classes|f9-classes");std::process::exit(2)}
    };
    let ctx=Context::new(q,n,9).unwrap(); let id=ctx.identity();
    let field=format!("{{\"prime\":{},\"degree\":{},\"modulus\":{},\"primitive_polynomial_index\":{},\"logarithm_to_polynomial_index\":{}}}",id.prime,id.degree,nums(&id.modulus),id.primitive_polynomial_index,nums(&id.logarithm_to_polynomial_index));
    let encode=|a:&[u32]|nums(&a.iter().map(|&x|ctx.encoding()[x as usize]).collect::<Vec<_>>());
    let mut rows=Vec::new();
    let count=ctx.visit_curve_classes(153,|class| {
        let members=array(class.members.iter().map(|w|format!("{{\"model\":{},\"u\":{},\"r\":{}}}",encode(&w.model),ctx.encoding()[w.u as usize],ctx.encoding()[w.r as usize])));
        rows.push(format!("{{\"representative\":{},\"members\":{}}}",encode(&class.representative),members));Ok(())
    }).unwrap();
    println!("{{\"schema\":\"pext.curve-class-certificate/v1\",\"field\":{},\"candidate_models\":{},\"class_count\":{},\"classes\":{}}}",field,ctx.curve_model_domain_size(),count,array(rows));
}
