"""Rebuild the manuscript's exact mechanism diagrams and domain study figure.

Only the domain study plot consumes measurements; its source is a current,
version-bound result, not an inferred benchmark or an illustrative data set.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Polygon
from matplotlib import font_manager

ROOT = Path(__file__).resolve().parents[1]
DOMAIN_SOURCE = ROOT/'data/domain-study/summary.json'

def publication_font_family():
    for candidate in ('Linux Libertine O', 'Linux Libertine', 'Libertinus Serif', 'Liberation Serif'):
        try:
            path = font_manager.findfont(candidate, fallback_to_default=False)
        except ValueError:
            continue
        return font_manager.FontProperties(fname=path).get_name()
    return 'DejaVu Serif'

plt.rcParams.update({'font.family':publication_font_family(), 'font.size':10,
    'pdf.fonttype':42, 'ps.fonttype':42, 'mathtext.fontset':'stix',
    'axes.linewidth':0.7, 'savefig.facecolor':'white'})
INK='#192b36'; BLUE='#1d5268'; PALE='#eef4f6'; RED='#8e3c31'; GRAY='#57636b'

def box(ax,x,y,w,h,title,body='',fc=PALE,ec=BLUE,size=10):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.008,rounding_size=0.012',
        linewidth=.9,facecolor=fc,edgecolor=ec))
    if body:
        ax.text(x+w/2,y+h-.034,title,ha='center',va='top',color=ec,weight='bold',fontsize=size)
        ax.text(x+w/2,y+.026,body,ha='center',va='bottom',color=INK,fontsize=size-0.5,linespacing=1.25)
    else: ax.text(x+w/2,y+h/2,title,ha='center',va='center',color=ec,fontsize=size,weight='bold')

def arrow(ax,start,end,label=None,dashed=False,color=BLUE,rad=0):
    ax.add_patch(FancyArrowPatch(start,end,arrowstyle='-|>',mutation_scale=9,
        color=color,linewidth=.95,linestyle='--' if dashed else '-',
        connectionstyle=f'arc3,rad={rad}',shrinkA=2,shrinkB=2))
    if label:
        mx=(start[0]+end[0])/2;my=(start[1]+end[1])/2
        ax.text(mx+.008,my+.008,label,fontsize=9,color=color,ha='left',va='bottom',
            bbox={'facecolor':'white','edgecolor':'none','pad':.5})

def save(fig,path):
    fig.savefig(path,bbox_inches='tight',pad_inches=.035,metadata={'CreationDate':None,'ModDate':None})
    plt.close(fig)

def overview(out):
    fig,ax=plt.subplots(figsize=(7.05,4.65));ax.set(xlim=(0,1),ylim=(-.07,1));ax.axis('off')
    box(ax,.01,.765,.42,.21,'Receiver-owned request',
        'Original P   Candidate Q   Reference T\nSelector R   Ordered D (M inputs)',size=10.5)
    box(ax,.57,.805,.41,.17,'Untrusted producer',
        'Full vectors  or  one claimed violation',fc='white',ec=GRAY,size=10.5)
    box(ax,.01,.49,.42,.205,'Independent reconstruction',
        'Source parser → typed DAG (N nodes)\nDefinedness   Repair   Preservation',size=10.5)
    arrow(ax,(.22,.765),(.22,.695))
    box(ax,.57,.49,.41,.205,'Packet bindings',
        'Request · source · order · domain\nStrict schema and integrity checks',size=10.5)
    arrow(ax,(.775,.805),(.775,.695),dashed=True,color=GRAY)
    arrow(ax,(.43,.592),(.57,.592))
    # Three output contracts align vertically with their evaluator below.
    xs=[.01,.35,.69];w=.29
    for x,title,body in [
        (xs[0],'Pruned direct (no packet)','L nodes: obligations + trace\nL × M cells (L ≤ N)'),
        (xs[1],'Full-vector check','Exact topology + roots\nCompute / compare N × M'),
        (xs[2],'Compact refutation','One supplied (j, u, trace)\nEvaluate N values at u')]:
        box(ax,x,.205,w,.19,title,body,size=9.8)
    arrow(ax,(.16,.49),(.155,.395))
    arrow(ax,(.64,.49),(.495,.395))
    arrow(ax,(.875,.49),(.835,.395))
    box(ax,.01,.025,.63,.10,'ACCEPT  or  canonical REFUTED',fc='white',size=10.1)
    box(ax,.69,.025,.29,.10,'REFUTED at supplied point',fc='white',size=9.4)
    arrow(ax,(.155,.205),(.155,.125));arrow(ax,(.495,.205),(.495,.125));arrow(ax,(.835,.205),(.835,.125))
    ax.text(.5,-.038,'Validation failure or interrupted work → no semantic verdict / no approval receipt',
        ha='center',va='center',fontsize=9.8,color=RED,
        bbox={'facecolor':'white','edgecolor':'none','pad':1.5})
    save(fig,out/'repairseal-overview.pdf')

def definedness(out):
    fig,ax=plt.subplots(figsize=(7.05,2.85));ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off')
    box(ax,.01,.60,.34,.34,'Executed candidate at n = 1',
        'scratch = 1u / (n − 1u);\nreturn repaired_value;',size=10.4)
    box(ax,.43,.68,.24,.24,'Total value cell','division by zero -> 0',size=10.3)
    box(ax,.43,.27,.24,.24,'Source flag','n − 1 ≠ 0  is false',fc='#f7eeeb',ec=RED,size=10.3)
    arrow(ax,(.35,.79),(.43,.79));arrow(ax,(.35,.66),(.43,.43),color=RED)
    box(ax,.74,.68,.24,.24,'Local value rule','can pass',size=10.3)
    box(ax,.74,.27,.24,.24,'Definedness root','O₀ = false',fc='#f7eeeb',ec=RED,size=10.3)
    arrow(ax,(.67,.79),(.74,.79));arrow(ax,(.67,.39),(.74,.39),color=RED)
    ax.text(.17,.37,'An unused result\ndoes not erase\nan executed fault.',ha='center',va='center',
        color=INK,fontsize=11,linespacing=1.35)
    arrow(ax,(.86,.27),(.86,.115),color=RED)
    ax.text(.86,.055,'REFUTED',ha='center',va='center',weight='bold',fontsize=11,color=RED)
    save(fig,out/'value-definedness.pdf')

def acceptance_transport(out):
    """Exact illustrative domains; no experimental measurements are plotted."""
    fig,ax=plt.subplots(figsize=(7.05,4.5))
    ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off')
    box(ax,.01,.84,.97,.14,'Receiver-established ACCEPT on D',
        'Same sources, policy, input order, and word semantics',size=10.4)
    ax.text(.235,.786,'(a) Disjoint domains, equal projections',
        ha='center',va='center',fontsize=10.1,weight='bold',color=INK)
    ax.text(.755,.786,'(b) Check coverage for the new request',
        ha='center',va='center',fontsize=10.1,weight='bold',color=INK)

    # The vertical coordinate is z; the globally relevant coordinate is x.
    # Filled circles and open squares remain distinguishable in grayscale.
    ax.plot(.025,.73,'o',ms=5.4,color=INK)
    ax.text(.048,.73,r'$D=\{0,1,2\}\times\{0\}$',
        ha='left',va='center',fontsize=10.6,color=INK)
    ax.plot(.025,.681,'s',ms=6.5,mfc='white',mec=BLUE,mew=1.2)
    ax.text(.048,.681,r'$E=\{0,1,2\}\times\{1,2,3\}$',
        ha='left',va='center',fontsize=10.6,color=INK)
    xs=[.13,.25,.37]; zs=[.32,.41,.50,.59]
    ax.add_patch(Rectangle((.107,.371),.287,.258,facecolor=PALE,edgecolor='none'))
    for y in zs:
        ax.plot([.10,.40],[y,y],color='#cbd4d9',lw=.55,zorder=0)
    for x in xs:
        ax.plot([x,x],[.31,.61],color='#cbd4d9',lw=.55,zorder=0)
        ax.plot(x,zs[0],'o',ms=5.4,color=INK,zorder=3)
        for z in zs[1:]:
            ax.plot(x,z,'s',ms=6.5,mfc='white',mec=BLUE,mew=1.2,zorder=3)
        arrow(ax,(x,.302),(x,.205),dashed=True,color=GRAY)
        ax.plot(x,.187,'s',ms=8,mfc='white',mec=BLUE,mew=1.0,zorder=3)
        ax.plot(x,.187,'o',ms=3.6,color=INK,zorder=4)
    arrow(ax,(.087,.285),(.418,.285),color=GRAY)
    arrow(ax,(.087,.285),(.087,.634),color=GRAY)
    for index,y in enumerate(zs):
        ax.text(.068,y,str(index),ha='right',va='center',fontsize=9.7,color=INK)
    for index,x in enumerate(xs):
        ax.text(x,.144,str(index),ha='center',va='center',fontsize=9.8,color=INK)
    ax.text(.437,.285,'x',ha='center',va='center',fontsize=10.6,fontstyle='italic',color=INK)
    ax.text(.072,.648,'z',ha='center',va='center',fontsize=10.6,fontstyle='italic',color=INK)
    ax.text(.25,.094,r'$\pi_x(D)=\pi_x(E)=\{0,1,2\}$',
        ha='center',va='center',fontsize=10.3,color=INK)
    ax.text(.25,.047,r'$D\cap E=\varnothing$',
        ha='center',va='center',fontsize=10.2,color=INK)

    ax.text(.755,.719,'Global obligation support',ha='center',va='center',
        fontsize=10.1,weight='bold',color=INK)
    ax.text(.755,.669,r'$B_0\cup B_1\cup B_2=\{x\}$',
        ha='center',va='center',fontsize=11.1,color=INK)
    arrow(ax,(.755,.626),(.755,.575))
    diamond=[(.755,.575),(.955,.465),(.755,.355),(.555,.465)]
    ax.add_patch(Polygon(diamond,closed=True,facecolor='white',edgecolor=BLUE,lw=1.0))
    ax.text(.755,.466,r'$\pi_x(E)\subseteq\pi_x(D)$ ?',
        ha='center',va='center',fontsize=11.0,color=INK)
    arrow(ax,(.66,.407),(.65,.292))
    arrow(ax,(.85,.407),(.875,.292),color=GRAY)
    ax.text(.605,.349,'covered',ha='center',va='center',fontsize=9.7,color=BLUE)
    ax.text(.945,.352,'new x\nvalue',ha='center',va='center',fontsize=9.6,
        color=GRAY,linespacing=1.0)
    box(ax,.535,.16,.23,.13,'Fresh ACCEPT','New E-bound result',size=10.1)
    box(ax,.795,.16,.19,.13,'Fresh checking','Evaluate on E',fc='white',ec=GRAY,size=10.1)
    ax.text(.755,.095,'Old packet stays bound to D',ha='center',va='center',
        fontsize=10.0,color=INK)
    ax.text(.755,.048,'No packet rebinding',ha='center',va='center',
        fontsize=9.7,color=GRAY)
    save(fig,out/'acceptance-transport.pdf')

def domain_results():
    if not DOMAIN_SOURCE.exists(): raise SystemExit('Run the current domain-adequacy study first.')
    data=json.loads(DOMAIN_SOURCE.read_text())
    if data['outcome']!='PASS': raise SystemExit('Domain study is not successful.')
    return data

def domain(out):
    data=domain_results()
    rows=data['domains']; fig,ax=plt.subplots(figsize=(6.8,2.7))
    for i,r in enumerate(rows):
        total=r['points']; f=r['repair_points']/total
        ax.barh(i,f,color=BLUE,height=.54,label='Repair region' if i==0 else None,
            edgecolor=INK,linewidth=.7,hatch='////')
        ax.barh(i,1-f,left=f,color='#dce4e8',height=.54,
            label='Preservation region' if i==0 else None,edgecolor=INK,linewidth=.7)
        if f>0: ax.text(f/2,i,f"{r['repair_points']:,}",ha='center',va='center',color='white',fontsize=11)
        ax.text(f+(1-f)/2,i,f"{r['preservation_points']:,}",ha='center',va='center',fontsize=11)
    ax.set_yticks(range(3),[f"{r['points']:,} inputs" for r in rows]);ax.invert_yaxis()
    ax.set_xlim(0,1);ax.set_xticks([0,.25,.5,.75,1],['0%','25%','50%','75%','100%'])
    ax.set_xlabel('Share of each receiver-declared domain (labels show point counts)')
    ax.spines[['top','right','left']].set_visible(False);ax.tick_params(axis='y',length=0)
    ax.legend(loc='lower center',bbox_to_anchor=(.48,1.02),ncol=2,frameon=False,handlelength=2)
    fig.tight_layout(pad=.7)
    save(fig,out/'domain-coverage.pdf')

def ceiling(out):
    data=domain_results()
    row=next(r for r in data['domains'] if r['name']=='retained42')
    ms,ns=row['axes']['m'],row['axes']['n'];U=(1<<32)-1
    repair=[(i,j) for i,m in enumerate(ms) for j,n in enumerate(ns) if m>U-(n-1)]
    if len(ms)*len(ns)!=42 or len(repair)!=row['repair_points']:
        raise ValueError('ceiling figure domain/count mismatch')
    fig,ax=plt.subplots(figsize=(6.7,3.2))
    for i,m in enumerate(ms):
        for j,n in enumerate(ns):
            bad=m>U-(n-1)
            ax.add_patch(Rectangle((j-.48,i-.48),.96,.96,
                facecolor=PALE if bad else 'white',edgecolor='#d5dce0',lw=.6))
            ax.plot(j,i,marker='x' if bad else 'o',markersize=7,
                markeredgewidth=1.3,markerfacecolor='white',color=BLUE)
    label=lambda x:'U' if x==U else ('U − 1' if x==U-1 else str(x))
    ax.set_xticks(range(len(ns)),[label(n) for n in ns]);ax.set_yticks(range(len(ms)),[label(m) for m in ms])
    ax.set_xlim(-.5,len(ns)-.5);ax.set_ylim(len(ms)-.5,-.5)
    ax.xaxis.tick_top();ax.xaxis.set_label_position('top');ax.set_xlabel('Divisor n   (U = 2³² − 1)',labelpad=9)
    ax.set_ylabel('Numerator m');ax.tick_params(length=0,pad=5)
    ax.spines[:].set_visible(False)
    ax.plot([],[],marker='x',color=BLUE,linestyle='None',label='Repair: compare with reference (12)')
    ax.plot([],[],marker='o',markerfacecolor='white',color=BLUE,linestyle='None',label='Preserve: compare with original (30)')
    ax.legend(loc='upper center',bbox_to_anchor=(.5,-.06),ncol=2,frameon=False,fontsize=10,handlelength=1)
    fig.tight_layout(pad=.7)
    save(fig,out/'ceil-obligations.pdf')

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT.parent/'paper/figures');a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=True)
    overview(a.output);definedness(a.output);acceptance_transport(a.output);domain(a.output);ceiling(a.output)

if __name__=='__main__':main()
