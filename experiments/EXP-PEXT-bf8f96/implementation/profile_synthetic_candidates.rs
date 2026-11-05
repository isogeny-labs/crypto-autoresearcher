//! Bounded design-only q11/n3 software profile; no elliptic cohort input.
#[path="quotient_core.rs"] mod quotient_core;
use quotient_core::Context;
use std::time::Instant;

fn main() {
    if std::env::args().len()!=1 {
        eprintln!("fixed synthetic profile takes no arguments");
        std::process::exit(2);
    }
    let started=Instant::now();
    let ctx=Context::new(11,3,1331).unwrap();
    let field_seconds=started.elapsed().as_secs_f64();
    let structures=ctx.structure_count().unwrap();
    assert_eq!(structures,1_786_323);
    let cocycle=ctx.cocycle_index(1,structures).unwrap();
    let cocycle_seconds=started.elapsed().as_secs_f64()-field_seconds;
    let images=ctx.rational_image_index(21_435_876).unwrap();
    let image_seconds=started.elapsed().as_secs_f64()-field_seconds-cocycle_seconds;
    // Three algebraic stress patterns over F11, embedded into K=F_(11^3).
    // Quadratics x^2+1 and x^2+3 stay irreducible in the odd cubic extension.
    let fixtures=[
        ("split-1111",[0,ctx.integer(5),0,ctx.integer(5),1],vec![1,1,1,1]),
        ("split-112",[0,ctx.integer(-1),1,ctx.integer(-1),1],vec![1,1,2]),
        ("split-22",[ctx.integer(3),0,ctx.integer(4),0,1],vec![2,2]),
    ];
    let mut rows=Vec::new();
    for (label,form,pattern) in fixtures {
        assert_eq!(ctx.factor_branch_form(form).unwrap().pattern(),pattern);
        let before=Instant::now();
        let checked=ctx.checked_exceptional_candidates(form,&images,std::slice::from_ref(&cocycle),
            80_332,21_312,80_332).unwrap();
        let generic=checked.generic_intervals.iter().map(|(start,end)|end-start).sum::<u64>();
        assert_eq!(generic+checked.exceptional.len() as u64,structures);
        rows.push(format!("{{\"label\":\"{}\",\"rational_candidates\":{},\"nonrational_candidates\":{},\"duplicate_candidates\":{},\"exceptional\":{},\"generic_intervals\":{},\"generic_positions\":{},\"candidate_seconds\":{:.6}}}",
            label,checked.rational_count,checked.nonrational_count,
            checked.duplicate_count,checked.exceptional.len(),checked.generic_intervals.len(),
            generic,before.elapsed().as_secs_f64()));
    }
    println!("{{\"schema\":\"pext.synthetic-candidate-profile/v1\",\"q\":11,\"n\":3,\"synthetic\":true,\"structures\":{},\"cocycle_entries\":{},\"rational_image_entries\":{},\"field_seconds\":{:.6},\"cocycle_seconds\":{:.6},\"image_seconds\":{:.6},\"total_seconds\":{:.6},\"rows\":[{}]}}",
        structures,structures,images.entries(),field_seconds,cocycle_seconds,
        image_seconds,started.elapsed().as_secs_f64(),rows.join(","));
}
