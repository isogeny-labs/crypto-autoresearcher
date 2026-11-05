//! Per-curve certificate serialization. This binary emits only named software
//! fixtures; it is not a scientific census launcher or approval bypass.
#[path="quotient_core.rs"] mod quotient_core;
use quotient_core::{Context,Point,QuarticPoint};

fn array(items:impl IntoIterator<Item=String>)->String { format!("[{}]",items.into_iter().collect::<Vec<_>>().join(",")) }
fn numbers(values:&[u32])->String { array(values.iter().map(|v|v.to_string())) }
fn point(ctx:&Context,p:Point)->String {
    match p { Point::Infinity=>"null".into(),Point::Affine{x,y}=>numbers(&[ctx.encoding()[x as usize],ctx.encoding()[y as usize]]) }
}
fn image(ctx:&Context,p:QuarticPoint)->String {
    match p {
        QuarticPoint::PlusInfinity=>"{\"infinity\":1}".into(),
        QuarticPoint::MinusInfinity=>"{\"infinity\":-1}".into(),
        QuarticPoint::Affine{t,w}=>format!("{{\"affine\":{}}}",numbers(&[ctx.encoding()[t as usize],ctx.encoding()[w as usize]])),
    }
}
/// Coefficients use the Context's explicit log encoding; output uses polynomial indices.
pub fn certificate(ctx:&Context,coefficients:[u32;3])->Result<String,&'static str> {
    let curve=ctx.curve(coefficients[0],coefficients[1],coefficients[2])?;
    let identity=ctx.identity();
    let field=format!("{{\"prime\":{},\"degree\":{},\"modulus\":{},\"primitive_polynomial_index\":{},\"logarithm_to_polynomial_index\":{}}}",identity.prime,identity.degree,numbers(&identity.modulus),identity.primitive_polynomial_index,numbers(&identity.logarithm_to_polynomial_index));
    let points=curve.points(); let cosets=curve.quotient_classes()?;
    let mut serialized_cosets=Vec::new(); let mut quotients=Vec::new();
    for coset in cosets {
        let target=coset.representative;
        serialized_cosets.push(format!("{{\"representative\":{},\"members\":{}}}",point(ctx,target),array(coset.members.iter().map(|&(p,h)|format!("{{\"point\":{},\"half\":{}}}",point(ctx,p),point(ctx,h))))));
        let form=curve.quotient_form(target)?;
        let conjugates=ctx.conjugate_forms(form)?; let square=ctx.square_classes(&conjugates)?;
        let forms=array(conjugates.iter().map(|f|numbers(&f.map(|a|ctx.encoding()[a as usize]))));
        let relations=array(square.relations.iter().map(|(m,s)|format!("[{},{}]",m,s)));
        let charts=if target==Point::Infinity { "null".into() } else {
            let mut rows=Vec::new();
            for &p in &points { rows.push(format!("{{\"point\":{},\"image\":{}}}",point(ctx,p),image(ctx,curve.forward(target,p)?))); }
            array(rows)
        };
        quotients.push(format!("{{\"target\":{},\"chart_kind\":\"{}\",\"conjugates\":{},\"relations\":{},\"geometric_rank\":{},\"arithmetic_rank\":{},\"contains_nonsquare_constant\":{},\"images\":{}}}",point(ctx,target),if target==Point::Infinity{"baseline-cubic"}else{"quartic"},forms,relations,square.geometric_rank,square.arithmetic_rank,square.contains_nonsquare_constant,charts));
    }
    Ok(format!("{{\"schema\":\"pext.quotient-certificate/v1\",\"scope\":\"one-curve-standard-structure\",\"field\":{},\"curve\":{},\"points\":{},\"cosets\":{},\"quotients\":{}}}",field,numbers(&coefficients.map(|a|ctx.encoding()[a as usize])),array(points.iter().map(|&p|point(ctx,p))),array(serialized_cosets),array(quotients)))
}
fn main() {
    let args:Vec<_>=std::env::args().collect();
    let fixture=args.get(1).map(String::as_str).unwrap_or("");
    let (q,n,a2,a4,a6)=match fixture {
        "f3-char3"=>(3,1,1,0,1),"f5-odd"=>(5,1,0,1,1),
        "f5-split"=>(5,1,0,1,0),"f9-embedded"=>(3,2,1,0,1),
        "f125-embedded"=>(5,3,0,1,1),
        _=>{eprintln!("required named software fixture: f3-char3|f5-odd|f5-split|f9-embedded|f125-embedded");std::process::exit(2)}
    };
    if args.len()!=2 { eprintln!("one fixture argument required");std::process::exit(2); }
    let ctx=Context::new(q,n,125).expect("fixed fixture field");
    println!("{}",certificate(&ctx,[ctx.integer(a2),ctx.integer(a4),ctx.integer(a6)]).expect("fixture certificate"));
}
