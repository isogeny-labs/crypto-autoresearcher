from pathlib import Path
import argparse, tempfile, platform, zlib
from reportlab import rl_config
rl_config.invariant = 1
import csv, hashlib, html, io, json, re, zipfile, unicodedata
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, KeepTogether, Flowable
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader, PdfWriter

B=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description="Build the frozen comprehensive report; no scientific programs are launched.")
parser.add_argument('--output-root',type=Path,default=B)
parser.add_argument('--font-dir',type=Path,default=Path('/System/Library/Fonts/Supplemental'))
args=parser.parse_args()
O=args.output_root.resolve(); OUT=O/'output/pdf/nist-seed-selection-search-comprehensive-report.pdf'
OUT.parent.mkdir(parents=True,exist_ok=True);(O/'tmp/pdfs').mkdir(parents=True,exist_ok=True)
inputs=json.loads((B/'inputs/build-inputs.json').read_text())
archive=B/'inputs/source-inputs.zip'
if hashlib.sha256(archive.read_bytes()).hexdigest()!=inputs['source_archive_sha256']:
 raise ValueError('Frozen source archive digest mismatch')
_source_tmp=tempfile.TemporaryDirectory(prefix='nist-report-inputs-');R=Path(_source_tmp.name)
with zipfile.ZipFile(archive) as z:
 if set(z.namelist())!=set(inputs['source_files']):raise ValueError('Source archive inventory mismatch')
 for path,digest in inputs['source_files'].items():
  dest=R/path
  if not dest.resolve().is_relative_to(R.resolve()):raise ValueError('Unsafe source archive path')
  data=z.read(path)
  if hashlib.sha256(data).hexdigest()!=digest:raise ValueError('Source digest mismatch: '+path)
  dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
FONT=str(args.font_dir.resolve())+'/'
for name,digest in inputs['font_sha256'].items():
 if hashlib.sha256((args.font_dir/name).read_bytes()).hexdigest()!=digest:
  raise ValueError('Font differs from the pinned report input: '+name)
for n,f in [('Body','Arial.ttf'),('Bold','Arial Bold.ttf'),('Italic','Arial Italic.ttf')]: pdfmetrics.registerFont(TTFont(n,FONT+f))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='Bold',italic='Italic',boldItalic='Bold')
NAVY=colors.HexColor('#132C46');TEAL=colors.HexColor('#006D77');BLUE=colors.HexColor('#EAF1F6');INK=colors.HexColor('#243746');GRAY=colors.HexColor('#61717F')
S=getSampleStyleSheet()
for n,kw in {'BodyX':dict(fontName='Body',fontSize=10,leading=14,spaceAfter=9,textColor=INK), 'SmallX':dict(fontName='Body',fontSize=8,leading=10.5,spaceAfter=6,textColor=GRAY), 'H1X':dict(fontName='Bold',fontSize=22,leading=27,spaceAfter=18,textColor=NAVY), 'H2X':dict(fontName='Bold',fontSize=12,leading=16,spaceBefore=8,spaceAfter=7,textColor=TEAL), 'CellX':dict(fontName='Body',fontSize=8.5,leading=11,textColor=INK), 'HeadX':dict(fontName='Bold',fontSize=8.5,leading=11,textColor=colors.white), 'CodeX':dict(fontName='Body',fontSize=7.2,leading=9.1,spaceAfter=5,textColor=INK), 'CoverX':dict(fontName='Bold',fontSize=34,leading=40,textColor=NAVY,spaceAfter=20)}.items(): S.add(ParagraphStyle(name=n,**kw))
W,H=A4;WIDTH=W-94
story=[]; outline=[]
def clean(x):
 x=str(x).replace('\u2011','-').replace('\u2013','-').replace('\u2014',' - ').replace('\u00a0',' ').replace('\u2265','>=').replace('\u2264','<=').replace('\u2260','!=').replace('\u00d7',' x ')
 return x

def p(t,sty='BodyX'): return Paragraph(clean(t),S[sty])
def add(t,sty='BodyX'):story.append(p(t,sty))
def h(t):add(t,'H2X')
def page(title,kicker=None):
 if story:story.append(PageBreak())
 if kicker:add(kicker.upper(),'SmallX')
 q=p(title,'H1X');q._section=title;story.append(q);outline.append(title)
def table(headers,rows,widths=None):
 data=[[p(html.escape(str(x)),'HeadX') for x in headers]]+[[p(html.escape(clean(x)),'CellX') for x in row] for row in rows]
 t=Table(data,colWidths=widths or [WIDTH/len(headers)]*len(headers),repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),NAVY),('VALIGN',(0,0),(-1,-1),'TOP'),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,BLUE]),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('LINEBELOW',(0,-1),(-1,-1),.4,colors.HexColor('#C5D2DB'))]))
 story.append(t);story.append(Spacer(1,10))

def slug(s):return re.sub('[^a-z0-9]+','-',s.lower()).strip('-')
frozen_manifest=json.loads((B/'source-manifest.json').read_text())
sources=[R/x['path'] for x in frozen_manifest['sources']]
for source,record in zip(sources,frozen_manifest['sources']):
 if hashlib.sha256(source.read_bytes()).hexdigest()!=record['sha256']:raise ValueError('Catalog source mismatch')
ids={str(x.relative_to(R)):f'R{i+1:02d}' for i,x in enumerate(sources)}
def ref(path):
 path='research/'+path if not path.startswith('research/') else path
 rid=ids[path];commit='134317a08335f64746eef21d507fd2219f213c45' if 'nist_seed_mattsson_comparison' in path else 'd0b5c6e101400bde71f696e6c1cd215c0d9302e7'
 return f'<link color="#006D77" href="https://github.com/isogeny-labs/crypto-autoresearcher/blob/{commit}/{path}">[{rid}]</link>'
def refs(*paths): add('Evidence: '+' '.join(ref(x+'/report.md') for x in paths),'SmallX')
cohortpath=R/'research/nist_seed_ccr_root_matching_20261027/signed-frobenius-20261027/prior-rows.json'
cohort=sorted(json.loads(cohortpath.read_text()),key=lambda c:(c['timestamp'],c['ordinal']))
final=json.loads((R/'research/nist_seed_final_checks_20261028/VERIFICATION.json').read_text())
matt=json.loads((R/'research/nist_seed_mattsson_comparison_20261106/comparison.json').read_text())
assert len(cohort)==21 and sum(c['label']=='omitted' for c in cohort)==11
assert final['status']=='PASS' and final['curve_order_certificates']==63
assert matt['status']=='PASS' and len(matt['rows'])==19 and matt['symbols_checked']==3173
manifest={'report_date':'2026-11-06','timezone':'America/Los_Angeles','scope':'Synthesis of retained search records; no new scientific trial','source_snapshot_commit':'d0b5c6e101400bde71f696e6c1cd215c0d9302e7','mattsson_commit':'134317a08335f64746eef21d507fd2219f213c45','sources':[{'id':ids[str(x.relative_to(R))],'path':str(x.relative_to(R)),'sha256':hashlib.sha256(x.read_bytes()).hexdigest()} for x in sources], 'cohort_sha256':hashlib.sha256(cohortpath.read_bytes()).hexdigest()}
assert manifest==frozen_manifest
(O/'source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(O/'cohort.json').write_text(json.dumps(cohort,indent=2)+'\n')

# Cover
story.append(Spacer(1,65));add('RESEARCH RECORD / 6 NOVEMBER 2026','SmallX');story.append(Spacer(1,20))
add('The NIST / ANSI<br/>seed-selection search','CoverX')
add('Comprehensive investigation report','H1X')
add('Twenty-one curves. Six reconstructed streams.<br/>Eleven qualifying omissions. One unresolved historical decision.','H2X')
story.append(Spacer(1,28))
add('<b>Central finding:</b> the seed bytes are reproducible, but the original rule or process that selected the published curves has not been recovered. Many specific arithmetic and implementation explanations fail. Some exploratory fits and field-specific patterns remain observations, without the provenance needed to identify the historical mechanism.')
story.append(Spacer(1,20))
table(['Evidence population','Historical criterion','Current research boundary'],[['10 published + 11 omitted','UNRESOLVED','No further predicate search']], [158,158,WIDTH-316])
add('Prepared from the retained October 16-28 investigations and the November 6 Mattsson reconciliation. This report distinguishes arithmetic facts, documentary findings, configured-software behavior, engineering controls, exploratory fits, and unknown history.','SmallX')
add('Includes a source catalog, exact curve records, and embedded evidence attachments. Prepared for the research owner; this is a synthesis, not an independent replication of every archived computation.','SmallX')

page('Executive findings','Decision record')
add('<b>The search did not identify the criteria used by the original program.</b> It did explain the published prime-field seed bytes and establish exact identities for the 21-curve comparison. The reconstructed omissions are qualifying stream positions, not documented rejection events.')
table(['Finding','Supported conclusion'],[
['Seed provenance','All ten published prime-field seeds match clock-initialized rand48 streams. Six initialization timestamps account for them.'],
['Ordinary validation','The 21 curves pass the retained order, nonsingularity, non-anomalous and bounded MOV checks. The final pass verifies 63 original/opposite-b/twist order certificates.'],
['Curve arithmetic','Twist strength, exact embedding degree, conductors, class-group tests, auxiliary-input divisors and fixed workflow proxies do not identify the historical split.'],
['Specific leads','P-224 cubic j / 3-division splitting is a real local pattern. An exploratory auxiliary-prime-199 two-rule classifier fits all 21 labels. Neither has established original-program use.'],
['Historical software','Period sources and later point-counting reconstructions expose real branches and possible faults, but no tested, authenticated acceptance path explains all eleven omissions.'],
['ECPP boundary','A period proof-search exhaustion mechanism is reproducible on an induced control. Retained cohort-wrapper engineering records execute zero named orders; this is not a cohort result.'],
['Mattsson reconciliation','All 19 overlapping curve identities reconcile. One P-224 sign change is isomorphic; SEA list/cutoff differences are convention and formula differences.'],
['Completion status','Historical objective unresolved. Mattsson follow-up PR #3129 is open at the last verified check, with all 22 hosted checks successful.']],[126,WIDTH-126])
refs('nist_seed_final_checks_20261028','nist_seed_p224_j_cube_20261025','nist_seed_ccr_root_matching_20261027/signed-frobenius-20261027','nist_seed_ecpp_compat_20261024','nist_seed_mattsson_comparison_20261106')

page('How to read this report','Navigation and claim labels')
add('The main narrative follows the chain from recovered seed bytes to candidate arithmetic, contemporary workflows, source archaeology, and the closing checks. Appendix A catalogs every retained report used in this synthesis, including superseded intermediate records. Appendix B prints exact identities and arithmetic parameters for all 21 curves. Appendix C lists primary external sources and the final evidence boundary.')
table(['Label','Meaning in this report'],[
['Verified / derived arithmetic','An exact archived computation, certificate or independent arithmetic check supports the stated finite result. This PDF does not rerun the scientific producer.'],
['Retrieved documentary fact','A specific source was obtained and read in the archived study. A dated citation is distinguished from a retrieved original draft.'],
['Configured-software result','Behavior of a specified recovered or reconstructed program under its recorded build and inputs; original NIST use remains unproven.'],
['Engineering control','A compatibility, framing, mock, or correctness observation. It does not count as a candidate-level scientific result.'],
['Exploratory fit','A relationship found after labels or correlated features were available. Exact fit alone is not historical causation or an independently predictive rule.'],
['Unknown / censored','Missing inputs, incomplete factorization, timeout, unavailable source, or unobserved execution. It is not recoded as acceptance or rejection.']],[130,WIDTH-130])
add('Reference tags such as [R01] link to the exact report path in a pinned repository snapshot. Appendix A gives the path and archival synopsis; the embedded source manifest gives each file SHA-256. Chronology follows recorded report dates, while archive-capture dates, PDF metadata, reconstructed timestamps and publication dates retain different meanings.')
add('<b>Important correction:</b> an older source-search note and one later refresh said the November 1997 draft had not been obtained. The recovered-draft report supersedes that statement. The 103-page November draft is available; the separately cited June 1996, January 1997 and June 1997 versions remain missing as full draft texts.')
refs('nist_seed_1997_original_draft_20261023','nist_seed_final_checks_20261028/provenance-refresh-01')

page('1. Scope and exact workload','What the search attempted')
add('The objective was to explain why eleven prime-field seed positions that pass the reconstructed eligibility screen were not published, while ten others were. The user raised possible transfer, j-invariant, endomorphism and CM/conductor explanations and suggested that two rules might operate together. The work therefore examined both curve properties and contemporary generation/validation behavior.')
add('The fixed comparison has ten published curves and eleven reconstructed omissions, across six streams and five field sizes. The four fields with both labels contain nineteen curves: five at 192 bits, four at 224 bits, eight at 239 bits and two at 256 bits. P-384 and P-521 are published singletons. Results on nineteen rows cannot silently be promoted to a complete 21-row result.')
add('The exact model is y^2 = x^3 - 3x + b over F_p. Each row retains p, b, n, the SHA-derived parameter c, full seed, timestamp, one-based ordinal and full curve UID. The trace is t=p+1-n. The symbol c is not the trace. In the canonical records the coefficient relation is c*b^2 = -27 mod p.')
add('The eleven windows are not proven to have been visited by the original program. Extra RNG calls, restarts, a separate point generator, review choices, or a flawed counting or certification path could prevent a simple block-by-block history. Retrospective mathematical eligibility does not demonstrate an original rejection for weakness.')
h('Fixed-population accounting')
table(['Population','Published','Omitted','Use'],[['Complete cohort','10','11','All six streams'],['Same-field comparison','8','11','Four fields with both labels'],['Mattsson external table','8','11','Excludes published P-384 and P-521']],[140,70,70,WIDTH-280])
refs('nist_seed_skipped_curves_20261016','nist_seed_generation_process_20261016','nist_seed_mattsson_comparison_20261106')

page('2. Recovered seed generation','Seed bytes versus selection')
add('The public reconstruction identifies consecutive 20-byte seed blocks from the high byte of successive rand48 states, initialized by srand48(timestamp). In integer form, x_next = (0x5DEECE66D*x + 0xB) mod 2^48, with initial state (timestamp << 16) | 0x330E; each output byte is x_next >> 40. Equivalently, use lrand48() >> 23. This regenerates all ten prime-field published seeds.')
table(['Timestamp / UTC start','Published positions','Other qualifying positions'],[
['863711343 / 1997-05-15 15:49:03','239v1: 2185; v2: 2320; v3: 3048','36, 1562, 2491, 2682, 2863'],
['863966734 / 1997-05-18 14:45:34','192v1: 139; v3: 5228; v2: 6013','2198, 5405'],
['871002724 / 1997-08-08 01:12:04','P-521: 1136','None in the reported cohort'],
['871696354 / 1997-08-16 01:52:34','P-256: 1842','876'],
['872952608 / 1997-08-30 14:50:08','P-384: 2688','None in the reported cohort'],
['891607927 / 1998-04-03 12:52:07','P-224: 7026','777, 1485, 5736']],[174,170,WIDTH-344])
add('The seed-reconstruction result is much stronger than a remembered phrase story: it predicts the exact bytes. It does not identify the selection rule or the number of attempted timestamp restarts. The timestamps are mathematically reconstructed initialization values; they are not surviving wall-clock logs.')
add('The other fairly clear extra restriction is bitlen(n) <= bitlen(p). It is not n < p: published prime239v2 has p < n < 2^239. The eleven omissions are what remain under the particular retrospective root/order-width screen, not all positions admitted by the original near-prime standards text.')
add('The broader record also reconstructs four binary-field seed streams and six May-1997 base points with FreeLIP, while B-163 and the four later NIST prime-field base-point recipes remain unresolved in the cited disclosure. Those ancillary findings do not change the 21-row prime-field selection workload.')
add('Seed provenance evidence: '+ref('nist_seed_provenance_20261016/README.md'),'SmallX')
refs('nist_seed_selection_deep_20261016','nist_seed_generation_process_20261016')

page('3. The 21-row cohort','No post-endpoint additions')
table(['Field','Ordinal','Canonical label','Published?'],[[str(int(c['p']).bit_length()),str(c['ordinal']),c['name'],'yes' if c['label']=='published' else 'no'] for c in cohort],[48,60,WIDTH-176,68])
add('P-192 / prime192v1, P-256 / prime256v1, secp224r1 / P-224, secp384r1 / P-384, and secp521r1 / P-521 are aliases in these records. The 192-bit ordinal 5228 is v3, while ordinal 6013 is v2. Appendix B provides full seeds and UIDs so names alone are never the identity key.','SmallX')
refs('nist_seed_skipped_curves_20261016','nist_seed_final_checks_20261028')

page('4. Standards chronology and version effects','ANSI and NIST need not be identical')
add('A complete 103-page ANSI X9.62 working draft with a 17 November 1997 cover was recovered. Its PDF was encoded in December 1997 and archived later; those metadata do not notarize every circulation date. It already includes the seven published 192-, 239- and 256-bit prime examples, including P-256. Its generation procedure supplies no additional documented gate distinguishing the eleven omissions.')
table(['Dated material','What was obtained','What remains unknown'],[
['21 June 1996 draft','Citation in NIST SP 800-15','Full draft and parameter tables'],
['15 January 1997 draft','Citation in USPS criteria','Full draft and parameter tables'],
['11 June 1997 draft','Citation and unnamed example in a 1998 implementation paper','Full draft; exact identity of that example'],
['17 November 1997 draft','Full text, seven exact published seed examples, generation procedure','Original generator and decisions'],
['20 September 1998-cover text','Full later standards text','Date and purpose of each editorial change']],[115,188,WIDTH-303])
add('There is a concrete rounding difference: the 1997 seed formula uses ceil(log2 p); the 1998-cover version uses floor(log2 p). The frozen replay finds that the earlier formula matches all 21 archived coefficients, while the later printed formula matches only 8/21 (4 publications and 4 omissions). It changes the curves for thirteen seeds. This discrepancy must be handled as a version issue, not as evidence that those thirteen were historically rejected.')
add('The 1997 near-prime procedure also allows smooth cofactors and an operator-supplied minimum order. Retained certified records yield at least 69 full-prime-order seed positions satisfying its numerical checks, and at least 99 positions after including 30 near-prime cases. The latter is a lower bound: 10,083 other positions have censored exact-order outputs. These populations differ from the chosen 21-row retrospective screen and are not counts of historical attempts.')
refs('nist_seed_1997_original_draft_20261023','nist_seed_1997_selection_extension_20261023/x962_rounding','nist_seed_1997_acceptance_20261024','nist_seed_1997_nearprime_20261024')

page('5. Root choices, twists and order filters','Simple arithmetic explanations')
add('For the seventeen cohort rows with p=3 mod 4, the recorded prime-order b is the usual exponentiation root of -27/c. That convention retains nine publications and eight omissions. A lower-valued-root choice and parity choice also overlap both labels. At P-224, where p=1 mod 4, opposite b signs give isomorphic models and cannot supply an intrinsic distinction.')
add('Every cohort curve has j different from 0 and 1728. The rational-twist classification therefore gives the ordinary pair of forms: the original and its nontrivial quadratic twist, rather than exceptional quartic or sextic twist families. A separate Sage rederivation agrees with the retained twist-order arithmetic.')
add('Largest-twist-factor preference fails by explicit counterexample. For P-224 ordinals 777, 1485, 5736 and 7026, the largest twist-prime factors have 83, 122, 106 and 118 bits. Published P-224 is not the maximum. In the 239-bit field, omitted ordinal 36 has a 138-bit largest factor, between published v1 at 86 bits and v2 at 147 bits. A uniform monotone cutoff cannot recover all the labels.')
add('A field-fixed minimum order r_min that retains every publication must also retain seven of the eleven omissions. It therefore cannot explain the entire split. Fixed order-shape/sparsity preferences likewise have counterexamples. A correct base-point search on a prime-order, cofactor-one group can use every nonidentity point, so failure to choose a generator is not an intrinsic curve exclusion.')
add('Only one of the 21 true quadratic twists has prime order: published secp384r1. Requiring prime twist order would also discard nine published controls. Twist arithmetic is thus useful for testing specific rules but does not establish the original selection decision.')
refs('nist_seed_generation_process_20261016','nist_seed_twist_classification_20261023','nist_seed_selection_followup_20261016','nist_seed_1997_order_threshold_20261024','nist_seed_selection_workflow_20261023','nist_seed_final_checks_20261028')

page('6. Transfers and implementation input surfaces','Attack preconditions versus curve selection')
add('The search explicitly checked pairing-transfer preconditions. For the nineteen curves in the four mixed fields, the exact multiplicative order k=ord_n(p) was computed and separately checked. The smallest k in that population has 189 bits; the smallest among the omissions has 190 bits. None meets the predeclared bounds 100, 1,000, 10,000 or 1,000,000. These particular low-embedding-degree rules reject none of the eleven omissions.')
add('The twist-subgroup screen includes 25 certified twist factors of at least 80 bits across the full cohort. None satisfies p^k=1 mod ell for k from 1 through 1,000. This excludes the tested bounded transfer route on those factors; it is not a complete curve-security theorem or a proof that every transfer over every extension is impossible.')
add('Order-neighbor divisors were also examined in relation to auxiliary-input algorithms. Such algorithms require secret-power auxiliary group elements beyond an ordinary ECDLP instance. The necessary inputs must not be assumed present in ECDSA or ECDH merely because n-1 or n+1 has a convenient divisor. The fixed divisor screen did not supply a common omitted-only opportunity, and the cited algorithm is later than 1997.')
add('The conditional invalid-curve and singular-companion surfaces are shared within each field when a scalar implementation omits curve-membership checks and uses the same a=-3 addition formulas. The configured b does not restrict those alternate equations. Singular companions with b=+2 and -2 similarly depend on the shared field and a coefficient. These implementation-input surfaces do not separate the named candidates.')
add('These results address specified attack preconditions and formula behavior. They neither recover a hidden transfer criterion nor establish a full security verdict. The unknown acceptance history should not be converted into evidence for a cryptanalytic weakness.')
refs('nist_seed_exact_embedding_degree_20261023','nist_seed_twist_embedding_20261023','nist_seed_aux_input_divisors_20261023','nist_seed_invalid_curve_surface_20261023','nist_seed_singular_companions_20261023')

page('7. j-invariants and exact conductors','The conductor-of-three correction')
add('For these a=-3 models, j=6912/(4-b^2) mod p. The P-224 publication has cubic j and four linear factors in the 3-division polynomial. The three P-224 omissions have noncubic j and factor degrees 1 and 3. This is a genuine field-specific pattern. Published P-256 has noncubic j and the same 1,3 pattern as its omission, so a universal requirement that j be a cube fails.')
add('The later signed-Frobenius audit gives the P-224 observation a more exact interpretation: the publication has scalar Frobenius -I on 3-torsion, while the three omissions have nonscalar Jordan action. The publication\'s quadratic twist consequently has full rational 3-torsion. This does not prove a universal equivalence between cubic j and a torsion pattern, or show that an original point counter needed a cube root of j.')
table(['Field','Omitted f_pi','Published f_pi'],[['192 bits','1, 1','1, 1, 1'],['239 bits','1, 1, 1, 5, 1','1, 5, 1'],['224 bits','1, 1, 1','3'],['256 bits','1','1']],[90,200,WIDTH-290])
add('Here Delta_pi=t^2-4p=f_pi^2*D_K, where D_K is the fundamental CM-field discriminant. The exact P-256 pair both have f_pi=1. The published curve with f_pi=3 in the retained same-field census is P-224, not P-256. A factor 3 in P-256\'s fundamental discriminant expresses ramification; it is not a conductor of three. An alternate model or curve setting must be identified explicitly before transferring a conductor claim.')
add('The actual endomorphism-order conductor and the Frobenius-order conductor are different objects. The former divides f_pi; f_pi=1 forces the maximal order, but a nontrivial f_pi alone does not determine the exact endomorphism ring. The shared f_pi=5 on an omitted 239-bit row and published v2 is a direct counterexample to a simple conductor exclusion.')
refs('nist_seed_p224_j_cube_20261025','nist_seed_exact_conductor_20261023','nist_seed_exact_conductor_census_20261023','nist_seed_ccr_root_matching_20261027/signed-frobenius-20261027')

page('8. CM class numbers and dated advice','Later requirements tested without fitted bounds')
add('A plausible mathematical motive for avoiding special CM structure is a class-number lower bound. The documentary search located h(O_K)>=200 in Baier\'s 2002 account and ETSI\'s July 2005 document, and h(O_K)>10^7 in RFC 5639 (March 2010). These are later sources; no retrieved artifact establishes their adoption by NIST in 1997.')
add('The stronger direct certificate test uses the first 24 split rational primes and checks a sufficient discriminant inequality. The resulting distinct ideal classes certify h(K)>=2^24=16,777,216. All eleven omissions and eight published same-field controls receive that lower bound. P-384 and P-521 remain UNKNOWN_D_K for this particular method because certified fundamental discriminants were not imported. Unknowns are not counted as failures.')
add('A subsequent operational test asks for a single ideal-class element of order at least 200. Taking the first odd split prime, no chosen class returns to the identity in powers 1 through 199 for any of those nineteen fields. Independent Python and GP computations agree on all 3,781 reduced powers per arm. Thus all eleven omissions satisfy both the class-number and element-order tests at the dated bounds.')
add('The earlier genus-theory screen finds overlapping class-group 2-ranks: omitted ranks include 2,3,4,5,7,9, while publications include 1,2,3,4,6. Every field in the nineteen-row comparison has even class number. Neither parity nor a global rank threshold recovers the labels.')
add('The report stages must be read in order. The initial source audit correctly said that the 10^7 bound had not yet been tested; the later certificate report completes the omission test. The earlier comparison to a modern externally claimed complete small-class-number list remains conditional on that external completeness claim. The direct nineteen-field certificates avoid that dependency. A large Frobenius-order class number must not be substituted for a lower bound on the maximal order without the proper conductor relation.')
refs('nist_seed_class_number_dated_bound_20261028','nist_seed_class_number_dated_bound_20261028/certificate-report-01','nist_seed_class_number_dated_bound_20261028/element-order-01/report-01','nist_seed_genus_rank_20261023')

page('9. RNG consumption and validation libraries','What the configured replays actually show')
add('The search considered variable draw counts, unaligned consumption, wrappers, buffering and reseeding as alternatives to a curve-arithmetic gate. A model in which every validation call consumes the seed generator is not automatic: the reconstructed May base points use FreeLIP\'s separate RNG, while the curve seeds use libc rand48. The caller would have to connect the streams in a demonstrable way.')
add('The FreeLIP prime-order replay classifies all eleven omitted orders and ten published orders alike under the specified zprobprime and zprime calls. Earlier native build failures tested zero cohort orders and remain retained. The successful build is a modern compatibility configuration, not an original system image.')
add('A routine FreeLIP primality call can reproduce the seven-output prefix in all six May base-point recipes. With portable 26-bit limbs, zprobprime(v,7) or zprime(v,8,2), using v=p or v=n, yields all 24 proposed call/curve matches; 24 wrong-prefix or 30-bit controls match none. Several calls therefore explain the same observed prefix. This does not identify a unique historical call or explain the seed omissions.')
add('Recovered March/August 1997 NTL source has a different literal consumption pattern: its default ProbPrime uses one small random base followed by ten full-size bases. Under 26-bit limbs the retained analysis derives at least 91 recurrence advances for 192-bit inputs and 111 for 239-bit inputs. Those bounds do not match a literal seven-output prefix. Source similarity is not enough to replace an executable call trace.')
add('The pre-1997 FreeLIP audit checks 21 orders, two limb sizes, four seeds and A/A repeats. All 168 unique configured primality calls pass; the tested coefficient inversions and square roots pass as well. Square-root calls use no FreeLIP RNG draws, twenty-round primality uses twenty calls, and the independently seeded rand48 stream remains unchanged. All 756 recorded inverse aliasing/version configurations pass.')
add('No retained source-bound wrapper, buffering or reseeding mechanism supplies a verified all-eleven omission explanation. This is not a proof that all possible RNG-consumption paths are excluded. The missing part is the original caller, its initialization and stream sharing, and its stopping or error policy.')
refs('nist_seed_freelip_primality_20261023','nist_seed_freelip_prefix_20261024','nist_seed_ntl_1997_source_20261024','nist_seed_pre1997_library_20261027')

page('10. Point-counting cost and root branches','Arithmetic proxies are not old execution times')
add('The strict Elkies-only trace-information proxy reaches its threshold earlier for omissions in 24 of 25 same-field comparisons. The P-256 pair reverses the direction. Adding Atkin information yields 20 earlier, three later and two tied comparisons, including a P-256 tie. Neither fixed proxy selects the eleven omissions. These are exact finite arithmetic comparisons, not measured 1997 runtimes.')
add('The fixed two-cost Pareto check pairs the point-counting proxy with an n-1 certification proxy. Among sixteen preceding-omission/publication comparisons, omissions dominate publications in five pairs under one certificate-cost metric and thirteen under another. A strict policy requiring the publication to be better on both costs is contradicted. Changing the direction does not repair every field.')
add('The all-root SEA audit follows every rational root at levels 3,5,13 in the available LiDIA build. Its final 63 cohort cells complete, with separate exceptional-j controls and independently checked arithmetic. The first attempt\'s absent table path and three aborting special controls are retained as execution observations. No omission-specific failed branch appears at those levels.')
add('The CCR root-pairing reconstruction examines 147 curve/degree cells at levels 3,5,7,11,13,17,19. The corrected conversion recovers all 112 rational cyclic kernels in the favorable cells. None of the tested cohort projection collisions occurs. The literal printed conversion error instead loses higher-degree kernels for publications as well as omissions and therefore does not reproduce the selection split.')
add('The modular-coordinate guard audit similarly finds that the bounded tested predicates pass all 21 curves. A real printed-formula discrepancy fails every cohort curve at degree 13 when interpreted literally. A bug that also loses the controls cannot serve as a recovered explanation of the historical labels.')
add('The later full-counter build and explicitly reconstructed sign-handling arms remain version-bound observations. A modified or later source tree is not authenticated as the 1997 generator. Failed controls, missing tables, partial cell output and successful final markers with internal errors are not silently turned into curve rejection decisions.')
refs('nist_seed_1997_selection_extension_20261023/sea_signature','nist_seed_1997_atkin_20261024','nist_seed_1997_selection_extension_20261023/workflow_pareto','nist_seed_sea_all_roots_20261027','nist_seed_ccr_root_matching_20261027','nist_seed_modular_coordinate_guards_20261027')

page('11. Two-rule searches and the prime-199 fit','A fit exists; its history is unproven')
add('The earlier bounded library contains 1,913 Boolean predicates from 574 numeric/source columns. It yields 495 distinct complemented signatures on the 21 exact identities. The independent implementations evaluate 122,265 unordered signature pairs and all sixteen Boolean truth tables per pair: 1,956,240 cases. This library has zero robust or possible fits. That statement excludes this finite library, not every conceivable pair of criteria.')
add('The signed-Frobenius extension adds new features and checks 1,281 cells: 21 curves times 61 odd primes through 293. The arithmetic implementations agree. This extended exploration finds exact fits, including the following at auxiliary prime 199: accept if C199 <= 32 and D199 <= 2048. C199 is a positive-half eigenvalue candidate-list metric; D199 is the minimum predicted irreducible-factor degree for the 199-division polynomial.')
table(['At ell=199','Publications','Omissions'],[['Split/Elkies branch','4: C <= 20','7: C = 60'],['Nonsplit/Atkin branch','6: list skipped, D <= 1980','4: list skipped, D = 2200 or 2475'],['Combined displayed rule','10 retained','0 retained']],[160,166,WIDTH-326])
add('The caps 32/2048 are post-observation representatives, not recovered constants. Any candidate cap 20..59 and degree cap 1980..2199 gives the same cohort labels. The search and calibration were exploratory; the descriptive capacity counts are not p-values or probabilities of an original choice. No held-out historical prediction establishes the rule.')
add('The subsequent fixed-policy checks weaken a simple resource-limit interpretation. Applying the caps uniformly through 199 discards every publication. At 199 with the splitting degree unknown it retains only six publications. The measured later full-counter replay stops below 199 for all omissions; even published P-224 stops at 197. A callback at 199 cannot explain those particular replay omissions. The recovered source allocates 100 candidate slots at 199, not 32; a cap on every intermediate polynomial also contradicts controls.')
add('This is why the full search cannot be summarized as either “nothing ever fits” or “the two criteria were found.” The exact fit is retained as a mathematical observation. The historical program, mandatory invocation, resource policy and cap provenance are missing.')
refs('nist_seed_ccr_root_matching_20261027/two-rule-audit-20261027','nist_seed_ccr_root_matching_20261027/signed-frobenius-20261027','nist_seed_ccr_root_matching_20261027/signed-frobenius-20261027/calibration-01')

page('12. Historical source archaeology','Actual documents versus inferred lineage')
add('Recovered sources include the relevant 1995 Mueller dissertation, Maurer\'s 1994 implementation thesis, Lehmann\'s 1994 modular-polynomial thesis, and a LiDIA package advertised as 1.3 in a May 1997 archive capture. These sources narrow the plausible workflow and expose actual function interfaces, relation tables and branch logic. None identifies the NIST/Reiter caller or its per-candidate decisions.')
add('Mueller\'s two special fast-counting routes - supersingularity and ordinary isogeny classes containing j=0 or 1728 - occur on none of the 21 cohort rows in the fixed test. They are source-described counting shortcuts, not documented rejection criteria. The historical modular-polynomial interface accepts j directly; a universal cube-root-of-j prerequisite is not established.')
add('A complete printed ell=5 polynomial is collated against a later table: G5(X,J)=(X^2+10X+5)^3-JX. All coefficient rows agree, including reduction modulo 101. This authenticates a mathematical table identity, not the original binary files, backend representation or NIST use. Historical native-word binary codecs differ across libI, LIP and GMP; source compatibility depends on backend and ABI.')
add('The May 1997 package contains general polynomial degree routines but not the named standalone ECO caller. A later ChangeLog records a September 2001 splitting-degree fix. The exact faulty predecessor, patch and introduction date were not recovered. A 2019 root-wrapper fix must not be backdated into a 1997 root routine that lacked the same filtering call.')
add('Static inspection finds an unguarded degree-one path into an invalid factor-list index. This is a source-level edge, not a native crash reproduction or a cohort rejection result. A conditional randomized-degree error bound is tiny under independent uniform field draws and valid inputs, but those assumptions do not prove the behavior of the actual deterministic RNG/caller. All 21 historical application statuses remain undetermined.')
add('The recovered correspondence attributes the original programming to Bob Reiter. Solinas\'s retrospective phrase-hash recollection was qualified and the old archives had not been located. The exact rand48 byte reconstruction supersedes that recollection as a complete account of the prime seeds. The Reiter-Solinas tau-adic patent is a characteristic-two Koblitz setting, not an acceptance procedure for this prime-field cohort.')
refs('nist_seed_ccr_root_matching_20261027/signed-frobenius-20261027/period-eigenvalue-20261027','nist_seed_ccr_root_matching_20261027/signed-frobenius-20261027/period-eigenvalue-20261027/implementation-sources-01','nist_seed_ccr_root_matching_20261027/signed-frobenius-20261027/period-eigenvalue-20261027/eco-code-recovery-01','nist_seed_ccr_root_matching_20261027/signed-frobenius-20261027/period-eigenvalue-20261027/eco-code-recovery-01/table-artifacts-01','nist_seed_ccr_root_matching_20261027/signed-frobenius-20261027/period-eigenvalue-20261027/eco-code-recovery-01/degree-routines-01','nist_seed_final_checks_20261028/provenance-refresh-01')

page('13. Prime-order proofs and ECPP','Keep engineering controls separate')
add('All nineteen same-field group orders have retained complete n-1 and n+1 factorizations. For every row, the product of n-1 factors at or below one million is smaller than sqrt(n), so a Pocklington proof using only those small factors is unavailable for every publication and omission. Mixed certificate-cost directions prevent a universal simple preference. This tests a workflow proxy, not the original proof engine.')
add('The November 1997 draft describes probable-prime generation and an optional GKA certificate route. It does not require that every candidate pass one particular ECPP implementation. The recovered ECPP V3.4.1 distribution supplies a concrete finite-search failure path: exhaustion can return a value that its command-line caller labels composite. The package existed by a contemporary 1996 citation, but no artifact proves that Reiter used it.')
add('A static 32-bit compatibility build passes 345 arithmetic comparisons and ordinary correctness controls. An elliptic-curve-only proof for 101 succeeds. With an intentionally empty discriminant catalog and both N+/-1 routes disabled, the same program labels prime 101 composite and exits zero; a missing catalog can instead crash. These are induced source-control outcomes, not observations on an omitted curve order.')
add('The guarded cohort producer/checker implementation went through retained failed mock suites: parsing, identity mapping, JSON serialization and framing problems were fixed through a final nine-method passing mock suite. The archive addendum binds the released artifacts and source custody. The named cohort orders executed in those retained engineering reports remain zero. A ready wrapper, strict admission checker or passed mock suite does not establish the scientific comparison.')
add('The ECPP branch is therefore incomplete at the historical-selection question. A certificate-search mechanism is plausible and executable on controls, but no retained result shows that it rejects exactly the eleven omitted orders and accepts the ten publications under an authenticated original configuration. This report does not launch that cohort experiment or imply that its approvals exist.')
refs('nist_seed_order_certificate_20261023','nist_seed_1997_selection_extension_20261023','nist_seed_ecpp_source_20261024','nist_seed_ecpp_compat_20261024','nist_seed_ecpp_compat_20261024/implementation-followup-20261024/final-v9','nist_seed_ecpp_compat_20261024/implementation-followup-20261024/archive-addendum')

page('14. Search extent, failures and uncertainty','A finite search is not historical reconstruction')
add('The generator-extension study scans six additional slices of 1,024 blocks after the final published positions, separately from a 65,536-state P-256 coefficient-screen shard. These populations overlap in possible representations and are not additive counts of unique curves. The orbit shard applies a coefficient-root screen, not point counting or a weak-curve test. It is not an exhaustive search of the full 2^46 strict candidate-start space.')
add('Under the strict twenty-draw block model, stepping by twenty in a full-period 48-bit recurrence gives 2^46 candidate-start states. Allowing arbitrary shifts gives a different ceiling. Neither bound includes unrestricted changes to the field, seed-generation algorithm or undisclosed arithmetic route. These bounds do not reveal the number of historical runs or establish a hidden weakness.')
add('The broader exploratory feature and root/splitting screens are documented in the source catalog. Many overlap algebraically: trace, discriminant, power residues, local splitting and class-group features are correlated. Repeated nulls do not become independent evidence merely because several reports display them. Conversely, searching many thresholds and Boolean combinations makes exact in-sample fits easier to obtain.')
add('Failures remain observations: the early twist factorization timeout was later resolved; FreeLIP builds initially failed before cohort calls; the base-point prefix build hit a watchdog before a portable build succeeded; ECPP mock suites failed before final engineering acceptance; SEA observers encountered missing tables and exceptional-control aborts; CCR attempts retained partial cells before a corrected run completed. The final fixed pass also retains a control-only GP precedence error repaired before its single cohort invocation.')
add('Independent arithmetic checks are distinguished from independent software lineage. Sage and GP can share PARI internals. A separate Python group-law verifier strengthens order certification, but a modern library still does not become the historical implementation. Archive bytes, compiler flags, data tables, exact input identity, call framing, and caller behavior are separate provenance requirements.')
refs('nist_seed_exhaustive_20261016','nist_seed_selection_hypotheses_20261022','nist_seed_commonality_20261023','nist_seed_freelip_primality_20261023','nist_seed_freelip_prefix_20261024','nist_seed_final_checks_20261028')

page('15. The final fixed 21-curve pass','User-directed stopping boundary')
add('The closing instruction was to run the twist/b-root and MOV/anomalous/order checks once against all 21 curves without retuning, then stop further class-group, isogeny and predicate-library rounds. The retained run has one fresh PARI cohort invocation, zero retries, and a separate Python verifier. It certifies the original curve, opposite-b model and true nonsquare twist for each row: 63 curve-order certificates and 63 point witnesses.')
table(['Fixed property','Published true','Omitted true'],[
['Field/order primality, nonsingularity, seed relation','10/10','11/11'],
['Original order certified; non-anomalous; order bit cap','10/10','11/11'],
['MOV passes through 20 and through 100','10/10','11/11'],
['Lower-valued b root','5/10','6/11'],
['Even b root','6/10','6/11'],
['p=3 mod 4 exponent root (where applicable)','9/9','8/8'],
['Opposite-b order prime','2/10','3/11'],
['Opposite-b order equals original order','1/10','3/11'],
['True quadratic-twist order prime','1/10','0/11'],
['Largest twist prime passes MOV 20 and 100','10/10','11/11']],[WIDTH-160,80,80])
add('The exponent-root row is not applicable to four P-224 rows. The opposite-b equality row likewise reflects those four isomorphic models. No fixed flag or its complement is a perfect separator, and no combinations were searched in this closing pass. Imported complete twist factorizations were rigorously checked; no new factorization or SEA count was needed.')
add('The order witness method verifies exact point order and that the Hasse interval contains a unique multiple of that order. The Python verifier checks every retained witness, factor-wise minimality and the Hasse uniqueness condition. The MOV no-hit result proves absence only in the stated range; the older nineteen-row exact embedding-degree result is a separate stronger calculation.')
add('<b>Closing interpretation:</b> these checks do not identify the historical rule. Finite null tests do not prove that no possible arithmetic criterion exists. The work stops short of claiming that the selection process was purely non-arithmetic.')
refs('nist_seed_final_checks_20261028','nist_seed_exact_embedding_degree_20261023')

page('16. Mattsson comparison and publication','Independent data reconciliation, not original source')
add('Mattsson\'s table states it was generated by Claude on 18 October 2026. The November 6 refresh downloads its commit-pinned and moving-main copies; both are 37,225 bytes with SHA-256 9fd4cf9a99482e44e7207b59aa831c58cec15682582a2932b65c04b3c6bc915c. An October 24 comparison already existed; the refresh replays it and binds all rows to the canonical 21-row record.')
add('All nineteen seeds, ordinals, fields, a coefficients, c parameters, orders and signed traces match. Eighteen b coefficients match exactly. Published P-224 uses the opposite isomorphic sign; the retained explicit u witness verifies u^4=1 and b*u^6=-b mod p, giving (x,y) -> (u^2*x,u^3*y). The table covers all eleven omissions and eight publications, omitting published P-384 and P-521.')
add('Every below-100 prime list agrees after recognizing that the external “Elkies” category includes ramified primes. There are 31 such entries across sixteen curves. Recomputing the retained strict signatures checks 3,173 Legendre symbols. The displayed literal threshold reproduces fifteen cutoffs, while the previously documented integer convention reproduces nineteen.')
table(['Curve','Reported','Literal formula'],[['Omitted 239 / 36','179','181'],['Omitted 239 / 2682','157','179'],['Omitted 192 / 2198','149','163'],['prime239v2','191','197']],[WIDTH-150,75,75])
add('The external formula is M>2^(L/2+2), while the exact output reconstruction uses M>2^(((L-1)//2)+2), including ramified primes. Our strict archive uses only +1 primes and M^2>16p. The generating code was not found in Mattsson\'s repository, so the reconstructed integer convention is not attributed as verified author code.')
add('Follow-up PR #3129 publishes eight comparison artifacts at commit 134317a08335f64746eef21d507fd2219f213c45. All 22 hosted checks pass at the last verified observation; the PR remains open and unmerged then. Conductor claim T-5773 was released after recording that inherited Go checks belonged to its configured project rather than this Python artifact. Neither publication nor green CI resolves the historical criterion.')
refs('nist_seed_mattsson_comparison_20261106','nist_seed_1997_selection_extension_20261023/external_crosscheck')

page('17. What is established, and what is missing','Final assessment')
add('<b>Established:</b> exact regeneration of the ten published prime-field seed bytes; exact identity and order evidence for the fixed cohort; numerous scoped arithmetic counterexamples; actual historical standards and library-source findings; bounded configured-software behavior; a preserved P-224 lead and an exploratory all-label fit; and a reconciled public nineteen-curve table.')
add('<b>Not established:</b> that the original program visited all eleven reconstructed omissions; that it rejected them for weakness; that the prime-199 fit or a cube-root condition was used; that any particular recovered ECPP, FreeLIP, NTL or later LiDIA build was the NIST generator; or that the investigation has recovered the historically used criteria.')
add('The main missing artifact is the original acceptance path: candidate visitation, validation calls, RNG ownership, proof/counting routines, resource limits, error handling and any human review. A run log or independently documented rule tied to exact candidates could be equally decisive. An earlier draft may constrain chronology, but a parameter table alone does not explain a rejection.')
add('An arithmetic classifier would need a fixed, independently motivated rule, all-eleven/all-ten verification without label-dependent changes, and preferably a held-out historical prediction. Even that would require provenance before being called the actual 1997-98 mechanism. The user has closed further predicate searching; this PDF performs no new scientific search.')
h('Corrections carried into this synthesis')
add('The November 1997 draft is recovered, superseding older missing-draft notes. The conductor-three case in the exact same-field census is published P-224; both P-256 Frobenius conductors are one. The class-number source audit\'s initially unperformed stronger test is superseded by the nineteen certified field results, with two published unknowns retained. The Mattsson reconciliation is a replay of an existing comparison plus a fresh canonical identity binding, not the first analysis of that table.')
add('<b>Historical criterion: UNRESOLVED.</b> The overall goal was marked blocked after repeated checks found no new original acceptance evidence. The completed comparison, publication and CI work are narrower finished deliverables; they do not substitute for the original objective.')
add('The following appendices preserve the breadth of the search without treating every earlier report\'s prospective next step or administrative status as current. The source manifest and source-report bundle are embedded in this PDF for inspection offline. The exact curve JSON is also embedded.')
refs('nist_seed_final_checks_20261028','nist_seed_1997_original_draft_20261023','nist_seed_exact_conductor_census_20261023','nist_seed_class_number_dated_bound_20261028/certificate-report-01','nist_seed_mattsson_comparison_20261106')

# Appendix A: every retained report, clearly marked historical and potentially superseded.
for start in range(0,len(sources),5):
 page('Appendix A. Evidence catalog',f'Entries {start+1}-{min(start+5,len(sources))} of {len(sources)}')
 add('Archival opening synopses below preserve each report\'s original scope. Earlier availability, planned-work and status statements may be superseded by the main narrative. These are internal research records, not authenticated original generator logs.','SmallX')
 for source in sources[start:start+5]:
  key=str(source.relative_to(R)); text=source.read_text();title=text.splitlines()[0].lstrip('# ').strip()
  h(ids[key]+' | '+html.escape(clean(title)))
  add(ref(key)+' '+html.escape(key),'SmallX')
  body=re.split(r'\n## ',text,1)[0]
  body=' '.join(body.splitlines()[1:]).strip()
  body=re.sub(r'!\[[^\]]*\]\([^)]*\)','',body)
  body=re.sub(r'\[([^\]]+)\]\([^)]*\)',r'\1',body)
  body=re.sub(r'[`*#]','',body)
  words=body.split(); synopsis=' '.join(words[:75])+(' ...' if len(words)>75 else '')
  add(html.escape(clean(synopsis)),'SmallX')

# Appendix B: exact values and complete seed/UID; three records per page.
for start in range(0,len(cohort),3):
 page('Appendix B. Exact curve records',f'Rows {start+1}-{min(start+3,len(cohort))} of 21')
 add('Canonical a=-3 short-Weierstrass model. All numerical field/model/order values below are hexadecimal. c is the SHA-derived parameter; t=p+1-n is the trace. Values are from the frozen cohort, not recomputed point counts.','SmallX')
 for c in cohort[start:start+3]:
  h(f"{int(c['p']).bit_length()} bits | block {c['ordinal']} | {c['name']} | {c['label']}")
  vals=[('stream',str(c['timestamp'])),('seed',c['seed_hex']),('UID',c['curve_uid'])]+[(k,format(int(c[k]),'x')) for k in ('p','b','c','n')]
  for label,value in vals:
   chunks=[value[i:i+76] for i in range(0,len(value),76)]
   add('<b>'+label+':</b> '+('<br/>'+(' '*6)).join(html.escape(v) for v in chunks),'CodeX')
  story.append(Spacer(1,9))

page('Appendix C. Primary-source reading map','Selected external documents')
primary=[
('Seed reconstruction disclosure','https://words.filippo.io/seeds-solved/','Six streams, published positions, eleven other qualifying windows; missing selection explanation.'),
('Anthropic primary writeup','https://www.anthropic.com/research/ecdsa-curve-origins','Reconstructed seed bytes and base-point recipes; open questions and limits on counting runs.'),
('17 November 1997 X9.62 draft','https://archive.org/download/x962-11-17-97/x962-11-17-97.pdf','Retrieved full draft. Numerical generation procedure and seven published prime-field examples.'),
('20 September 1998-cover X9.62 text','https://safecurves.cr.yp.to/grouper.ieee.org/groups/1363/private/x9-62-09-20-98.pdf','Later generation and validation text; printed rounding differs from the 1997 draft.'),
('Schoof 1995','https://www.numdam.org/article/JTNB_1995__7_1_219_0.pdf','Point-counting framework and split/nonsplit information; not the original generator.'),
('Morain 1995','https://www.numdam.org/article/JTNB_1995__7_1_255_0.pdf','Practical point counting and the CCR coefficient-conversion correction.'),
('Lehmann 1994 archived thesis','https://web.archive.org/web/19970731071932id_/http://www.cs.uni-sb.de:80/users/mdenny/Bewohner/lehmann/lehmann.diplom.ps','Modular-polynomial construction, interface and printed ell=5 witness.'),
('SEC 1 version 2','https://www.secg.org/sec1-v2.pdf','Later documentation of the MOV-bound increase from 20 to 100.'),
('Baier 2002 thesis','https://d-nb.info/964515040/34','Dated account of the CM class-number lower-bound advice.'),
('ETSI TS 102 176-1, July 2005','https://www.etsi.org/deliver/etsi_ts/102100_102199/10217601/01.02.01_60/ts_10217601v010201p.pdf','Dated maximal-order class-number and operational ideal-class guidance.'),
('RFC 5639, March 2010','https://www.rfc-editor.org/rfc/rfc5639.html','Later h(O_K)>10^7 requirement; no evidence of 1997 NIST adoption.'),
('Mattsson commit-pinned table','https://github.com/emanjon/share/blob/6279fab0416e756998f0de6fcb0ccb473815127b/ecdsa_skipped_curves.txt','Modern 19-curve computation. Exact identity and SEA-convention reconciliation in R catalog.'),
]
for title,url,desc in primary:
 add(f'<b>{html.escape(title)}</b> - {html.escape(desc)}','SmallX')
 add(f'<link color="#006D77" href="{html.escape(url,quote=True)}">{html.escape(url)}</link>','SmallX')

page('Appendix D. Reproduction and custody','What this PDF contains')
add('The source-manifest.json attachment records the source path and SHA-256 for every cataloged report. The source-report-bundle.zip attachment contains those internal Markdown reports plus the exact curve JSON, the final fixed-pass verification record, the Mattsson comparison JSON and the source manifest. The bundle does not redistribute the third-party thesis, standards PDFs, executable binaries or private source archives.')
add('To inspect the Mattsson comparison, use research/nist_seed_mattsson_comparison_20261106/report.md and compare.py at commit 134317a08335f64746eef21d507fd2219f213c45. The report distinguishes the literal external cutoff, the integer output reconstruction, and the retained strict cutoff. The full historical investigation remains distinct from this comparison\'s validation.')
add('To audit the closing pass, use research/nist_seed_final_checks_20261028/VERIFICATION.json, its report, FROZEN.json, INPUTS.json, and the retained runs/final-01 records. The verifier reports 63 certificates, 63 witnesses, 21 rows, one fresh cohort invocation and zero retries. Other report-specific archives and controls are located through the catalog links.')
add('This synthesis is a document-production operation. It reads existing results, checks the stated population counts and constructs tables; it starts no point-counting, factorization, class-group, predicate-search, native historical-code or ECPP cohort trial. Internal source dates may be UTC while this cover uses the client date in America/Los_Angeles.')
add('The report is not a claim that all untested arithmetic rules are impossible. It is not a claim that every omitted window was historically visited. It does not infer a weakness from a missing record. The evidence needed to settle the central question remains an authenticated acceptance mechanism or equivalent direct historical record explaining the actual choices.')
h('Record identifiers')
add('Canonical cohort SHA-256: '+manifest['cohort_sha256'],'CodeX')
add('Historical investigation source snapshot: '+manifest['source_snapshot_commit'],'CodeX')
add('Mattsson publication commit: '+manifest['mattsson_commit'],'CodeX')
add('Final assessment: historical selection criterion UNRESOLVED.','H2X')

class ReportDoc(SimpleDocTemplate):
 def afterFlowable(self,f):
  if hasattr(f,'_section'):
   k=slug(f._section)+'-'+str(self.page); self.canv.bookmarkPage(k);self.canv.addOutlineEntry(f._section,k,0,False)

def footer(c,doc):
 c.saveState();c.setStrokeColor(colors.HexColor('#CAD5DF'));c.setLineWidth(.5);c.line(47,41,W-47,41)
 c.setFont('Body',7.5);c.setFillColor(GRAY);c.drawString(47,28,'NIST / ANSI SEED-SELECTION SEARCH | Historical criterion unresolved')
 c.drawRightString(W-47,28,str(doc.page))
 if doc.page>1:
  c.setFont('Body',7.5);c.drawString(47,H-29,'COMPREHENSIVE RESEARCH RECORD');c.drawRightString(W-47,H-29,'6 NOVEMBER 2026')
 c.restoreState()
raw=O/'tmp/pdfs/report-unattached.pdf'
doc=ReportDoc(str(raw),pagesize=A4,rightMargin=47,leftMargin=47,topMargin=53,bottomMargin=56,title='NIST / ANSI seed-selection search - comprehensive report',author='Research synthesis',subject='Historical selection criterion unresolved; fixed cohort and source-bound investigations')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
# Embed the report sources and exact row identities in the final self-contained PDF.
zbuf=io.BytesIO()
with zipfile.ZipFile(zbuf,'w',zipfile.ZIP_DEFLATED) as z:
 def put(name,data):
  info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,data)
 for s in sources:put(str(s.relative_to(R)),s.read_bytes())
 put('source-manifest.json',(O/'source-manifest.json').read_bytes())
 put('cohort.json',(O/'cohort.json').read_bytes())
 put('final-pass-verification.json',json.dumps(final,indent=2))
 put('mattsson-comparison.json',json.dumps(matt,indent=2))
w=PdfWriter();w.clone_document_from_reader(PdfReader(str(raw)))
w.add_attachment('source-manifest.json',(O/'source-manifest.json').read_bytes())
w.add_attachment('cohort.json',(O/'cohort.json').read_bytes())
w.add_attachment('source-report-bundle.zip',zbuf.getvalue())
with OUT.open('wb') as f:w.write(f)
r=PdfReader(str(OUT));text='\n'.join(x.extract_text() or '' for x in r.pages)
assert len(r.pages)>20 and 'Historical criterion' in text and 'UNRESOLVED' in text
assert all(c['seed_hex'] in text for c in cohort)
assert len(r.attachments)==3
v={'pages':len(r.pages),'sources':len(sources),'cohort_rows':len(cohort),'omitted':11,'published':10,'attachments':list(r.attachments),'all_seeds_present':True,'pdf_sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'pdf_bytes':OUT.stat().st_size,'output':'output/pdf/nist-seed-selection-search-comprehensive-report.pdf','new_scientific_trials':0}
(O/'validation.json').write_text(json.dumps(v,indent=2)+'\n')
print(json.dumps(v,indent=2))
_source_tmp.cleanup()
