//! Bounded per-form checked candidate unit. The cohort/T wrapper binds the form.
#[path="quotient_core.rs"] mod quotient_core;
use quotient_core::Context;

fn numbers(values:impl IntoIterator<Item=String>)->String {
    format!("[{}]",values.into_iter().collect::<Vec<_>>().join(","))
}
fn parse_u32(raw:&str)->Result<u32,String> {
    raw.parse().map_err(|_|format!("invalid unsigned integer: {raw}"))
}
fn parse_u64(raw:&str)->Result<u64,String> {
    raw.parse().map_err(|_|format!("invalid unsigned integer: {raw}"))
}
fn run()->Result<(),String> {
    let args=std::env::args().collect::<Vec<_>>();
    if args.len()!=10 {
        return Err("usage: candidate_unit q n basis_form_csv max_field_elements max_structures max_image_entries max_rational_candidates max_nonrational_maps max_total_candidates".into());
    }
    let q=parse_u32(&args[1])?;let n=parse_u32(&args[2])?;
    if ![3,5,7].contains(&n) {return Err("candidate unit requires n=3,5,7".into());}
    let ctx=Context::new(q,n,parse_u32(&args[4])?).map_err(str::to_string)?;
    let encoded=args[3].split(',').map(parse_u32).collect::<Result<Vec<_>,_>>()?;
    if encoded.len()!=5 || encoded.iter().any(|&value|value>=ctx.size()) {
        return Err("basis form requires five coefficients in the pinned field".into());
    }
    let mut inverse=vec![0;ctx.size() as usize];
    for (label,&basis) in ctx.encoding().iter().enumerate() {inverse[basis as usize]=label as u32;}
    let mut form=[0;5];
    for (index,&basis) in encoded.iter().enumerate() {form[index]=inverse[basis as usize];}
    let branch=ctx.branch_roots(form).map_err(str::to_string)?;
    let pattern=numbers(branch.factorization.pattern().iter().map(ToString::to_string));
    let factors=numbers(branch.factorization.finite_factors.iter().map(|factor|
        numbers(factor.iter().map(|&value|ctx.encoding()[value as usize].to_string()))));
    let extension_modulus=branch.extension.as_ref().map_or_else(||"null".to_string(),|extension|
        numbers(extension.modulus().iter().map(|&value|ctx.encoding()[value as usize].to_string())));
    let root_degree=branch.extension.as_ref().map_or(1,|extension|extension.degree());
    let roots=numbers(branch.finite_roots.iter().map(|root|
        numbers(root.coefficients()[..root_degree].iter().map(|&value|ctx.encoding()[value as usize].to_string()))));
    let max_structures=parse_u64(&args[5])?;
    let mut indices=(1..=(n-1)/2).map(|power|ctx.cocycle_index(power,max_structures))
        .collect::<Result<Vec<_>,_>>().map_err(str::to_string)?;
    let mut images=ctx.rational_image_index(parse_u64(&args[6])?).map_err(str::to_string)?;
    let checked=ctx.checked_exceptional_candidates(form,&images,&indices,
        parse_u64(&args[7])?,parse_u64(&args[8])?,parse_u64(&args[9])?)
        .map_err(str::to_string)?;
    for index in &mut indices {
        ctx.rebuild_cocycle_index_reverse(index,max_structures).map_err(str::to_string)?;
        index.reverse_representatives();
    }
    images.reverse_buckets();
    let reversed=ctx.checked_exceptional_candidates_reversed_roots(form,&images,&indices,
        parse_u64(&args[7])?,parse_u64(&args[8])?,parse_u64(&args[9])?)
        .map_err(str::to_string)?;
    if checked!=reversed {return Err("C3 reversed candidate enumeration differs".into());}
    let identity=ctx.identity();
    let field=format!("{{\"prime\":{},\"degree\":{},\"modulus\":{},\"primitive_polynomial_index\":{},\"logarithm_to_polynomial_index\":{}}}",
        identity.prime,identity.degree,
        numbers(identity.modulus.iter().map(ToString::to_string)),
        identity.primitive_polynomial_index,
        numbers(identity.logarithm_to_polynomial_index.iter().map(ToString::to_string)));
    let rows=checked.exceptional.iter().map(|(ordinal,geometry)| {
        let matrix=ctx.structure_matrix(&indices[0],*ordinal).map_err(str::to_string)?;
        Ok(format!("[{},[{},{},{},{}],{},{},{}]",ordinal,
            ctx.encoding()[matrix[0] as usize],ctx.encoding()[matrix[1] as usize],
            ctx.encoding()[matrix[2] as usize],ctx.encoding()[matrix[3] as usize],
            geometry.geometric_rank,geometry.branch_points,geometry.geometric_genus))
    }).collect::<Result<Vec<String>,String>>()?;
    let intervals=numbers(checked.generic_intervals.iter().map(|(start,end)|format!("[{start},{end}]")));
    println!("{{\"schema\":\"pext.checked-candidate-unit/v1\",\"structure_order\":\"left-pgl2-fq/v1\",\"candidate_order_aa\":\"reverse-cocycle-build-representatives-buckets-and-roots/v1\",\"field\":{},\"form\":{},\"factor_pattern\":{},\"infinity\":{},\"factors\":{},\"extension_modulus\":{},\"roots\":{},\"structures\":{},\"cocycle_entries\":{},\"rational_image_entries\":{},\"rational_count\":{},\"nonrational_count\":{},\"duplicate_count\":{},\"exceptional\":{},\"generic\":{},\"rows\":{},\"generic_intervals\":{}}}",
        field,numbers(encoded.iter().map(ToString::to_string)),pattern,branch.factorization.infinity,
        factors,extension_modulus,roots,checked.structures,
        numbers(indices.iter().map(|index|index.len().to_string())),images.entries(),
        checked.rational_count,checked.nonrational_count,checked.duplicate_count,
        checked.exceptional.len(),checked.structures-checked.exceptional.len() as u64,
        numbers(rows),intervals);
    Ok(())
}
fn main() {
    if let Err(error)=run() {eprintln!("{error}");std::process::exit(2);}
}
