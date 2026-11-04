//! Fixed F27 software certificate for the complete K-rational-root contribution.
//! This is not a scientific census launcher or a degree-2/3/4 generator.
#[path="quotient_core.rs"] mod quotient_core;
use quotient_core::Context;

fn numbers(values:impl IntoIterator<Item=String>)->String {
    format!("[{}]",values.into_iter().collect::<Vec<_>>().join(","))
}
fn main() {
    if std::env::args().len()!=1 {
        eprintln!("fixed F27 software certificate takes no arguments");
        std::process::exit(2);
    }
    let ctx=Context::new(3,3,27).unwrap();
    let curve=ctx.curve(ctx.integer(1),0,ctx.integer(1)).unwrap();
    let structures=ctx.structure_count().unwrap();
    let cocycles=[ctx.cocycle_index(1,structures).unwrap()];
    let images=ctx.rational_image_index(structures*4).unwrap();
    let mut rows=Vec::new();
    for (coset_index,coset) in curve.quotient_classes().unwrap().iter().enumerate() {
        let form=curve.quotient_form(coset.representative).unwrap();
        let roots=ctx.rational_branch_roots(form).unwrap();
        let indices=ctx.rational_root_collision_ordinals(form,&images,&cocycles,10_000).unwrap();
        let encoded_form=numbers(form.iter().map(|&v|ctx.encoding()[v as usize].to_string()));
        let encoded_roots=numbers(roots.iter().map(|&v|
            if v==ctx.size() {v.to_string()} else {ctx.encoding()[v as usize].to_string()}));
        rows.push(format!("{{\"coset_index\":{},\"form\":{},\"rational_roots\":{},\"structure_indices\":{}}}",
            coset_index,encoded_form,encoded_roots,numbers(indices.iter().map(|v|v.to_string()))));
    }
    println!("{{\"schema\":\"pext.rational-collision-software/v1\",\"fixture\":\"f27-char3\",\"structures\":{},\"cocycle_entries\":{},\"rational_image_entries\":{},\"rows\":{}}}",
        structures,cocycles[0].len(),images.entries(),numbers(rows));
}
