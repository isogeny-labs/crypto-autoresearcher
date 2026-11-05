//! Fixed F27 software certificate for all five squarefree branch patterns.
//! This is not a scientific cohort launcher.
#[path="quotient_core.rs"] mod quotient_core;
use quotient_core::Context;

fn array(values:impl IntoIterator<Item=String>)->String {
    format!("[{}]",values.into_iter().collect::<Vec<_>>().join(","))
}
fn numbers(values:impl IntoIterator<Item=u32>)->String {
    array(values.into_iter().map(|value|value.to_string()))
}
fn ordinals(values:&[u64])->String {
    array(values.iter().map(ToString::to_string))
}
fn cross_ratio_orbit(label:&str)->&'static str {
    // Fixed fixture values; the separate polynomial-basis checker recomputes
    // all 24 orderings from the certified roots rather than trusting these.
    match label {
        "split-1111" => "[[10],[14],[17],[18],[23],[26]]",
        "split-112" => "[[0,1],[0,2],[1,1],[1,2],[2,1],[2,2]]",
        "split-13" => "[[2,14,14],[2,14,25],[2,25,14],[2,25,25],[13,0,25],[24,0,14]]",
        "split-22" => "[[3,0],[7,0],[9,0],[12,0],[19,0],[25,0]]",
        "irreducible-4" => "[[2,0,0,0]]",
        _ => "null",
    }
}
fn main() {
    if std::env::args().len()!=1 {
        eprintln!("fixed F27 all-degree software certificate takes no arguments");
        std::process::exit(2);
    }
    let ctx=Context::new(3,3,27).unwrap();
    let encoding=ctx.encoding();
    let mut inverse=vec![0;27];
    for (label,&basis) in encoding.iter().enumerate() {inverse[basis as usize]=label as u32;}
    let fixtures=[
        ("split-1111",[0,3,2,6,1]),
        ("split-112",[0,2,1,2,1]),
        ("split-13",[0,9,2,0,1]),
        ("split-22",[6,0,7,0,1]),
        ("irreducible-4",[2,1,0,0,1]),
    ];
    let curve=ctx.curve(ctx.integer(1),0,ctx.integer(1)).unwrap();
    let mut forms=fixtures.into_iter().map(|(label,form)|(label.to_string(),form))
        .collect::<Vec<_>>();
    for (index,coset) in curve.quotient_classes().unwrap().iter().enumerate() {
        let form=curve.quotient_form(coset.representative).unwrap();
        forms.push((format!("actual-{index}"),form.map(|value|encoding[value as usize])));
    }
    let structures=ctx.structure_count().unwrap();
    let cocycles=[ctx.cocycle_index(1,structures).unwrap()];
    let images=ctx.rational_image_index(structures*4).unwrap();
    let mut rows=Vec::new();
    for (label,basis_form) in forms {
        let form=basis_form.map(|value|inverse[value as usize]);
        let roots=ctx.branch_roots(form).unwrap();
        let rational=ctx.rational_root_collision_ordinals(form,&images,&cocycles,10_000).unwrap();
        let nonrational=ctx.nonrational_root_collision_ordinals(form,&cocycles,10_000).unwrap();
        let mut union=rational.clone();union.extend_from_slice(&nonrational);
        union.sort_unstable();union.dedup();
        let factors=array(roots.factorization.finite_factors.iter().map(|factor|
            numbers(factor.iter().map(|&value|encoding[value as usize]))));
        let extension=roots.extension.as_ref().map(|value|value.modulus());
        let extension_degree=extension.as_ref().map_or(1,|modulus|modulus.len()-1);
        let modulus=extension.map_or_else(||"null".to_string(),|modulus|
            numbers(modulus.into_iter().map(|value|encoding[value as usize])));
        let root_values=array(roots.finite_roots.iter().map(|root|
            numbers(root.coefficients()[..extension_degree].iter().map(|&value|encoding[value as usize]))));
        rows.push(format!("{{\"label\":\"{label}\",\"form\":{},\"pattern\":{},\"infinity\":{},\"factors\":{},\"extension_modulus\":{},\"roots\":{},\"cross_ratio_orbit\":{},\"rational_indices\":{},\"nonrational_indices\":{},\"union_indices\":{}}}",
            numbers(basis_form),numbers(roots.factorization.pattern().into_iter().map(|value|value as u32)),
            roots.factorization.infinity,factors,modulus,root_values,cross_ratio_orbit(&label),
            ordinals(&rational),ordinals(&nonrational),ordinals(&union)));
    }
    println!("{{\"schema\":\"pext.all-degree-collision-software/v1\",\"fixture\":\"f27-char3\",\"structures\":{},\"cocycle_entries\":{},\"rational_image_entries\":{},\"rows\":{}}}",
        structures,cocycles[0].len(),images.entries(),array(rows));
}
