"""VMF brush helpers lifted from gcs-gmod tools/build_vmf.py (gm_grand_central 0.19.0).
build_vmf.py sets SCALE, USHIFT and FACEUV entries for its own materials."""
import math

WALL = 64
TEX_CLOCK = None
SCALE = {}
USHIFT = {}
FACEUV = {}
_id = [0]

def nid():
    _id[0] += 1
    return _id[0]


def sub(a, b): return (a[0]-b[0], a[1]-b[1], a[2]-b[2])
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def dot(a, b): return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]

def axes_for(n, s=0.25):
    ax = max(range(3), key=lambda i: abs(n[i]))
    if ax == 2:
        return "[1 0 0 0] %g" % s, "[0 -1 0 0] %g" % s
    if ax == 0:
        return "[0 1 0 0] %g" % s, "[0 0 -1 0] %g" % s
    return "[1 0 0 0] %g" % s, "[0 0 -1 0] %g" % s


def side(pts, n, tex, uv=None):
    p1, p2, p3 = pts[0], pts[1], pts[2]
    # Source plane winding: outward normal = (p3-p1) x (p2-p1)
    if dot(cross(sub(p3, p1), sub(p2, p1)), n) < 0:
        p2, p3 = p3, p2
    f = lambda p: "(%g %g %g)" % p
    uv = uv or (FACEUV[tex](n) if tex in FACEUV else None)
    u, v = uv or axes_for(n, SCALE.get(tex, 0.25))
    if not uv and tex == TEX_CLOCK and abs(n[2]) < 0.5 and n[0] - n[1] < 0:
        u = u.replace("[0 1 0", "[0 -1 0").replace("[1 0 0", "[-1 0 0")   # unmirror -x and +y dials
    if not uv and tex in USHIFT:
        u = u.replace(" 0] ", " %g] " % USHIFT[tex])
    return ('\tside\n\t{\n\t\t"id" "%d"\n\t\t"plane" "%s %s %s"\n\t\t"material" "%s"\n'
            '\t\t"uaxis" "%s"\n\t\t"vaxis" "%s"\n\t\t"rotation" "0"\n\t\t"lightmapscale" "16"\n'
            '\t\t"smoothing_groups" "0"\n\t}\n') % (nid(), f(p1), f(p2), f(p3), tex, u, v)


def prism(poly, z0, z1, tex, caps=None):
    """Convex polygon in xy (counter-clockwise), extruded z0..z1."""
    caps = caps or tex
    s = side([(x, y, z1) for x, y in poly], (0, 0, 1), caps)
    s += side([(x, y, z0) for x, y in poly], (0, 0, -1), caps)
    for i in range(len(poly)):
        a, b = poly[i], poly[(i+1) % len(poly)]
        n = (b[1]-a[1], -(b[0]-a[0]), 0)
        s += side([(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1)], n, tex)
    return "solid\n{\n\t\"id\" \"%d\"\n%s}\n" % (nid(), s)


def xprism(poly, x0, x1, tex, uvs=None):
    """Convex polygon in yz (counter-clockwise seen from +x), extruded x0..x1.
    uvs: optional {edge index: (uaxis, vaxis)} for the face on that edge."""
    s = side([(x1, y, z) for y, z in poly], (1, 0, 0), tex)
    s += side([(x0, y, z) for y, z in poly], (-1, 0, 0), tex)
    for i in range(len(poly)):
        a, b = poly[i], poly[(i+1) % len(poly)]
        n = (0, b[1]-a[1], -(b[0]-a[0]))
        s += side([(x0, a[0], a[1]), (x0, b[0], b[1]), (x1, b[0], b[1])], n, tex, (uvs or {}).get(i))
    return "solid\n{\n\t\"id\" \"%d\"\n%s}\n" % (nid(), s)


def yprism(poly, y0, y1, tex, uv=None, ends=None):
    """Convex polygon in xz (counter-clockwise seen from -y), extruded y0..y1.
    uv: one (u, v) for every face; ends: material for the two y faces (default tex)."""
    s = side([(x, y0, z) for x, z in poly], (0, -1, 0), ends or tex, uv)
    s += side([(x, y1, z) for x, z in poly], (0, 1, 0), ends or tex, uv)
    for i in range(len(poly)):
        a, b = poly[i], poly[(i+1) % len(poly)]
        n = (b[1]-a[1], 0, -(b[0]-a[0]))
        s += side([(a[0], y0, a[1]), (b[0], y0, b[1]), (b[0], y1, b[1])], n, tex, uv)
    return "solid\n{\n\t\"id\" \"%d\"\n%s}\n" % (nid(), s)


def halfdisc(cx, z0, r, n=10):
    return [(round(cx + r*math.cos(math.pi*i/n)), round(z0 + r*math.sin(math.pi*i/n))) for i in range(n+1)]


def ccw(poly):
    a = sum(poly[i][0]*poly[(i+1) % len(poly)][1] - poly[(i+1) % len(poly)][0]*poly[i][1] for i in range(len(poly)))
    return poly if a > 0 else poly[::-1]


def box(x0, y0, z0, x1, y1, z1, tex):
    return prism([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1, tex)


def ngon(cx, cy, r, n, rot=0.0):
    return [(round(cx + r*math.cos(rot + 2*math.pi*i/n)), round(cy + r*math.sin(rot + 2*math.pi*i/n))) for i in range(n)]


def ent(cls, origin=None, solids="", **kv):
    kv = {"classname": cls, **kv}
    if origin:
        kv["origin"] = "%g %g %g" % origin
    body = "".join('\t"%s" "%s"\n' % (k, v) for k, v in kv.items())
    return "entity\n{\n\t\"id\" \"%d\"\n%s%s}\n" % (nid(), body, solids)



def groin(W, x0, x1, y0, y1, zs, rise, tex, n=8):
    """Groin vault over x0..x1, y0..y1 springing at zs: the solid is the intersection of two
    crossing barrels' solids, so the plan splits along the diagonals into four triangles and
    each triangle follows the barrel whose arch stands on its wall. n even. World brushes."""
    top = zs + rise + 16
    yc, hy, xc, hx = (y0+y1)/2, (y1-y0)/2, (x0+x1)/2, (x1-x0)/2
    a = [math.pi*i/n for i in range(n+1)]
    for axis in (0, 1):                      # 0: triangles on the x walls, profile across y
        c, h, oc, oh = (yc, hy, xc, hx) if axis == 0 else (xc, hx, yc, hy)
        prof = [(c + h*math.cos(t), zs + rise*math.sin(t)) for t in a]
        for sgn in (-1, 1):                  # wall at oc + sgn*oh
            for i in range(n):
                (u0, z0), (u1, z1) = prof[i], prof[i+1]
                # Diagonal: |v - oc|/oh = |u - c|/h; the strip runs from the wall to it.
                d0, d1 = oh*abs(u0 - c)/h, oh*abs(u1 - c)/h
                uv = [(u0, oc + sgn*oh), (u1, oc + sgn*oh), (u1, oc + sgn*d1), (u0, oc + sgn*d0)]
                if abs(d0 - oh) < 1e-6:
                    uv.pop(3)
                elif abs(d1 - oh) < 1e-6:
                    uv.pop(2)
                poly =ccw([(v, u) for u, v in uv]) if axis == 0 else ccw(list(uv))
                s = (z1 - z0) / (u1 - u0)
                zf = (lambda x, y, u0=u0, z0=z0, s=s: z0 + s*((y if axis == 0 else x) - u0))
                nb = (0, s, -1) if axis == 0 else (s, 0, -1)
                W(_slab(poly, zf, nb, top, tex))
    W(box(x0, y0, top, x1, y1, top + WALL, tex))


def _slab(poly, zf, nb, top, tex):
    """Convex xy polygon (ccw) from the plane z = zf(x, y) (outward normal nb) up to top."""
    r = lambda v: round(v, 2)
    s = side([(r(x), r(y), top) for x, y in poly], (0, 0, 1), tex)
    s += side([(r(x), r(y), r(zf(x, y))) for x, y in poly], nb, tex)
    for i in range(len(poly)):
        a, b = poly[i], poly[(i+1) % len(poly)]
        n = (b[1]-a[1], -(b[0]-a[0]), 0)
        s += side([(r(a[0]), r(a[1]), r(zf(*a))), (r(b[0]), r(b[1]), r(zf(*b))), (r(b[0]), r(b[1]), top)], n, tex)
    return "solid\n{\n\t\"id\" \"%d\"\n%s}\n" % (nid(), s)

