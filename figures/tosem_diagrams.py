"""Publication figures aligned with TOSEM examples in verification and repair.

The figures use sparse line art, direct object-to-object arrows, a single reading
path, and icons only where they encode a real object.  Color is secondary to
shape and position.  All labels and data are generated deterministically.
"""
from __future__ import annotations

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Polygon, Ellipse, FancyArrowPatch, Arc

INK = "#17252d"
BLUE = "#1f6685"
BLUE2 = "#5c89a0"
GRAY = "#68777f"
MID = "#9aa7ad"
RULE = "#d8dde0"
PALE = "#f7f9fa"
RUST = "#a54432"
GREEN = "#2f6d4a"


class Canvas:
    def __init__(self, style, width=428.42, height=190):
        self.style = style
        self.width = width
        self.height = height
        self.figure = plt.figure(figsize=(width / 72, height / 72))
        self.ax = self.figure.add_axes([0, 0, 1, 1], xlim=(0, width), ylim=(0, height))
        self.ax.set_axis_off()

    def text(self, x, y, value, size=9, *, ha="center", va="center",
             color=INK, weight="normal", rotation=0, zorder=6, **kwargs):
        return self.ax.text(x, y, value, fontsize=size, ha=ha, va=va,
                            color=color, fontweight=weight, rotation=rotation,
                            linespacing=1.04, zorder=zorder, **kwargs)

    def line(self, x0, y0, x1, y1, *, color=INK, lw=.8, ls="-", zorder=2):
        self.ax.plot([x0, x1], [y0, y1], color=color, lw=lw, ls=ls,
                     solid_capstyle="round", zorder=zorder)

    def arrow(self, start, end, *, color=INK, lw=.85, ls="-", mutation=7.2,
              connectionstyle="arc3", zorder=4):
        patch = FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=mutation,
                                linewidth=lw, linestyle=ls, color=color,
                                shrinkA=0, shrinkB=0, connectionstyle=connectionstyle,
                                zorder=zorder)
        self.ax.add_patch(patch)
        return patch

    def rect(self, x, y, w, h, *, edge=INK, face="white", lw=.75, ls="-", zorder=1):
        patch = Rectangle((x, y), w, h, facecolor=face, edgecolor=edge,
                          linewidth=lw, linestyle=ls, zorder=zorder)
        self.ax.add_patch(patch)
        return patch

    def ellipse(self, x, y, w, h, *, edge=INK, face="white", lw=.8, ls="-", zorder=2):
        patch = Ellipse((x, y), w, h, facecolor=face, edgecolor=edge,
                        linewidth=lw, linestyle=ls, zorder=zorder)
        self.ax.add_patch(patch)
        return patch

    def circle(self, x, y, r, *, edge=INK, face="white", lw=.8, ls="-", zorder=2):
        patch = Circle((x, y), r, facecolor=face, edgecolor=edge,
                       linewidth=lw, linestyle=ls, zorder=zorder)
        self.ax.add_patch(patch)
        return patch

    def diamond(self, x, y, w, h, *, edge=INK, face="white", lw=.8, zorder=2):
        patch = Polygon([(x, y+h/2), (x+w/2, y), (x, y-h/2), (x-w/2, y)],
                        closed=True, facecolor=face, edgecolor=edge,
                        linewidth=lw, zorder=zorder)
        self.ax.add_patch(patch)
        return patch


def icon_document(c: Canvas, x, y, w=22, h=27, *, edge=INK, code=False):
    f = 6
    pts = [(x-w/2, y-h/2), (x+w/2, y-h/2), (x+w/2, y+h/2-f),
           (x+w/2-f, y+h/2), (x-w/2, y+h/2)]
    c.ax.add_patch(Polygon(pts, closed=True, facecolor="white", edgecolor=edge,
                           linewidth=.85, zorder=2))
    c.line(x+w/2-f, y+h/2, x+w/2-f, y+h/2-f, color=edge, lw=.55)
    c.line(x+w/2-f, y+h/2-f, x+w/2, y+h/2-f, color=edge, lw=.55)
    if code:
        c.text(x, y, "</>", size=7.1, color=edge, weight="bold")
    else:
        for dy, frac in [(5,.55),(0,.72),(-5,.45)]:
            c.line(x-w*.25, y+dy, x-w*.25+w*frac, y+dy, color=edge, lw=.55)


def icon_table(c: Canvas, x, y, w=24, h=18, *, edge=BLUE, rows=2, cols=3):
    c.rect(x-w/2, y-h/2, w, h, edge=edge, face="white", lw=.85)
    for i in range(1, cols):
        c.line(x-w/2+i*w/cols, y-h/2, x-w/2+i*w/cols, y+h/2, color=edge, lw=.5)
    for i in range(1, rows):
        c.line(x-w/2, y-h/2+i*h/rows, x+w/2, y-h/2+i*h/rows, color=edge, lw=.5)


def icon_magnifier(c: Canvas, x, y, r=5.5, *, edge=BLUE):
    c.circle(x, y, r, edge=edge, face="white", lw=.95)
    c.line(x+r*.7, y-r*.7, x+r*1.75, y-r*1.75, color=edge, lw=1.0)


def icon_database(c: Canvas, x, y, w=22, h=22, *, edge=BLUE):
    c.ellipse(x, y+h*.36, w, h*.34, edge=edge, face="white", lw=.85)
    c.line(x-w/2, y-h*.36, x-w/2, y+h*.36, color=edge, lw=.85)
    c.line(x+w/2, y-h*.36, x+w/2, y+h*.36, color=edge, lw=.85)
    c.ax.add_patch(Arc((x,y),w,h*.34,theta1=180,theta2=360,color=edge,lw=.85))
    c.ax.add_patch(Arc((x,y-h*.36),w,h*.34,theta1=180,theta2=360,color=edge,lw=.85))


def icon_history(c: Canvas, x, y, *, edge=BLUE):
    icon_database(c, x-3, y+2, w=19, h=19, edge=edge)
    c.circle(x+8, y-7, 6.5, edge=edge, face="white", lw=.85)
    c.line(x+8, y-7, x+8, y-3.5, color=edge, lw=.75)
    c.line(x+8, y-7, x+11, y-8.8, color=edge, lw=.75)


def icon_key(c: Canvas, x, y, *, edge=BLUE):
    c.circle(x-4, y+2, 4.6, edge=edge, face="white", lw=.9)
    c.line(x, y-.5, x+11, y-7, color=edge, lw=.95)
    c.line(x+7.5, y-5, x+10.5, y-2.5, color=edge, lw=.9)


def icon_shield(c: Canvas, x, y, *, edge=GREEN, scale=.65, check=True):
    w, h = 18*scale, 22*scale
    pts = [(x, y+h*.48), (x+w*.48, y+h*.27), (x+w*.36, y-h*.22),
           (x, y-h*.50), (x-w*.36, y-h*.22), (x-w*.48, y+h*.27)]
    c.ax.add_patch(Polygon(pts, closed=True, facecolor="white", edgecolor=edge,
                           linewidth=.95, zorder=2))
    if check:
        c.line(x-w*.18, y, x-w*.03, y-h*.16, color=edge, lw=1.0)
        c.line(x-w*.03, y-h*.16, x+w*.23, y+h*.14, color=edge, lw=1.0)


def icon_cross(c: Canvas, x, y, *, edge=RUST, r=5.0):
    c.circle(x, y, r, edge=edge, face="white", lw=.95)
    c.line(x-r*.45, y-r*.45, x+r*.45, y+r*.45, color=edge, lw=1.0)
    c.line(x-r*.45, y+r*.45, x+r*.45, y-r*.45, color=edge, lw=1.0)


def icon_open(c: Canvas, x, y, *, edge=GRAY, r=5.0):
    c.ellipse(x, y, 2*r, 1.3*r, edge=edge, face="white", lw=.95)


def icon_support_graph(c: Canvas, x, y, *, edge=BLUE):
    pts = [(x-14,y+7),(x,y+13),(x+13,y+7),(x-7,y-9),(x+9,y-8)]
    edges = [(0,1),(1,2),(0,3),(1,3),(1,4),(2,4),(3,4)]
    for a,b in edges:
        c.line(*pts[a], *pts[b], color=edge, lw=.62)
    for px,py in pts:
        c.circle(px,py,2.2,edge=edge,face="white",lw=.78)


def icon_refresh(c: Canvas, x, y, *, edge=GRAY):
    c.ax.add_patch(Arc((x,y),16,16,theta1=35,theta2=210,color=edge,lw=1.0))
    c.ax.add_patch(Arc((x,y),16,16,theta1=215,theta2=390,color=edge,lw=1.0))
    c.arrow((x-6.5,y+3.5),(x-8,y+7),color=edge,lw=.8,mutation=5.5)
    c.arrow((x+6.5,y-3.5),(x+8,y-7),color=edge,lw=.8,mutation=5.5)


def small_label(c: Canvas, x, y, text, *, color=GRAY, size=7.2, ha="center", weight="normal"):
    c.text(x, y, text, size=size, color=color, ha=ha, weight=weight)


def overview(style, output: Path, name="repairseal-overview", variant=5):
    """Three receiver obligations as one shared-input object-flow diagram."""
    c = Canvas(style, height=174)
    icon_document(c, 25, 150, 21, 26, edge=INK, code=True)
    c.text(43, 150, r"request $A$", size=9.2, ha="left", weight="bold")
    c.arrow((91,150),(117,150),color=INK)
    c.circle(136,150,16,edge=BLUE,face="white",lw=1.0)
    c.text(136,154,"R",size=11.5,weight="bold",color=BLUE)
    small_label(c,116,132,"receiver semantics",color=BLUE,size=7.1,ha="right")
    c.line(136,134,136,28,color=INK,lw=.75)

    ys=(112,72,32)
    for y in ys:
        c.circle(136,y,2.1,edge=INK,face=INK,lw=.5)
        c.arrow((138,y),(166,y),color=INK)

    # Complete decision: rows or support-keyed demand reach the same checker.
    c.text(171,130,"complete decision",size=7.9,ha="left",weight="bold")
    icon_table(c,184,116,21,16,edge=GRAY)
    icon_key(c,214,109,edge=BLUE)
    small_label(c,184,98,"rows",color=GRAY,size=6.7)
    small_label(c,214,98,"demand",color=BLUE,size=6.7)
    c.line(196,116,232,116,color=GRAY,lw=.62)
    c.line(225,109,232,109,color=BLUE,lw=.62)
    c.line(232,109,232,116,color=INK,lw=.65)
    c.arrow((232,112),(257,112),color=INK)
    icon_magnifier(c,270,112,r=5.4,edge=INK)
    c.arrow((283,112),(306,112),color=INK)
    c.circle(309,112,2.0,edge=INK,face=INK,lw=.5)
    c.arrow((311,116),(335,127),color=GREEN)
    icon_shield(c,345,129,edge=GREEN,scale=.58)
    c.text(356,129,"ACCEPT",size=7.8,ha="left",weight="bold",color=GREEN)
    c.arrow((311,108),(335,97),color=RUST)
    icon_cross(c,345,96,edge=RUST,r=4.5)
    c.text(356,100,"least",size=6.5,ha="left",color=RUST)
    c.text(356,91,"REFUTED",size=7.5,ha="left",weight="bold",color=RUST)

    # A named violation proves only a local refutation.
    c.text(171,89,"named violation",size=7.9,ha="left",weight="bold")
    c.circle(190,72,5.0,edge=RUST,face="white",lw=.95)
    c.circle(190,72,1.4,edge=RUST,face=RUST,lw=.4)
    c.text(190,59,r"$u^*$",size=7.2,color=RUST)
    c.arrow((200,72),(250,72),color=RUST)
    icon_magnifier(c,264,72,r=5.3,edge=RUST)
    small_label(c,264,57,r"check $O_j(u^*)$",color=RUST,size=6.8)
    c.arrow((277,72),(335,72),color=RUST)
    icon_cross(c,345,72,edge=RUST,r=4.8)
    c.text(356,76,"REFUTED",size=7.7,ha="left",weight="bold",color=RUST)
    c.text(356,65,"at the named point",size=6.7,ha="left",color=GRAY)

    # Accepted history can authorize reuse, otherwise it gives no conclusion.
    c.text(171,45,"accepted history",size=7.9,ha="left",weight="bold")
    icon_history(c,191,27,edge=BLUE)
    c.arrow((206,27),(242,32),color=BLUE)
    c.diamond(260,32,34,25,edge=INK,face="white",lw=.85)
    c.text(260,32,"cover?",size=7.1,weight="bold")
    c.arrow((277,38),(309,48),color=GREEN)
    small_label(c,291,47,"yes",color=GREEN,size=6.4)
    icon_shield(c,320,50,edge=GREEN,scale=.52)
    c.text(330,50,r"ACCEPT $E$",size=7.5,ha="left",weight="bold",color=GREEN)
    c.arrow((277,26),(307,16),color=GRAY)
    small_label(c,290,30,"no",color=GRAY,size=6.4)
    icon_open(c,318,15,edge=GRAY,r=4.5)
    c.text(328,15,"no conclusion",size=7.0,ha="left",weight="bold",color=GRAY)
    c.arrow((387,15),(400,15),color=GRAY)
    icon_refresh(c,410,15,edge=GRAY)
    small_label(c,404,5,"complete check",color=GRAY,size=5.9)
    style.save_figure(c.figure, output, name)


def ceil_obligations(style, root: Path, output: Path, name="ceil-obligations", variant=5):
    """Exact 42-point running example, using a compact matrix and one edit arrow."""
    U = 2**32 - 1
    ms = [0,1,2,31,32,U-1,U]
    ns = [1,2,3,7,32,U]
    def repair(m,n): return m > U-(n-1)
    flags = [[repair(m,n) for n in ns] for m in ms]
    assert sum(v for row in flags for v in row) == 12
    c = Canvas(style, height=226)

    # edit strip
    icon_document(c, 24, 202, 20, 25, edge=INK, code=True)
    c.text(42,208,"before",size=7.1,ha="left",color=RUST,weight="bold")
    c.text(42,194,r"$(m+n-1)/n$",size=10.0,ha="left")
    c.arrow((124,202),(157,202),color=INK)
    c.text(140,214,"wrap",size=7.0,color=RUST,weight="bold")
    icon_document(c, 177, 202, 20, 25, edge=INK, code=True)
    c.text(195,208,"after",size=7.1,ha="left",color=BLUE,weight="bold")
    c.text(195,194,r"$m/n+[m\,\mathrm{mod}\,n\ne0]$",size=10.0,ha="left")
    c.text(420,202,r"32-bit unsigned; $n>0$",size=7.3,ha="right",color=GRAY)

    # matrix
    x0,y0=112,34
    cw,ch=47,17
    c.text(74,158,r"$n$",size=8.3,weight="bold")
    for j,n in enumerate(ns):
        c.text(x0+j*cw+(cw-3)/2,158,r"$U$" if n==U else str(n),size=8.0)
    for i,m in enumerate(ms):
        label = r"$U-1$" if m==U-1 else (r"$U$" if m==U else str(m))
        cy=y0+(len(ms)-1-i)*ch+(ch-2)/2
        c.text(96,cy,label,size=7.9,ha="right")
        for j,n in enumerate(ns):
            x=x0+j*cw; y=y0+(len(ms)-1-i)*ch
            c.rect(x,y,cw-3,ch-2,edge=RULE,face="white",lw=.55)
            cx=x+(cw-3)/2; cy=y+(ch-2)/2
            if flags[i][j]:
                icon_cross(c,cx,cy,edge=RUST,r=3.7)
            else:
                c.circle(cx,cy,2.8,edge=BLUE,face="white",lw=.85)
    c.text(70,90,r"$m$",size=8.3,weight="bold",rotation=90)

    # concise legend
    icon_cross(c,104,15,edge=RUST,r=3.8)
    c.text(114,15,"repair 12",size=7.7,ha="left")
    c.circle(199,15,2.8,edge=BLUE,face="white",lw=.85)
    c.text(209,15,"preserve 30",size=7.7,ha="left")
    icon_shield(c,315,15,edge=GREEN,scale=.48)
    c.text(326,15,"defined at all 42",size=7.7,ha="left")
    style.save_figure(c.figure, output, name)


def support_demand(style, output: Path, name="support-demand-overview", variant=5):
    """One continuous support-keyed evaluation path with explicit short-circuiting."""
    c = Canvas(style, height=148)
    y=78
    icon_document(c,18,y,19,24,edge=INK,code=True)
    small_label(c,18,52,"request",color=GRAY,size=6.7)
    c.arrow((31,y),(49,y),color=INK)

    icon_support_graph(c,64,y,edge=BLUE)
    c.text(64,110,"supports",size=7.5,weight="bold")
    c.text(64,48,r"$B_g=\{x\}$; $B_e=\{x,y\}$",size=6.7,color=GRAY)
    c.arrow((81,y),(103,y),color=INK)

    icon_key(c,113,y+5,edge=BLUE)
    icon_table(c,143,y,27,21,edge=BLUE,rows=2,cols=2)
    c.text(130,110,"projected memo",size=7.5,weight="bold")
    c.text(130,48,"four projection keys",size=6.7,color=GRAY)
    c.arrow((158,y),(181,y),color=INK)

    nodes=[(201,GREEN,"check",r"$O_0$"),(232,RUST,"cross",r"$O_1$"),(263,GRAY,"",r"$O_2$")]
    for i,(x,col,symbol,lab) in enumerate(nodes):
        ls=(0,(3,2)) if col==GRAY else "-"
        c.circle(x,y,8.5,edge=col,face="white",lw=.9,ls=ls)
        if symbol == "check":
            c.line(x-3.6,y-.4,x-1.0,y-2.8,color=col,lw=1.0)
            c.line(x-1.0,y-2.8,x+3.8,y+2.8,color=col,lw=1.0)
        elif symbol == "cross":
            c.line(x-3.0,y-3.0,x+3.0,y+3.0,color=col,lw=1.0)
            c.line(x-3.0,y+3.0,x+3.0,y-3.0,color=col,lw=1.0)
        else:
            c.line(x-3.7,y,x+3.7,y,color=GRAY,lw=.75,ls=(0,(3,2)))
        c.text(x,101,lab,size=7.7,weight="bold",color=col)
        if i<2:
            c.arrow((x+8.5,y),(nodes[i+1][0]-8.5,y),color=INK if i==0 else GRAY,
                    ls="-" if i==0 else (0,(3,2)),lw=.75)
    c.text(232,49,"first failure",size=6.8,color=RUST,weight="bold")
    c.text(263,49,"not run",size=6.6,color=GRAY)

    c.arrow((272,y),(295,y),color=RUST)
    icon_magnifier(c,307,y,r=5.5,edge=RUST)
    c.text(307,110,"lazy diagnostic",size=7.5,weight="bold")
    c.text(307,49,"trace + input",size=6.7,color=GRAY)
    c.arrow((320,y),(340,y),color=INK)
    icon_table(c,352,y,25,19,edge=GRAY,rows=2,cols=2)
    c.text(352,49,"least pair",size=6.7,color=GRAY)
    c.arrow((366,y),(389,y),color=INK)
    icon_cross(c,402,y,edge=RUST,r=4.8)
    c.text(402,110,"decision",size=7.2,weight="bold")
    c.text(402,49,"least REFUTED",size=6.8,color=RUST,weight="bold")
    style.save_figure(c.figure, output, name)


def acceptance_transport(style, output: Path, name="acceptance-transport", variant=5):
    """Coverage as a projection relation with a non-verdict fallback."""
    c = Canvas(style, width=402.715, height=156)
    icon_history(c,24,132,edge=BLUE)
    c.text(43,136,r"accepted on $D$",size=8.0,ha="left",weight="bold",color=BLUE)
    c.text(43,124,"receiver-owned",size=6.7,ha="left",color=GRAY)
    c.arrow((109,132),(139,132),color=BLUE)
    icon_key(c,153,132,edge=BLUE)
    c.text(166,132,r"supports $B_j$",size=7.7,ha="left",weight="bold")

    c.text(57,113,r"old domain $D$",size=6.9,weight="bold")
    c.ellipse(57,94,60,28,edge=BLUE,face="white",lw=.85)
    for dx,dy in [(-17,4),(-4,7),(11,4),(-10,-6),(7,-5),(18,-2)]:
        c.circle(57+dx,94+dy,1.9,edge=BLUE,face=BLUE,lw=.4)
    c.text(57,68,r"new domain $E$",size=6.9,weight="bold")
    c.ellipse(57,49,60,28,edge=GRAY,face="white",lw=.85)
    for dx,dy in [(-17,4),(-4,7),(11,4),(-10,-6),(7,-5),(18,-2),(0,-1)]:
        c.circle(57+dx,49+dy,1.9,edge=GRAY,face=GRAY,lw=.4)

    c.arrow((89,94),(116,94),color=BLUE)
    c.arrow((89,49),(116,49),color=GRAY)
    c.ellipse(143,94,44,22,edge=BLUE,face="white",lw=.8)
    c.ellipse(143,49,44,22,edge=GRAY,face="white",lw=.8)
    for x in [134,143,152]:
        c.circle(x,94,1.9,edge=BLUE,face=BLUE,lw=.35)
        c.circle(x,49,1.9,edge=GRAY,face=GRAY,lw=.35)
    c.text(143,111,r"$\pi_{B_j}(D)$",size=6.9)
    c.text(143,66,r"$\pi_{B_j}(E)$",size=6.9)

    c.line(166,94,196,94,color=BLUE,lw=.65)
    c.line(166,49,196,49,color=GRAY,lw=.65)
    c.line(196,49,196,94,color=INK,lw=.65)
    c.arrow((196,72),(220,72),color=INK)
    c.text(242,108,"coverage",size=7.5,weight="bold")
    c.diamond(242,72,40,30,edge=INK,face="white",lw=.85)
    c.text(242,76,"all j",size=6.8,weight="bold")
    c.text(242,66,r"$\subseteq$",size=8.5,weight="bold")

    c.arrow((262,81),(296,101),color=GREEN)
    c.text(280,97,"yes",size=6.5,color=GREEN)
    icon_shield(c,307,104,edge=GREEN,scale=.58)
    c.text(319,108,r"reuse ACCEPT $E$",size=7.5,ha="left",weight="bold",color=GREEN)
    c.text(319,95,"0 new semantic cells",size=6.5,ha="left",color=GRAY)

    c.arrow((262,63),(294,45),color=GRAY)
    c.text(279,48,"no",size=6.5,color=GRAY)
    icon_open(c,306,43,edge=GRAY,r=4.6)
    c.text(318,47,"no conclusion",size=7.3,ha="left",weight="bold",color=GRAY)
    c.arrow((350,38),(350,20),color=GRAY)
    icon_refresh(c,307,15,edge=GRAY)
    c.text(320,15,"ordinary complete check",size=6.8,ha="left",color=GRAY)
    style.save_figure(c.figure, output, name)


def trust_boundary(style, output: Path, name="trust-boundary", variant=5):
    """Direct checking and replay converge on one semantic kernel."""
    c = Canvas(style, height=174)

    # Direct lane.
    c.text(12,151,"direct",size=8.0,ha="left",weight="bold")
    icon_document(c,35,128,19,24,edge=INK,code=True)
    c.text(35,107,"request",size=6.7,color=GRAY)
    c.arrow((48,128),(87,128),color=INK)
    icon_support_graph(c,104,128,edge=BLUE)
    c.text(104,107,"derive supports",size=6.7,color=GRAY)

    # Replay lane with additional admission checks.
    c.text(12,82,"replay",size=8.0,ha="left",weight="bold")
    c.text(151,82,"replay-only checks",size=6.8,color=GRAY,weight="bold")
    icon_table(c,34,53,20,16,edge=GRAY)
    c.text(34,34,"packet",size=6.7,color=GRAY)
    c.arrow((46,53),(63,53),color=INK)
    replay=[(76,"id",icon_magnifier),(112,"bind",icon_shield),(157,"cover",icon_key),(202,"rows",icon_table),(242,"proof",icon_magnifier)]
    for i,(x,label,fn) in enumerate(replay):
        if fn is icon_magnifier: fn(c,x,53,r=4.3,edge=BLUE)
        elif fn is icon_shield: fn(c,x,53,edge=BLUE,scale=.43)
        elif fn is icon_key: fn(c,x,53,edge=BLUE)
        else: fn(c,x,53,17,13,edge=BLUE)
        c.text(x,68,label,size=6.5,color=GRAY)
        if i<len(replay)-1:
            c.arrow((x+9,53),(replay[i+1][0]-9,53),color=INK,lw=.68)

    # Replay-only exits are outcomes of admission, not repair verdicts.
    c.arrow((112,44),(104,20),color=RUST,ls=(0,(3,2)),lw=.7)
    icon_cross(c,101,13,edge=RUST,r=3.7)
    c.text(91,13,"INVALID",size=6.1,color=RUST,weight="bold",ha="right")
    c.arrow((157,44),(163,20),color=GRAY,ls=(0,(3,2)),lw=.7)
    icon_open(c,165,13,edge=GRAY,r=3.8)
    c.text(175,13,"UNCOVERED",size=6.0,color=GRAY,weight="bold",ha="left")

    # Both lanes join the same receiver semantics.
    c.arrow((122,128),(263,103),color=BLUE)
    c.arrow((254,53),(267,75),color=BLUE)
    c.circle(282,89,18,edge=BLUE,face="white",lw=.95)
    c.text(282,93,"semantic",size=7.0,weight="bold",color=BLUE)
    c.text(282,83,"kernel",size=7.0,weight="bold",color=BLUE)
    c.text(282,116,"shared",size=6.6,color=BLUE,weight="bold")

    c.arrow((300,89),(329,89),color=INK)
    icon_magnifier(c,342,89,r=5.2,edge=BLUE)
    c.text(342,68,"evaluate",size=6.7,color=GRAY)
    c.arrow((355,89),(382,89),color=INK)
    icon_shield(c,375,89,edge=GREEN,scale=.58)
    c.text(387,89,"verdict",size=7.4,ha="left",weight="bold",color=GREEN)
    style.save_figure(c.figure, output, name)


def definedness_example(style, output: Path, name="value-definedness", variant=1):
    """Artifact-only source-definedness example in the publication line-art style."""
    c = Canvas(style, height=132)

    # Concrete executed request.
    icon_document(c, 24, 92, 20, 25, edge=INK, code=True)
    c.text(43, 104, r"executed at $n=1$", size=8.1, ha="left", weight="bold")
    c.text(43, 88, r"$s\leftarrow1/(n-1)$", size=9.2, ha="left")
    c.text(43, 72, r"return repaired value", size=7.0, ha="left", color=GRAY)
    c.arrow((124, 91), (154, 91), color=INK)
    c.circle(160, 91, 2.1, edge=INK, face=INK, lw=.5)

    # Totalized value lane: it can satisfy the local value relation, but is not
    # the definedness evidence.
    c.arrow((162, 96), (197, 112), color=BLUE)
    c.text(224, 117, "totalized value", size=7.6, weight="bold", color=BLUE)
    c.text(224, 101, r"$1/0\mapsto0$", size=9.4, color=BLUE)
    c.arrow((253, 106), (291, 106), color=BLUE)
    c.circle(302, 106, 7.0, edge=BLUE, face="white", lw=.9)
    c.line(298.5, 106.0, 301.0, 103.6, color=BLUE, lw=1.0)
    c.line(301.0, 103.6, 305.3, 109.0, color=BLUE, lw=1.0)
    c.text(319, 106, "value relation", size=7.2, ha="left", color=BLUE)

    # Source-definedness lane: the executed denominator is undefined, so the
    # corresponding root refutes the candidate even if s is unused later.
    c.arrow((162, 86), (197, 56), color=RUST)
    c.text(238, 61, "source definedness", size=7.6, weight="bold", color=RUST)
    c.text(224, 44, r"$n-1\ne0$ is false", size=8.7, color=RUST)
    c.arrow((260, 51), (292, 51), color=RUST)
    c.circle(302, 51, 7.0, edge=RUST, face="white", lw=.9)
    c.text(302, 51, r"$O_0$", size=7.3, color=RUST, weight="bold")
    c.arrow((311, 51), (346, 51), color=RUST)
    icon_cross(c, 356, 51, edge=RUST, r=5.1)
    c.text(369, 51, "REFUTED", size=8.1, ha="left", weight="bold", color=RUST)

    # One short mechanism annotation, attached to the executed assignment.
    c.line(89, 65, 89, 29, color=GRAY, lw=.65, ls="--")
    c.text(89, 17, "executed fault persists", size=7.0,
           color=GRAY, weight="bold")

    style.save_figure(c.figure, output, name)
