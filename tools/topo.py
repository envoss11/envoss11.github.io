"""Contours of a 2-D Gaussian mixture, drawn behind every page.

Usage: python3 tools/topo.py _includes/topo.svg  (or `make topo`)
"""
import math, sys

W = H = 640
STEP = 4
# (weight, mean x, mean y, sd x, sd y, correlation)
COMPONENTS = [
    (0.50, 360, 255, 60, 48, 0.30),
    (0.30, 245, 385, 42, 50, -0.20),
    (0.20, 425, 425, 38, 34, 0.10),
]
# The page crops this drawing: roughly x 0-460 and y 160-640 of the
# 640 x 640 box are on screen. Keep the means in there.

def density(x, y):
    total = 0.0
    for w, mx, my, sx, sy, r in COMPONENTS:
        dx, dy = (x - mx) / sx, (y - my) / sy
        q = (dx * dx - 2 * r * dx * dy + dy * dy) / (1 - r * r)
        total += w / (2 * math.pi * sx * sy * math.sqrt(1 - r * r)) * math.exp(-q / 2)
    return total

nx, ny = W // STEP + 1, H // STEP + 1
grid = [[density(i * STEP, j * STEP) for i in range(nx)] for j in range(ny)]
peak = max(max(row) for row in grid)
grid = [[v / peak for v in row] for row in grid]

def contour(level):
    """Marching squares; returns polylines (lists of points), joined end to end."""
    def lerp(a, b, pa, pb):
        t = (level - a) / (b - a)
        return (pa[0] + t * (pb[0] - pa[0]), pa[1] + t * (pb[1] - pa[1]))
    segs = []
    for j in range(ny - 1):
        for i in range(nx - 1):
            c = [grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]]
            p = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
            pts = []
            for e in range(4):
                a, b = c[e], c[(e + 1) % 4]
                if (a >= level) != (b >= level):
                    key = tuple(sorted((p[e], p[(e + 1) % 4])))
                    pts.append((key, lerp(a, b, p[e], p[(e + 1) % 4])))
            if len(pts) == 2:
                segs.append(pts)
            elif len(pts) == 4:  # saddle: pair by the centre value
                centre = sum(c) / 4
                if (centre >= level) == (c[0] >= level):
                    segs += [[pts[0], pts[3]], [pts[1], pts[2]]]
                else:
                    segs += [[pts[0], pts[1]], [pts[2], pts[3]]]
    # Join segments that share an edge crossing.
    ends = {}
    for s in segs:
        for k in (0, 1):
            ends.setdefault(s[k][0], []).append(s)
    used, lines = set(), []
    for s in segs:
        if id(s) in used:
            continue
        used.add(id(s))
        line = [s[0], s[1]]
        for _ in range(2):  # extend forward, then reverse and extend the other end
            while True:
                nxt = [t for t in ends[line[-1][0]] if id(t) not in used]
                if not nxt:
                    break
                t = nxt[0]; used.add(id(t))
                line.append(t[1] if t[0][0] == line[-1][0] else t[0])
            if line[0][0] == line[-1][0]:
                break
            line.reverse()
        closed = line[0][0] == line[-1][0]
        lines.append(([(q[1][0] * STEP, q[1][1] * STEP) for q in line], closed))
    return lines

def thin(pts, every=4):
    return pts[::every] if len(pts) > every * 4 else pts

def path(pts, closed):
    if closed:
        pts = pts[:-1]
    pts = thin(pts)
    n = len(pts)
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[i - 1] if (closed or i > 0) else pts[i]
        p1, p2 = pts[i], pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f"C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
    return d + ("Z" if closed else "")

for w, mx, my, *_ in COMPONENTS:
    here = density(mx, my)
    near = max(density(mx + 6 * math.cos(a / 8 * math.pi), my + 6 * math.sin(a / 8 * math.pi)) for a in range(16))
    if near >= here:
        sys.exit(f"component at ({mx},{my}) is not a peak of the mixture; space the components out")

out, open_count = [], 0
LEVELS = 14
for k in range(1, LEVELS + 1):
    # Spaced like the rings of a single Gaussian at even radii.
    level = math.exp(-0.5 * ((LEVELS + 1 - k) * 0.21) ** 2)
    cls = ' class="index"' if k % 5 == 0 else ''
    for pts, closed in contour(level):
        open_count += not closed
        out.append(f'<path{cls} d="{path(pts, closed)}"/>')

dots = []
for n, (w, mx, my, *_rest) in enumerate(COMPONENTS):
    dots.append(f'<circle class="summit" cx="{mx}" cy="{my}" r="{2.5 if n == 0 else 1.8}"/>')

comment = ("<!-- Contours of a Gaussian mixture: "
           + "; ".join(f"w={w}, mu=({mx},{my}), sd=({sx},{sy}), rho={r}" for w, mx, my, sx, sy, r in COMPONENTS)
           + ". Dots mark the component means. -->")
svg = (comment + f'<svg class="topo" viewBox="0 0 {W} {H}" aria-hidden="true" focusable="false">'
       '<g fill="none" stroke="currentColor">' + "".join(out) + "".join(dots) + "</g></svg>\n")
open(sys.argv[1], "w").write(svg)
print(f"{len(out)} paths, {open_count} open, {len(svg)} bytes", file=sys.stderr)
