//! Fixed group/coordinate software fixtures, never a scientific curve census.
#[path="quotient_core.rs"] mod quotient_core;
use quotient_core::Context;
fn array(items:impl IntoIterator<Item=String>)->String { format!("[{}]",items.into_iter().collect::<Vec<_>>().join(",")) }
fn nums(a:&[u32])->String { array(a.iter().map(|x|x.to_string())) }
fn main() {
    let args:Vec<_>=std::env::args().collect();
    let n=match args.get(1).map(String::as_str) {
        Some("f3-identity") if args.len()==2=>1,
        Some("f27-structures") if args.len()==2=>3,
        _=>{eprintln!("required software fixture f3-identity|f27-structures");std::process::exit(2)}
    };
    let ctx=Context::new(3,n,27).unwrap(); let id=ctx.identity();
    let field=format!("{{\"prime\":{},\"degree\":{},\"modulus\":{},\"primitive_polynomial_index\":{},\"logarithm_to_polynomial_index\":{}}}",id.prime,id.degree,nums(&id.modulus),id.primitive_polynomial_index,nums(&id.logarithm_to_polynomial_index));
    let forms=[[1,1,0,1,0],[2,2,0,2,0]].map(|a|a.map(|x|ctx.integer(x)));
    let encode=|a:&[u32]|nums(&a.iter().map(|&x|ctx.encoding()[x as usize]).collect::<Vec<_>>());
    let mut rows=Vec::new();
    let count=ctx.visit_structures(819,|matrix| {
        let cocycle=ctx.structure_cocycle(matrix)?;
        let transformed=forms.iter().map(|&form|ctx.transform_form(form,matrix).map(|a|encode(&a))).collect::<Result<Vec<_>,_>>()?;
        rows.push(format!("{{\"matrix\":{},\"cocycle\":{},\"transformed_forms\":{}}}",encode(&matrix),encode(&cocycle),array(transformed)));
        Ok(())
    }).unwrap();
    println!("{{\"schema\":\"pext.structure-certificate/v1\",\"field\":{},\"forms\":{},\"count\":{},\"structures\":{}}}",field,array(forms.iter().map(|a|encode(a))),count,array(rows));
}
