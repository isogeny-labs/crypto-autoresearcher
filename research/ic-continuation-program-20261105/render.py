"""Render the plan, not experimental results."""
from pathlib import Path
import json,html
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Image,PageBreak
from reportlab.lib.styles import getSampleStyleSheet

root=Path(__file__).resolve().parent
p=json.loads((root/'program.json').read_text())
fig,ax=plt.subplots(figsize=(11,5));ax.set_xlim(0,10);ax.set_ylim(0,5);ax.axis('off')
nodes={'B0':(1,3.5),'L1':(3,4.3),'C2':(3,3.4),'F3':(3,2.5),'S4':(5.2,3.5),
       'K8':(1,1.4),'H6':(3,1.4),'R7':(5.2,1.4),'M9':(7.4,1.4),'E5':(7.4,4.1),'P10':(9,2.8)}
for t in p['workstreams']:
 x,y=nodes[t['id']];ax.text(x,y,t['id']+'\n'+t['title'].replace(' ', '\n',1),ha='center',va='center',fontsize=8,
 bbox=dict(boxstyle='round,pad=.5',facecolor='#e4eff7',edgecolor='#416c8c'))
 for dep in t['dependencies']:
  a,b=nodes[dep];ax.annotate('',xy=(x-.6,y),xytext=(a+.6,b),arrowprops=dict(arrowstyle='->',color='#416c8c'))
ax.text(5,.45,'Proposal only: all experiments await existing admission, checkpoint custody and owner-lane checks.',ha='center',fontsize=10)
ax.set_title('IC continuation: dependencies and distinct research tracks (no experiments launched)')
fig.tight_layout();fig.savefig(root/'program.svg');fig.savefig(root/'program.png',dpi=160);plt.close(fig)
svg=root/'program.svg';svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
styles=getSampleStyleSheet();styles['BodyText'].fontSize=9;styles['BodyText'].leading=12
story=[Paragraph('Index-calculus continuation program',styles['Title']),Paragraph('5 November 2026 — preparation bundle, not scientific admission',styles['Heading2']),
 Paragraph('All requested mechanisms have a concrete source-bound next step. The bundle does not create experiment approval, dispatch jobs, change official research status, or establish an impossibility theorem. Implementation and written derivations are producer assertions [pcc:unverified].',styles['BodyText']),Spacer(1,10),Image(str(root/'program.png'),width=490,height=223)]
def para(label,text):
 story.append(Paragraph('<b>'+html.escape(label)+':</b> '+html.escape(text),styles['BodyText']));story.append(Spacer(1,5))
para('Proposed order','Reconcile B0; then at most two critical slots for F3 complete trace costs and L1 held-out learned bases. Resume K8 only in its owned lane and original protocol. E5 source review and P10 proof preparation proceed without experimental launches.')
para('Admission','The WIP gate reports 91/12 open PRs and refuses expansion. Checkpoint upload access is absent. A scoped WIP exception was requested; no exception is assumed. No new cloud expenditure or resource expansion is authorized here.')
para('Measurement','Cold one-target total includes construction, selection/training, failed queries, root discovery, signed/subgroup validation, independent rank, linear algebra, descent and verification. Reused-setup batches are separate. Counted work and isolated wall time are separate metrics.')
for t in p['workstreams']:
 story.append(Paragraph(t['id']+' — '+t['title'],styles['Heading2']))
 para('Question',t['question']);para('Next step',t['next_step']);para('Controls','; '.join(t['controls']));para('Scale',t['scaling']);para('Deliverables','; '.join(t['deliverables']));para('If favorable',t['outcomes']['positive']);para('If null',t['outcomes']['null'])
story.append(Spacer(1,12));story.append(Paragraph('What a no-go theorem would require',styles['Heading1']))
for title,text in [
 ('Define the theorem','Specify curve/subgroup family, target distribution, algorithm and presentation class, success probability, preprocessing/advice, memory, cost model, uniformity and asymptotic quantifiers. “Never finds a relation” is false; “never beats rho in this model” is a possible scoped target.'),
 ('First written counting result','For a finite group H and ordered m-tuples from a base F, sum_R N_m(R)=|F|^m. Hence uniform-target success probability is at most min(1,|F|^m/|H|). This does not prove uniform coverage or independent row rank.'),
 ('Restricted collection floor','With iid uniform queries, at least K successes needed, setup A, and a per-query lower bound c0, expected work is at least A+c0*K*|H|/min(|H|,|F|^m). The query/rank/cost assumptions must be proved for the actual algorithm. Adaptive policies and amortized tables require separate arguments.'),
 ('Membership lemma','A nonzero univariate polynomial vanishing on B distinct field elements has degree at least B. Auxiliary-variable systems and towers remain outside this statement; PKM2016 explicitly uses that escape.'),
 ('Substantial missing bridge','A solver-family theorem must establish an unavoidable charged-resource lower bound for every allowed parameter choice, then justify its probability over target instances. Degree lower bounds do not automatically imply runtime lower bounds; a finite fitted slope is not an asymptotic proof.'),
 ('Countercontrols','Keep coordinate-aware algorithms outside generic-group conclusions; audit pulled-back degrees for large multipliers; do not infer k-SUM hardness from random-looking statistics. Test weak curves, alternate solvers and extended membership formulations against every proposed theorem.'),
 ('Formalization and review','The readable statements, exact hypotheses and countermodels are in PROOF_PROGRAM.md. Finite Python development checks are supplied. Lean formalization, axiom audit, the algorithm bridge and independent proof review remain uncompleted; no universal theorem is asserted.')]:
 para(title,text)
story.append(Paragraph('Pinned source index',styles['Heading1']))
for s in p['source_lock']:
 para(s['id'],s['repository']+' @ '+s['commit'][:12]+' / '+s['path'])
 story.append(Paragraph('<link href="'+s['url']+'" color="blue">Open immutable source</link>',styles['BodyText']))
para('Primary literature','PKM2016 primary construction and experimental conclusions were read. Zhang-Liu ePrint 2018/795 PDF request returned HTTP 403; the actual received-word construction remains unread.')
para('Graphs','This is a planning diagram. No measured research graph or leaderboard is modified, because there is no new independently verified scientific result.')
SimpleDocTemplate(str(root/'report.pdf'),leftMargin=42,rightMargin=42,topMargin=40,bottomMargin=40).build(story)
print('Rendered report.pdf and program.svg')
