//! Bounded checked candidate units. The cohort/T wrapper binds each form.
#[path="quotient_core.rs"] mod quotient_core;
use quotient_core::{Context,CocycleIndex,RationalImageIndex};
use std::io::{self,Read,Write};

fn numbers(values:impl IntoIterator<Item=String>)->String {
    format!("[{}]",values.into_iter().collect::<Vec<_>>().join(","))
}
fn parse_u32(raw:&str)->Result<u32,String> {
    raw.parse().map_err(|_|format!("invalid unsigned integer: {raw}"))
}
fn parse_u64(raw:&str)->Result<u64,String> {
    raw.parse().map_err(|_|format!("invalid unsigned integer: {raw}"))
}
fn field_json(ctx:&Context)->String {
    let identity=ctx.identity();
    format!("{{\"prime\":{},\"degree\":{},\"modulus\":{},\"primitive_polynomial_index\":{},\"logarithm_to_polynomial_index\":{}}}",
        identity.prime,identity.degree,
        numbers(identity.modulus.iter().map(ToString::to_string)),
        identity.primitive_polynomial_index,
        numbers(identity.logarithm_to_polynomial_index.iter().map(ToString::to_string)))
}
struct CandidateEngine {
    ctx:Context,
    indices:Vec<CocycleIndex>,
    images:RationalImageIndex,
    inverse:Vec<u32>,
    max_rational:u64,
    max_nonrational:u64,
    max_total:u64,
}
impl CandidateEngine {
    fn new(q:u32,n:u32,limits:[u64;6])->Result<Self,String> {
        if ![3,5,7].contains(&n) {return Err("candidate unit requires n=3,5,7".into());}
        let max_field=u32::try_from(limits[0]).map_err(|_|"field element limit exceeds u32")?;
        let ctx=Context::new(q,n,max_field).map_err(str::to_string)?;
        let mut inverse=vec![0;ctx.size() as usize];
        for (label,&basis) in ctx.encoding().iter().enumerate() {inverse[basis as usize]=label as u32;}
        let mut indices=(1..=(n-1)/2).map(|power|ctx.cocycle_index(power,limits[1]))
            .collect::<Result<Vec<_>,_>>().map_err(str::to_string)?;
        let images=ctx.rational_image_index(limits[2]).map_err(str::to_string)?;
        // C3 rebuilds in reverse order and checks every canonical ordinal once per field.
        for index in &mut indices {
            ctx.rebuild_cocycle_index_reverse(index,limits[1]).map_err(str::to_string)?;
        }
        Ok(Self{ctx,indices,images,inverse,max_rational:limits[3],
                max_nonrational:limits[4],max_total:limits[5]})
    }
    fn startup_json(&self)->String {
        format!("{{\"schema\":\"pext.candidate-worker-start/v1\",\"field\":{},\"structures\":{},\"cocycle_entries\":{},\"rational_image_entries\":{},\"c3_reverse_build_checked\":true}}",
            field_json(&self.ctx),self.indices[0].len(),
            numbers(self.indices.iter().map(|index|index.len().to_string())),
            self.images.entries())
    }
    fn evaluate(&mut self,raw:&str)->Result<String,String> {
        let ctx=&self.ctx;
        let encoded=raw.split(',').map(parse_u32).collect::<Result<Vec<_>,_>>()?;
        if encoded.len()!=5 || encoded.iter().any(|&value|value>=ctx.size()) {
            return Err("basis form requires five coefficients in the pinned field".into());
        }
        let mut form=[0;5];
        for (index,&basis) in encoded.iter().enumerate() {form[index]=self.inverse[basis as usize];}
        let branch=ctx.branch_roots(form).map_err(str::to_string)?;
        let pattern=numbers(branch.factorization.pattern().iter().map(ToString::to_string));
        let factors=numbers(branch.factorization.finite_factors.iter().map(|factor|
            numbers(factor.iter().map(|&value|ctx.encoding()[value as usize].to_string()))));
        let extension_modulus=branch.extension.as_ref().map_or_else(||"null".to_string(),|extension|
            numbers(extension.modulus().iter().map(|&value|ctx.encoding()[value as usize].to_string())));
        let root_degree=branch.extension.as_ref().map_or(1,|extension|extension.degree());
        let roots=numbers(branch.finite_roots.iter().map(|root|
            numbers(root.coefficients()[..root_degree].iter().map(|&value|ctx.encoding()[value as usize].to_string()))));
        let checked=ctx.checked_exceptional_candidates(form,&self.images,&self.indices,
            self.max_rational,self.max_nonrational,self.max_total).map_err(str::to_string)?;
        for index in &mut self.indices {index.reverse_representatives();}
        self.images.reverse_buckets();
        let reversed=ctx.checked_exceptional_candidates_reversed_roots(form,&self.images,&self.indices,
            self.max_rational,self.max_nonrational,self.max_total).map_err(str::to_string);
        self.images.reverse_buckets();
        for index in &mut self.indices {index.reverse_representatives();}
        if checked!=reversed? {return Err("C3 reversed candidate enumeration differs".into());}
        let mut squareclasses=Vec::with_capacity(checked.exceptional.len());
        let rows=checked.exceptional.iter().map(|(ordinal,geometry)| {
            let matrix=ctx.structure_matrix(&self.indices[0],*ordinal).map_err(str::to_string)?;
            let moved=ctx.transform_form(form,matrix).map_err(str::to_string)?;
            let orbit=ctx.conjugate_forms(moved).map_err(str::to_string)?;
            let classes=ctx.square_classes(&orbit).map_err(str::to_string)?;
            if classes.geometric_rank!=geometry.geometric_rank {
                return Err("exceptional arithmetic/geometric rank mismatch".into());
            }
            squareclasses.push(format!("[{},{}]",classes.arithmetic_rank,
                classes.contains_nonsquare_constant));
            Ok(format!("[{},[{},{},{},{}],{},{},{}]",ordinal,
                ctx.encoding()[matrix[0] as usize],ctx.encoding()[matrix[1] as usize],
                ctx.encoding()[matrix[2] as usize],ctx.encoding()[matrix[3] as usize],
                geometry.geometric_rank,geometry.branch_points,geometry.geometric_genus))
        }).collect::<Result<Vec<String>,String>>()?;
        let intervals=numbers(checked.generic_intervals.iter().map(|(start,end)|format!("[{start},{end}]")));
        Ok(format!("{{\"schema\":\"pext.checked-candidate-unit/v1\",\"structure_order\":\"left-pgl2-fq/v1\",\"candidate_order_aa\":\"reverse-cocycle-build-representatives-buckets-and-roots/v1\",\"field\":{},\"form\":{},\"factor_pattern\":{},\"infinity\":{},\"factors\":{},\"extension_modulus\":{},\"roots\":{},\"structures\":{},\"cocycle_entries\":{},\"rational_image_entries\":{},\"rational_count\":{},\"nonrational_count\":{},\"duplicate_count\":{},\"exceptional\":{},\"generic\":{},\"rows\":{},\"exceptional_squareclasses\":{},\"generic_intervals\":{}}}",
            field_json(ctx),numbers(encoded.iter().map(ToString::to_string)),pattern,branch.factorization.infinity,
            factors,extension_modulus,roots,checked.structures,
            numbers(self.indices.iter().map(|index|index.len().to_string())),self.images.entries(),
            checked.rational_count,checked.nonrational_count,checked.duplicate_count,
            checked.exceptional.len(),checked.structures-checked.exceptional.len() as u64,
            numbers(rows),numbers(squareclasses),intervals))
    }
}
fn limits(args:&[String])->Result<[u64;6],String> {
    let mut result=[0;6];
    for (slot,raw) in result.iter_mut().zip(&args[4..10]) {*slot=parse_u64(raw)?;}
    Ok(result)
}
fn read_form_line(input:&mut impl Read)->Result<Option<String>,String> {
    let mut bytes=Vec::new();
    let mut one=[0u8;1];
    loop {
        match input.read(&mut one).map_err(|error|error.to_string())? {
            0 if bytes.is_empty()=>return Ok(None),
            0=>return Err("unterminated worker form line".into()),
            _ if one[0]==b'\n'=>break,
            _ if bytes.len()>=127=>return Err("worker form line exceeds 127 bytes".into()),
            _=>bytes.push(one[0]),
        }
    }
    String::from_utf8(bytes).map(Some).map_err(|_|"worker form line is not UTF-8".into())
}
fn run()->Result<(),String> {
    let args=std::env::args().collect::<Vec<_>>();
    if args.len()!=10 {
        return Err("usage: candidate_unit q n basis_form_csv max_field_elements max_structures max_image_entries max_rational_candidates max_nonrational_maps max_total_candidates; or candidate_unit --worker q n max_field_elements max_structures max_image_entries max_rational_candidates max_nonrational_maps max_total_candidates".into());
    }
    let worker=args[1]=="--worker";
    let q=parse_u32(&args[if worker {2} else {1}])?;
    let n=parse_u32(&args[if worker {3} else {2}])?;
    let mut engine=CandidateEngine::new(q,n,limits(&args)?)?;
    if !worker {
        println!("{}",engine.evaluate(&args[3])?);
        return Ok(());
    }
    let stdout=io::stdout();
    let mut output=stdout.lock();
    writeln!(output,"{}",engine.startup_json()).map_err(|error|error.to_string())?;
    output.flush().map_err(|error|error.to_string())?;
    let stdin=io::stdin();
    let mut input=stdin.lock();
    while let Some(form)=read_form_line(&mut input)? {
        let result=engine.evaluate(&form)?;
        writeln!(output,"{result}").map_err(|error|error.to_string())?;
        output.flush().map_err(|error|error.to_string())?;
    }
    Ok(())
}
fn main() {
    if let Err(error)=run() {eprintln!("{error}");std::process::exit(2);}
}

#[cfg(test)]
mod tests {
    use super::*;
    const LIMITS:[u64;6]=[27,819,3276,1000,1000,819];
    const FORMS:[&str;2]=["1,0,1,1,0","1,1,1,0,1"];

    #[test]
    fn persistent_f27_forms_match_fresh_units() {
        let mut session=CandidateEngine::new(3,3,LIMITS).unwrap();
        assert!(session.startup_json().contains("\"c3_reverse_build_checked\":true"));
        for form in FORMS {
            let persistent=session.evaluate(form).unwrap();
            let fresh=CandidateEngine::new(3,3,LIMITS).unwrap().evaluate(form).unwrap();
            assert_eq!(persistent,fresh);
        }
        assert_eq!(session.evaluate(FORMS[0]).unwrap(),
                   CandidateEngine::new(3,3,LIMITS).unwrap().evaluate(FORMS[0]).unwrap());
    }

    #[test]
    fn malformed_forms_and_lines_are_rejected() {
        let mut session=CandidateEngine::new(3,3,LIMITS).unwrap();
        for form in ["","1,2","1,2,3,4,27","1,2,3,4,-1","1,2,3,4,5,6"] {
            assert!(session.evaluate(form).is_err());
        }
        assert!(read_form_line(&mut &b"1,2,3,4,5"[..]).is_err());
        assert!(read_form_line(&mut &b"\n"[..]).unwrap().is_some());
        assert!(read_form_line(&mut &b""[..]).unwrap().is_none());
        assert!(read_form_line(&mut &vec![b'1';129][..]).is_err());
        assert!(session.evaluate(FORMS[1]).is_ok());
    }
}
