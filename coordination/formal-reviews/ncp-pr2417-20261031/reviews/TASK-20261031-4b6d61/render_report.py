#!/usr/bin/env python3
"""Render this review and its source/control scope diagram with system LaTeX."""
from pathlib import Path
import re
import subprocess
import json
import gzip
ROOT = Path(__file__).resolve().parent

def escape(s):
    table={'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}','•':r'$\cdot$','–':'--','—':'---','−':'-','’':"'",'“':'``','”':"''"}
    return ''.join(table.get(ch,ch) for ch in s)

def code(s):
    if re.fullmatch('[0-9a-f]{40,64}',s):
        return r'\texttt{'+r'\allowbreak{}'.join(s[i:i+8] for i in range(0,len(s),8))+'}'
    parts=re.split(r'([/_.-])',s)
    return r'\texttt{'+r'\allowbreak{}'.join(escape(p) for p in parts)+'}'

def inline(s):
    chunks=re.split(r'(`[^`]+`|\*\*[^*]+\*\*|\[[^]]+\]\([^)]+\))',s)
    out=[]
    for p in chunks:
        if p.startswith('`') and p.endswith('`'): out.append(code(p[1:-1]))
        elif p.startswith('**') and p.endswith('**'): out.append(r'\textbf{'+escape(p[2:-2])+'}')
        elif re.fullmatch(r'\[[^]]+\]\([^)]+\)',p):
            m=re.match(r'\[([^]]+)\]\(([^)]+)\)',p); out.append(r'\href{'+m[2]+'}{'+escape(m[1])+'}')
        else: out.append(escape(p))
    return ''.join(out)

lines=(ROOT/'review.md').read_text().splitlines(); body=[]; i=0
while i<len(lines):
    line=lines[i]
    if line.startswith('|'):
        rows=[]
        while i<len(lines) and lines[i].startswith('|'):
            cells=[c.strip() for c in lines[i].strip('|').split('|')]
            if not all(re.fullmatch(r'[-: ]+',c) for c in cells): rows.append(cells)
            i+=1
        n=len(rows[0]); widths={2:[.39,.55],3:[.27,.30,.35]}[n]
        body += [r'\small\begin{longtable}{'+''.join('>{\\raggedright\\arraybackslash}p{'+str(w)+r'\linewidth}' for w in widths)+'}',r'\hline']
        for j,row in enumerate(rows):
            body.append(' & '.join(inline(c) for c in row)+r' \\ '+(r'\hline' if j==0 else ''))
        body += [r'\hline\end{longtable}\normalsize']; continue
    if line.startswith('```'):
        i+=1; b=[]
        while i<len(lines) and not lines[i].startswith('```'): b.append(lines[i]); i+=1
        body.append(r'\begin{quote}\small '+code(' '.join(b))+r'\end{quote}')
    elif line.startswith('# '): body.append(r'\section*{'+escape(line[2:])+'}')
    elif line.startswith('## '): body.append(r'\subsection*{'+escape(line[3:])+'}')
    elif not line.strip(): body.append('\n')
    else: body.append(inline(line))
    i+=1
preamble=r'''\documentclass[10pt]{article}
\usepackage[margin=0.7in]{geometry}
\usepackage[T1]{fontenc}
\usepackage{longtable,array,hyperref}
\hypersetup{colorlinks=true,urlcolor=blue}
\setlength{\parindent}{0pt}
\setlength{\parskip}{5pt}
\setlength{\tabcolsep}{4pt}
\renewcommand{\arraystretch}{1.18}
\sloppy
\begin{document}
'''
diagram=r'''\subsection*{Scope diagram}
\begin{center}
\fbox{\parbox{0.83\linewidth}{\centering
Pinned source signatures and definitions\\
Chronological action; integer signed counts\\
$\downarrow$\\
Canonical cyclic map $\mathrm{encode}_P : \mathbb{Z}/n \to A$\\
Well-defined when $nP=0$; injective when $\mathrm{ord}(P)=n$\\
$\downarrow$\\
Independent exact controls: 2,115 positive finite cases\\
Zero-generator control rejects removing the order hypothesis\\[5pt]
\textbf{Source fidelity: faithful at the scoped abstract level}\\
\textbf{Fresh Lean replay: not verified in this task}\\[5pt]
Concrete curve operations, generator order, and parser refinement\\
remain separately named application obligations.
}}
\end{center}
'''
diagram=diagram.replace(r'\mathbb{Z}',r'\mathbf{Z}')
tex = preamble+'\n'.join(body)+diagram+'\n\\end{document}\n'
(ROOT/'report.tex').write_text('\n'.join(line.rstrip() for line in tex.splitlines())+'\n')
svg='''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="600" viewBox="0 0 1000 600"><rect width="1000" height="600" fill="#f8fafc"/><style>text{font-family:Arial,sans-serif;fill:#172033} .box{fill:white;stroke:#45657c;stroke-width:2} .h{font-size:23px;font-weight:bold}.s{font-size:19px}</style><text x="35" y="42" class="h">J1 point action and canonical encoding</text><text x="35" y="74" class="s">TASK-20261031-4b6d61 | producer f4330e1a29fe</text><rect class="box" x="45" y="100" width="910" height="85" rx="8"/><text x="65" y="132" class="h">Pinned source signatures</text><text x="65" y="164" class="s">Chronological action and right-negation signed counts agree with Lemma 1</text><path d="M500 185v28" stroke="#45657c" stroke-width="3"/><rect class="box" x="45" y="215" width="910" height="95" rx="8"/><text x="65" y="248" class="h">Canonical encoding: scalar multiplication by P</text><text x="65" y="281" class="s">nP = 0 defines the map; exact order ord(P) = n gives injectivity</text><path d="M500 310v28" stroke="#45657c" stroke-width="3"/><rect class="box" x="45" y="340" width="910" height="90" rx="8"/><text x="65" y="373" class="h">Exact controls: 2,115 finite cases pass</text><text x="65" y="406" class="s">P = 0 in Z/2 rejects removing the exact-order hypothesis</text><rect x="45" y="455" width="440" height="90" rx="8" fill="#dcfce7" stroke="#457559"/><text x="65" y="488" class="h">Source fidelity: faithful scoped</text><text x="65" y="519" class="s">Abstract additive groups</text><rect x="515" y="455" width="440" height="90" rx="8" fill="#fef3c7" stroke="#967e40"/><text x="535" y="488" class="h">Lean replay: not verified</text><text x="535" y="519" class="s">Separate owned machine lane</text><text x="45" y="579" class="s">Concrete curve operations and parser refinement remain application obligations.</text></svg>'''
(ROOT/'diagram.svg').write_text(svg+'\n')
cmd=['pdflatex','-interaction=nonstopmode','-halt-on-error','-output-directory',str(ROOT/'raw'),'report.tex']
r=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
(ROOT/'raw/pdf-render.stdout').write_text(r.stdout);(ROOT/'raw/pdf-render.stderr').write_text(r.stderr)
(ROOT/'raw/pdf-render-command.json').write_text(json.dumps({'command':cmd,'exit_code':r.returncode},indent=2)+'\n')
if r.returncode: raise SystemExit(r.returncode)
(ROOT/'report.pdf').write_bytes((ROOT/'raw/report.pdf').read_bytes())
(ROOT/'raw/report.pdf').unlink()
log=ROOT/'raw/report.log'
(ROOT/'raw/report.log.gz').write_bytes(gzip.compress(log.read_bytes(),mtime=0))
log.unlink()
for suffix in ['aux','out']:
    f=ROOT/('raw/report.'+suffix)
    if f.exists(): f.unlink()
print('Rendered report.pdf')
