"""Scaled SVG drawings for the AMR design proposal.
Robot frame: x forward (+ = front), y left (+ = left), z up. Units: mm.
All geometry comes from the constants below so the PDF and the later 3D model agree.
"""
import math

# ---------------- master parameters ----------------
L, W, H = 813, 584, 305            # shell envelope (32 x 23 x 12 in)
SKL, SKW = 800, 570                 # skeleton outer
SX, SY = L / 2, W / 2               # shell half sizes 406.5, 292
KX, KY = SKL / 2, SKW / 2           # skeleton half sizes 400, 285
CH_F, CH_R = 93, 63                 # shell chamfer legs front / rear
KCH_F, KCH_R = 90, 60               # skeleton chamfer legs
GC = 40                             # ground clearance (base plate underside)
Z_MID = 185                         # top of lower bay / mid plate
Z_BAND = 240                        # bottom of upper section
# RPLIDAR A2M12 (Slamtec datasheet fig 5-1): body D76 x 41, fixed base 18.6, rotor D72.5,
# scan plane 31 above base, 4 x M3 (max 4 mm deep) on R29.5
LID_D, LID_H, LID_BASE_H, LID_SCAN = 76, 41, 18.6, 31
Z_LID = 182                         # lidar base, recessed 3 mm below the mid plate
Z_SCAN = Z_LID + LID_SCAN           # 213 = centre of the 186.5-240 band
TUBE = 25
SLOPE = 60                          # front upper face set-back at the top
# DFRobot M0601 (dimension diagram): tyre D100.7, overall width 65.5, single-sided boss
WHL_D, WHL_W = 100.7, 65.5
DRV_Y, DRV_R = 185, 75              # drive module centre y, envelope radius (user 15 cm)
SWEEP_R = 64                        # real swept radius of wheel + hanger about the steering axis
STP_Y, STP_L = 55, 51               # steering stepper centre y; 23HS5628 body length (store)
CAS_X, CAS_Y, CAS_R = 260, 175, 85  # caster centres and swivel radius
BAT_X0, BAT_X1 = 112, 192           # battery bay x span (front; rear mirrored)
# corner posts 25x25 on the side rails where the chamfers start (clear of caster swivel + front slope)
POSTS = [(297.5, 272.5), (297.5, -272.5), (-327.5, 272.5), (-327.5, -272.5)]
MIDX_X = 62                          # mid cross-members (LiDAR plate + guide-rod tops)
TOP_XF, TOP_CH = 345, 35             # top ring: front outer x (behind the slope), front chamfer

C = dict(ink="#1f2937", mute="#6b7280", shell="#eef0f3", shell2="#dfe3e8", dark="#2b2f36",
         ms="#c2410c", buy="#2563eb", buyf="#dbeafe", prt="#15803d", prtf="#dcfce7",
         amber="#f59e0b", red="#dc2626", gold="#b8860b", hid="#9ca3af", plate="#f8fafc")

FONT = "font-family:Helvetica Neue,Helvetica,Arial,sans-serif"


def svg(vb, body, w="100%"):
    x0, y0, vw, vh = vb
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {vw} {vh}" width="{w}" '
            f'style="{FONT}">'
            '<defs><pattern id="haz" width="16" height="16" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
            '<rect width="16" height="16" fill="#facc15"/><rect width="8" height="16" fill="#111"/></pattern>'
            '<marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{C["mute"]}"/></marker></defs>'
            f'{body}</svg>')


def rect(x0, y0, x1, y1, fill="none", stroke=C["ink"], sw=1.5, rx=0, dash=None, op=1):
    x, y = min(x0, x1), min(y0, y1)
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{abs(x1-x0):.1f}" height="{abs(y1-y0):.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" opacity="{op}"{d}/>')


def circ(cx, cy, r, fill="none", stroke=C["ink"], sw=1.5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


def poly(pts, fill="none", stroke=C["ink"], sw=1.5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<polygon points="{p}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


def line(x0, y0, x1, y1, stroke=C["ink"], sw=1.5, dash=None, marker=False):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = ' marker-start="url(#ar)" marker-end="url(#ar)"' if marker else ""
    return f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{stroke}" stroke-width="{sw}"{d}{m}/>'


def text(x, y, s, size=15, fill=C["ink"], anchor="middle", weight=400, rot=None):
    t = f' transform="rotate({rot} {x:.1f} {y:.1f})"' if rot is not None else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}" dominant-baseline="middle"{t}>{s}</text>')


def tag(x, y, n, col=C["ink"]):
    """numbered callout bubble"""
    return circ(x, y, 11, fill=col, stroke="white", sw=1.5) + text(x, y + 0.5, n, 12, "white", weight=700)


def dim_h(x0, x1, y, label, off=0):
    return (line(x0, y - 8, x0, y + 8, C["mute"], 1) + line(x1, y - 8, x1, y + 8, C["mute"], 1) +
            line(x0, y, x1, y, C["mute"], 1, marker=True) + text((x0 + x1) / 2, y - 12 + off, label, 14, C["mute"]))


def dim_v(x, y0, y1, label, side=1):
    return (line(x - 8, y0, x + 8, y0, C["mute"], 1) + line(x - 8, y1, x + 8, y1, C["mute"], 1) +
            line(x, y0, x, y1, C["mute"], 1, marker=True) +
            text(x + 14 * side, (y0 + y1) / 2, label, 14, C["mute"], anchor="start" if side > 0 else "end"))


def outline(hx, hy, cf, cr):
    """chamfered rectangle in plan (x forward, y left) -> list of (x, y)"""
    return [(hx, hy - cf), (hx, -hy + cf), (hx - cf, -hy), (-hx + cr, -hy), (-hx, -hy + cr),
            (-hx, hy - cr), (-hx + cr, hy), (hx - cf, hy)]


def lidar_elev(cx=0):
    """A2M12 in elevation: fixed base D76 x 18.6, rotor D72.5 to 41, 6 mm laser window at +31"""
    z0 = Z_LID
    o = rect(cx - LID_D / 2, -(z0 + LID_BASE_H), cx + LID_D / 2, -z0, fill="#3f4652", stroke=C["buy"], sw=1.3, rx=2)
    o += rect(cx - 36.25, -(z0 + LID_H), cx + 36.25, -(z0 + 19.6), fill=C["dark"], stroke=C["buy"], sw=1.3, rx=8)
    o += rect(cx - 26, -(z0 + LID_SCAN + 3), cx + 26, -(z0 + LID_SCAN - 3), fill="#64748b", stroke="none", rx=3)
    o += rect(cx - 45, -z0, cx + 45, -(z0 - 3), fill="#94a3b8", stroke="none")   # 3 mm mount plate
    return o


# ======================================================================
# 1. PLAN VIEW — lower bay layout (svg x = robot x, svg y = -robot y)
# ======================================================================
def plan_view():
    P = lambda pts: [(x, -y) for x, y in pts]
    b = []
    # shell + skeleton ring
    b.append(poly(P(outline(SX, SY, CH_F, CH_R)), fill=C["shell"], stroke=C["dark"], sw=2.5))
    b.append(poly(P(outline(KX, KY, KCH_F, KCH_R)), fill=C["ms"], stroke=C["ms"], sw=1, ))
    b.append(poly(P(outline(KX - TUBE, KY - TUBE, KCH_F - 10, KCH_R - 10)), fill="white", stroke=C["ms"], sw=1))
    # cross members
    for sx in (1, -1):
        b.append(rect(sx * 87.5, -(KY - TUBE), sx * 112.5, KY - TUBE, fill=C["ms"], stroke=C["ms"], sw=0.5))
    # caster pockets
    for sx in (1, -1):
        for sy in (1, -1):
            cx, cy = sx * CAS_X, -sy * CAS_Y
            b.append(rect(cx - 85, cy - 85, cx + 85, cy + 85, fill="#fff7ed", stroke=C["ms"], sw=1.2))
            b.append(circ(cx, cy, CAS_R, stroke=C["hid"], sw=1.2, dash="6 5"))
            b.append(rect(cx - 50, cy - 18, cx + 50, cy + 18, fill=C["buyf"], stroke=C["buy"], sw=1.2, rx=6))
    # drive modules
    for sy in (1, -1):
        cy = -sy * DRV_Y
        b.append(circ(0, cy, DRV_R, stroke=C["hid"], sw=1.2, dash="6 5"))
        b.append(circ(0, cy, SWEEP_R, stroke=C["hid"], sw=0.8, dash="2 3"))
        b.append(rect(-75, -sy * 25, 75, -sy * 235, fill="none", stroke=C["ms"], sw=1.2, dash="3 3"))  # carriage
        # M0601: tyre 50 wide centred on the steering axis, boss + hanger on the inboard side
        b.append(rect(-WHL_D / 2, -sy * (DRV_Y - 25), WHL_D / 2, -sy * (DRV_Y + 25), fill=C["buyf"], stroke=C["buy"], sw=1.5, rx=10))
        b.append(rect(-12, -sy * (DRV_Y - 33), 12, -sy * (DRV_Y - 25), fill=C["buy"], stroke="none"))  # boss
        b.append(rect(-30, -sy * (DRV_Y - 39), 30, -sy * (DRV_Y - 33), fill=C["ms"], stroke="none"))   # hanger
        b.append(circ(0, cy, 48, stroke=C["ink"], sw=1, dash="4 3"))            # 60T pulley
        b.append(circ(0, cy, 21, fill="white", stroke=C["ink"], sw=1.2))        # cartridge
        sy_ = -sy * STP_Y
        b.append(rect(-28.5, sy_ - 28.5, 28.5, sy_ + 28.5, fill=C["buyf"], stroke=C["buy"], sw=1.5))  # NEMA23 57 sq
        b.append(circ(0, sy_, 12, stroke=C["ink"], sw=1))
        # belt tangents
        for s in (1, -1):
            b.append(line(s * 12, sy_, s * 48, cy, C["ink"], 1))
        for rx_ in (-62, 62):
            b.append(circ(rx_, -sy * 120, 6, fill=C["ink"], stroke="none", sw=0))  # guide rods
    # battery bays
    for sx in (1, -1):
        b.append(rect(sx * BAT_X0, -90, sx * BAT_X1, 90, fill="none", stroke=C["prt"], sw=1.2, dash="5 4"))
        b.append(rect(sx * 128, -77, sx * 176, 77, fill="#fde68a", stroke="#92400e", sw=1.5, rx=3))
    # front power bay: 2x TB6600, relay, fuse, speaker
    b.append(rect(200, -90, 372, 90, fill="none", stroke=C["prt"], sw=1.2, dash="5 4"))
    for y0 in (8, -79):
        b.append(rect(212, y0, 308, y0 + 71, fill=C["buyf"], stroke=C["buy"], sw=1.2))
    b.append(rect(320, -80, 352, -35, fill=C["buyf"], stroke=C["buy"], sw=1.2))
    b.append(rect(320, 35, 352, 80, fill=C["buyf"], stroke=C["buy"], sw=1.2))
    b.append(rect(356, -20, 372, 20, fill=C["buyf"], stroke=C["buy"], sw=1.2))
    # rear MCU / PCB bay
    b.append(rect(-372, -90, -200, 90, fill="none", stroke=C["prt"], sw=1.2, dash="5 4"))
    b.append(rect(-325.6, -80, -224, -26.7, fill=C["buyf"], stroke=C["buy"], sw=1.2))   # Mega 101.6 x 53.3
    b.append(rect(-367, 20, -222, 85, fill=C["plate"], stroke=C["buy"], sw=1.2))        # vero 145 x 65
    for i in range(3):
        b.append(rect(-366, -78 + i * 16, -347.7, -67.8 + i * 16, fill=C["buyf"], stroke=C["buy"], sw=1))  # 5V3A 18.3x10.2
    b.append(rect(-366, -28, -334, -8, fill=C["buyf"], stroke=C["buy"], sw=1))   # 5.1V 5A buck (est.)
    b.append(rect(-320, -18, -265, 12, fill=C["buyf"], stroke=C["buy"], sw=1))   # USB hub (est.)
    b.append(rect(-262, -20, -202, -2, fill=C["buyf"], stroke=C["buy"], sw=1))   # RS485 60 x 18
    b.append(rect(-255, 2, -215, 16, fill=C["buyf"], stroke=C["buy"], sw=1))     # USB audio
    # charge funnel (rear centre)
    b.append(rect(-SX - 4, -60, -368, 60, fill=C["prtf"], stroke=C["prt"], sw=1.5))
    for y in (-40, 40):
        b.append(circ(-390, y, 6, fill=C["gold"], stroke="none"))
    # Pi (rear-left) + port cover
    b.append(rect(-158, -285, -102, -200, fill="#ecfccb", stroke="#3f6212", sw=1.5, rx=3))
    b.append(rect(-180, -SY - 10, -80, -SY, fill=C["prtf"], stroke=C["prt"], sw=1.5))
    # Display (front-right)
    b.append(rect(87, 272, 173, 285, fill=C["buyf"], stroke=C["buy"], sw=1.5))
    b.append(rect(77, SY, 183, SY + 6, fill=C["prtf"], stroke=C["prt"], sw=1.5))
    # sonars
    for y in (150, -150):
        b.append(rect(384, -y - 23, 400, -y + 23, fill=C["buyf"], stroke=C["buy"], sw=1))
        b.append(rect(-400, -y - 23, -384, -y + 23, fill=C["buyf"], stroke=C["buy"], sw=1))
    for x in (250, -250):
        for s in (1, -1):
            b.append(rect(x - 23, s * 285, x + 23, s * 269, fill=C["buyf"], stroke=C["buy"], sw=1))
    # IMU, lidar (above), posts
    b.append(rect(-10, -10, 10, 10, fill=C["buy"], stroke="none"))
    b.append(circ(0, 0, 38, stroke=C["buy"], sw=1.5, dash="6 4"))
    for (px, py) in POSTS:
        b.append(rect(px - 12.5, -py - 12.5, px + 12.5, -py + 12.5, fill=C["ms"], stroke="none"))
    # light bars (chamfer + 100 mm side wrap)
    for sy in (1, -1):
        b.append(f'<polyline points="{SX},{-sy*(SY-CH_F)} {SX-CH_F},{-sy*SY} {SX-CH_F-100},{-sy*SY}" '
                 f'fill="none" stroke="{C["amber"]}" stroke-width="9" stroke-linecap="round"/>')
        b.append(f'<polyline points="{-SX},{-sy*(SY-CH_R)} {-SX+CH_R},{-sy*SY} {-SX+CH_R+100},{-sy*SY}" '
                 f'fill="none" stroke="{C["amber"]}" stroke-width="9" stroke-linecap="round"/>')
    # callouts
    tags = [(0, -DRV_Y - 95, 1), (0, -STP_Y + 2, 2), (CAS_X, -CAS_Y, 3), (150, 0, 4), (285, 0, 5),
            (-290, 0, 6), (-130, -243, 7), (130, 255, 8), (0, 52, 9), (-385, 0, 10), (430, 150, 11),
            (370, -255, 12), (-100, 0, 13), (100, 140, 14), (297.5, -235, 15)]
    for x, y, n in tags:
        b.append(tag(x, y, n))
    # labels & dims
    b.append(text(0, -SY - 52, "LEFT SIDE", 15, C["mute"], weight=700))
    b.append(text(0, SY + 48, "RIGHT SIDE", 15, C["mute"], weight=700))
    b.append(text(SX + 62, -10, "FRONT", 15, C["mute"], weight=700, rot=90))
    b.append(line(SX + 30, 60, SX + 30, -60, C["mute"], 1.2))
    b.append(dim_h(-SX, SX, SY + 80, "813 mm (32 in)"))
    b.append(dim_v(-SX - 45, -SY, SY, "584 mm (23 in)", side=-1))
    return svg((-SX - 175, -SY - 75, L + 290, W + 185), "".join(b))


# ======================================================================
# 2. SIDE ELEVATIONS (svg x = +-robot x, svg y = -z)
# ======================================================================
def _side(left=True):
    s = -1 if left else 1            # seen from the left the front is on the left; from the right, on the right
    X = lambda x: s * x
    b = [line(-SX - 60, 0, SX + 60, 0, C["ink"], 2)]
    b.append(f'<rect x="{-SX-60}" y="0" width="{L+120}" height="10" fill="#e5e7eb"/>')
    # hidden wheels
    b.append(circ(0, -WHL_D / 2, WHL_D / 2, stroke=C["hid"], sw=1.3, dash="6 4"))
    for x in (CAS_X, -CAS_X):
        b.append(circ(X(x), -50, 50, stroke=C["hid"], sw=1.3, dash="6 4"))
        b.append(rect(X(x) - 40, -128, X(x) + 40, -100, stroke=C["hid"], sw=1.1, dash="4 3"))
    # lower shell
    b.append(rect(-SX, -Z_MID, SX, -GC, fill=C["shell"], stroke=C["dark"], sw=2.2))
    b.append(rect(X(SX - CH_F), -Z_MID, X(SX), -GC, fill=C["shell2"], stroke=C["dark"], sw=1.2))
    b.append(rect(X(-SX + CH_R), -Z_MID, X(-SX), -GC, fill=C["shell2"], stroke=C["dark"], sw=1.2))
    # band: posts + lidar + scan plane
    for x in (POSTS[0][0], POSTS[2][0]):
        b.append(rect(X(x) - 12.5, -Z_BAND, X(x) + 12.5, -Z_MID, fill=C["ms"], stroke="none"))
    b.append(lidar_elev(0))
    b.append(line(-SX + 20, -Z_SCAN, SX - 20, -Z_SCAN, C["red"], 1.2, dash="8 5"))
    b.append(line(-SX, -Z_MID - 1, SX, -Z_MID - 1, C["dark"], 2))
    # upper shell (front slope)
    up = [(X(-SX), -Z_BAND), (X(SX), -Z_BAND), (X(SX - SLOPE), -H), (X(-SX), -H)]
    b.append(poly(up, fill=C["shell"], stroke=C["dark"], sw=2.2))
    b.append(line(X(-SX), -H + 1.5, X(SX - SLOPE), -H + 1.5, C["dark"], 3))
    # hazard strip on upper side
    b.append(rect(X(-300), -256, X(200), -244, fill="url(#haz)", stroke="none"))
    # light bars
    b.append(rect(X(SX - CH_F - 100), -180, X(SX), -165, fill=C["amber"], stroke="none", rx=3))
    b.append(rect(X(-SX + CH_R + 100), -180, X(-SX), -165, fill=C["amber"], stroke="none", rx=3))
    # side sonars
    for x in (250, -250):
        b.append(rect(X(x) - 23, -150, X(x) + 23, -130, fill=C["plate"], stroke=C["buy"], sw=1))
        for o in (-13, 13):
            b.append(circ(X(x) + o, -140, 8, fill="#cbd5e1", stroke=C["buy"], sw=1))
    # corner bumpers
    for x0, x1 in ((SX - CH_F, SX), (-SX + CH_R, -SX)):
        b.append(rect(X(x0), -78, X(x1), -GC, fill=C["prtf"], stroke=C["prt"], sw=1.2))
    if left:   # Pi port cover
        b.append(rect(X(-180), -163, X(-80), -103, fill=C["prtf"], stroke=C["prt"], sw=1.8, rx=6))
        for x, z in ((-172, -155), (-88, -155), (-172, -111), (-88, -111)):
            b.append(circ(X(x), z, 3.2, fill=C["ink"], stroke="none"))
        b.append(rect(X(-160), -146, X(-100), -120, fill="#d1d5db", stroke=C["mute"], sw=1, dash="3 2"))
        b.append(tag(X(-130), -190 + 2, "P"))
    else:      # display
        b.append(rect(X(183), -160, X(77), -85, fill=C["prtf"], stroke=C["prt"], sw=1.8, rx=6))
        b.append(rect(X(166), -147, X(94), -98, fill="#0f172a", stroke=C["buy"], sw=1))
        b.append(text(X(130), -122, "3.5&quot;", 13, "#93c5fd"))
    # dims
    b.append(dim_h(-SX, SX, 40, "813"))
    for z, lab in ((GC, "40"), (Z_MID, "185"), (Z_SCAN, f"{Z_SCAN:.0f} scan"), (Z_BAND, "240"), (H, "305")):
        b.append(line(SX + 8, -z, SX + 30, -z, C["mute"], 1) if left else line(-SX - 8, -z, -SX - 30, -z, C["mute"], 1))
        b.append(text(SX + 36 if left else -SX - 36, -z, lab, 13, C["red"] if "scan" in lab else C["mute"],
                      anchor="start" if left else "end"))
    arrow_x = -SX + 60 if left else SX - 60
    b.append(text(arrow_x, 70, "⟵ FRONT" if left else "FRONT ⟶", 15, C["mute"], weight=700))
    return svg((-SX - 110, -H - 25, L + 230, H + 125), "".join(b))


def left_view():
    return _side(True)


def right_view():
    return _side(False)


# ======================================================================
# 3. FRONT / REAR ELEVATIONS (svg x = +-robot y)
# ======================================================================
def _end(front=True):
    cf = CH_F if front else CH_R
    s = 1 if front else -1           # front: svg x = y ; rear: svg x = -y
    Y = lambda y: s * y
    b = [line(-SY - 60, 0, SY + 60, 0, C["ink"], 2), f'<rect x="{-SY-60}" y="0" width="{W+120}" height="10" fill="#e5e7eb"/>']
    for sg in (1, -1):
        b.append(rect(sg * (DRV_Y - 33), -WHL_D, sg * (DRV_Y + 32.5), 0, stroke=C["hid"], sw=1.2, dash="5 4", rx=8))
    # lower
    b.append(rect(-SY, -Z_MID, SY, -GC, fill=C["shell"], stroke=C["dark"], sw=2.2))
    for sg in (1, -1):
        b.append(rect(sg * (SY - cf), -Z_MID, sg * SY, -GC, fill=C["shell2"], stroke=C["dark"], sw=1.2))
        b.append(rect(sg * (SY - cf), -180, sg * SY, -165, fill=C["amber"], stroke="none", rx=3))
        b.append(rect(sg * (SY - cf), -78, sg * SY, -GC, fill=C["prtf"], stroke=C["prt"], sw=1.2))
    # band
    for sg in (1, -1):
        b.append(rect(sg * POSTS[0][1] - 12.5, -Z_BAND, sg * POSTS[0][1] + 12.5, -Z_MID, fill=C["ms"], stroke="none"))
    b.append(lidar_elev(0))
    b.append(line(-SY + 15, -Z_SCAN, SY - 15, -Z_SCAN, C["red"], 1.2, dash="8 5"))
    b.append(line(-SY, -Z_MID - 1, SY, -Z_MID - 1, C["dark"], 2))
    # upper
    b.append(rect(-SY, -H, SY, -Z_BAND, fill="#f6f7f9" if front else C["shell"], stroke=C["dark"], sw=2.2))
    for sg in (1, -1):
        b.append(rect(sg * (SY - cf), -H, sg * SY, -Z_BAND, fill=C["shell2"], stroke=C["dark"], sw=1.2))
    b.append(line(-SY, -H + 1.5, SY, -H + 1.5, C["dark"], 3))
    # sonars
    for y in (150, -150):
        b.append(rect(y - 23, -120, y + 23, -100, fill=C["plate"], stroke=C["buy"], sw=1))
        for o in (-13, 13):
            b.append(circ(y + o, -110, 8, fill="#cbd5e1", stroke=C["buy"], sw=1))
    if front:
        b.append(text(150, -H + 14, "sloped face (≈43°)", 11, C["mute"]))
        b.append(rect(-28, -284, 28, -258, fill=C["prtf"], stroke=C["prt"], sw=1.5, rx=5))
        b.append(circ(0, -271, 8, fill="#0f172a", stroke=C["buy"], sw=1.2))
        b.append(circ(Y(-160), -270, 19.5, fill=C["red"], stroke="#7f1d1d", sw=1.5))
        b.append(circ(Y(-160), -270, 25, fill="none", stroke="#facc15", sw=4))
        b.append(circ(60, -272, 3, fill=C["ink"], stroke="none"))
        for i in range(-2, 3):
            for j in range(-2, 3):
                if i * i + j * j <= 5:
                    b.append(circ(i * 9, -118 + j * 9, 2.6, fill=C["ink"], stroke="none"))
        tags = [(0, -300 + 2, "C"), (Y(-160), -300 + 2, "E"), (60, -252, "M"), (0, -150, "S"), (150, -88, "U")]
    else:
        b.append(rect(-60, -115, 60, -70, fill=C["prtf"], stroke=C["prt"], sw=1.8, rx=8))
        b.append(rect(-52, -108, 52, -77, fill="none", stroke=C["prt"], sw=1, rx=6, dash="3 2"))
        for y in (-40, 40):
            b.append(circ(y, -92, 7, fill=C["gold"], stroke="#7c5a00", sw=1.5))
        b.append(rect(-28, -272, 28, -246, fill=C["prtf"], stroke=C["prt"], sw=1.5, rx=5))
        b.append(circ(0, -259, 8, fill="#0f172a", stroke=C["buy"], sw=1.2))
        b.append(rect(Y(-110) - 23, -272, Y(-110) + 23, -246, fill="#111", stroke=C["ink"], sw=1))
        b.append(text(Y(-110), -259, "14.8V", 11, "#ef4444", weight=700))
        for y, lb in ((-180, "MAIN"), (-215, "LOGIC")):
            b.append(circ(Y(y), -259, 6, fill="#e5e7eb", stroke=C["ink"], sw=1.2))
        b.append(circ(Y(160), -259, 19.5, fill=C["red"], stroke="#7f1d1d", sw=1.5))
        b.append(circ(Y(160), -259, 25, fill="none", stroke="#facc15", sw=4))
        tags = [(0, -132, "Q"), (0, -232, "C"), (Y(-110), -232, "V"), (Y(-197), -232, "T"), (Y(160), -296, "E")]
    for x, y, n in tags:
        b.append(tag(x, y, n))
    b.append(dim_h(-SY, SY, 40, "584"))
    return svg((-SY - 70, -H - 30, W + 140, H + 95), "".join(b))


def front_view():
    return _end(True)


def rear_view():
    return _end(False)


# ======================================================================
# 4. SECTION A-A at x = 0 (through the drive modules, looking forward)
# ======================================================================
def section_view():
    b = [line(-SY - 40, 0, SY + 40, 0, C["ink"], 2), f'<rect x="{-SY-40}" y="0" width="{W+80}" height="10" fill="#e5e7eb"/>']
    # shell walls
    for sg in (1, -1):
        b.append(rect(sg * SY, -Z_MID, sg * (SY - 1.5), -GC, fill=C["dark"], stroke="none"))
        b.append(rect(sg * SY, -H, sg * (SY - 1.5), -Z_BAND, fill=C["dark"], stroke="none"))
        # tubes
        b.append(rect(sg * KY, -67, sg * (KY - 25), -42, fill=C["ms"], stroke="none"))
        b.append(rect(sg * KY, -Z_MID, sg * (KY - 20), -165, fill=C["ms"], stroke="none"))
        b.append(rect(sg * KY, -303.5, sg * (KY - 25), -278.5, fill=C["ms"], stroke="none"))
    # plates
    b.append(rect(-KY, -41.5, -275, -40, fill=C["dark"], stroke="none"))
    b.append(rect(275, -41.5, KY, -40, fill=C["dark"], stroke="none"))
    b.append(rect(-125, -41.5, 125, -40, fill=C["dark"], stroke="none"))
    b.append(rect(-KY, -186.5, -40, -185, fill="#94a3b8", stroke="none"))
    b.append(rect(40, -186.5, KY, -185, fill="#94a3b8", stroke="none"))
    b.append(rect(-SY, -305, SY, -303.5, fill=C["dark"], stroke="none"))
    for sg in (1, -1):
        Y = lambda v: sg * v
        cy = Y(DRV_Y)
        # M0601: tyre 50 wide on the steering axis, D19 boss inboard, hub cap outboard
        b.append(rect(Y(DRV_Y - 25), -WHL_D, Y(DRV_Y + 25), 0, fill="#334155", stroke=C["ink"], sw=1.2, rx=10))
        b.append(rect(Y(DRV_Y - 25), -70, Y(DRV_Y + 25), -31, fill=C["buyf"], stroke=C["buy"], sw=1))
        b.append(rect(Y(DRV_Y + 25), -62, Y(DRV_Y + 32.5), -39, fill=C["buyf"], stroke=C["buy"], sw=1, rx=3))
        b.append(rect(Y(DRV_Y - 33), -60, Y(DRV_Y - 25), -41, fill=C["buy"], stroke="none"))
        # single-sided hanger + yoke (MS 6 mm) -> steering shaft on the tyre centreline
        b.append(rect(Y(DRV_Y - 39), -112, Y(DRV_Y - 33), -30, fill=C["ms"], stroke="none"))
        b.append(rect(Y(DRV_Y - 39), -112, Y(DRV_Y + 12), -106, fill=C["ms"], stroke="none"))
        b.append(rect(cy - 10, -181, cy + 10, -112, fill="#9ca3af", stroke=C["ink"], sw=1))     # shaft D20
        b.append(rect(cy - 21, -155, cy + 21, -115, fill="#e5e7eb", stroke=C["ink"], sw=1.2))  # 2x6004 cartridge
        b.append(rect(Y(25), -135, Y(235), -130, fill=C["ms"], stroke="none"))                  # carriage
        b.append(rect(cy - 48, -180, cy + 48, -160, fill="#cbd5e1", stroke=C["ink"], sw=1.2))  # 60T
        sx_ = Y(STP_Y)
        b.append(rect(sx_ - 31, -160, sx_ + 31, -155, fill=C["ms"], stroke="none"))             # L-bracket top
        b.append(rect(Y(STP_Y + 31), -160, Y(STP_Y + 35), -135, fill=C["ms"], stroke="none"))   # L-bracket leg
        b.append(rect(sx_ - 12, -180, sx_ + 12, -160, fill="#cbd5e1", stroke=C["ink"], sw=1.2))  # 15T
        b.append(rect(sx_ - 28.5, -155, sx_ + 28.5, -(155 - STP_L), fill=C["buyf"], stroke=C["buy"], sw=1.5))
        b.append(rect(Y(STP_Y + 12), -176, Y(DRV_Y - 48), -164, fill="#475569", stroke="none"))  # belt
        b.append(rect(Y(114), -185, Y(126), -67, fill="none", stroke=C["hid"], sw=1.2, dash="4 3"))  # rod
        for k in range(6):
            z = -150 - k * 5
            b.append(line(Y(111), z, Y(129), z - 4, C["hid"], 1))
    # lidar (recessed 3 mm into a D80 hole in the mid plate)
    b.append(lidar_elev(0))
    b.append(line(-SY + 5, -Z_SCAN, SY - 5, -Z_SCAN, C["red"], 1.3, dash="8 5"))
    b.append(rect(-12.5, -45, 12.5, -41.5, fill=C["buy"], stroke="none"))
    # height ladder
    for z, lab in ((GC, "40  ground clearance"), (WHL_D, "100.7  wheel top (M0601)"), (Z_MID, "185  lower bay top / mid plate"),
                   (Z_SCAN, f"{Z_SCAN:.0f}  lidar scan plane (base + 31)"), (Z_BAND, "240  band top / upper section"), (H, "305  deck")):
        b.append(line(SY + 6, -z, SY + 28, -z, C["red"] if z == Z_SCAN else C["mute"], 1))
        b.append(text(SY + 34, -z, lab, 13, C["red"] if z == Z_SCAN else C["mute"], anchor="start"))
    tags = [(DRV_Y, -51, 1), (DRV_Y + 50, -135, 2), (DRV_Y, -196, 3), (STP_Y, -125, 4), (120, -55, 5),
            (0, -255, 6), (0, -62, 7), (-DRV_Y, -51, 1), (-STP_Y, -125, 4), (-(DRV_Y - 36), -88, 8)]
    for x, y, n in tags:
        b.append(tag(x, y, n))
    return svg((-SY - 45, -H - 20, W + 345, H + 40), "".join(b))


# ======================================================================
# 5. ELECTRICAL BLOCK DIAGRAM
# ======================================================================
def elec_view():
    b = []

    def box(x, y, w, h, title, sub="", col=C["buy"], fill=C["buyf"]):
        out = rect(x, y, x + w, y + h, fill=fill, stroke=col, sw=1.6, rx=8)
        out += text(x + w / 2, y + (h / 2 if not sub else h / 2 - 9), title, 15, C["ink"], weight=700)
        if sub:
            out += text(x + w / 2, y + h / 2 + 11, sub, 12, C["mute"])
        return out

    def arr(x0, y0, x1, y1, col=C["ink"], lab=None, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        o = (f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="{col}" stroke-width="2"{d} '
             f'marker-end="url(#ar)"/>')
        if lab:
            o += text((x0 + x1) / 2, (y0 + y1) / 2 - 9, lab, 11, col)
        return o
    P, D = "#b45309", "#7c3aed"
    # power column
    b.append(box(20, 20, 170, 54, "Dock charge port", "16.8 V CC/CV in", C["prt"], C["prtf"]))
    b.append(box(20, 104, 170, 54, "Diode + 15 A fuse", "charge detect → Mega", P, "#fff7ed"))
    b.append(box(20, 188, 170, 64, "2 × 4S battery", "14.8 V · BMS · XT60", P, "#fde68a"))
    b.append(box(20, 282, 170, 54, "30 A main fuse", "+ MAIN toggle", P, "#fff7ed"))
    b.append(box(20, 366, 170, 64, "E-stop contactor", "2 × CR-257R in series", C["red"], "#fee2e2"))
    b.append(box(20, 460, 170, 54, "14.8 V motor bus", "", P, "#fff7ed"))
    for y0, y1 in ((74, 104), (158, 188), (252, 282), (336, 366), (430, 460)):
        b.append(arr(105, y0, 105, y1, P))
    # converters
    b.append(box(260, 188, 175, 50, "5.1 V 5 A buck", "Pi 5 (USB-C)", P, "#fff7ed"))
    b.append(box(260, 252, 175, 50, "5 V 3 A buck", "logic · sensors · hub", P, "#fff7ed"))
    b.append(box(260, 316, 175, 50, "5 V 3 A buck", "LED light bars", P, "#fff7ed"))
    b.append(box(260, 380, 175, 50, "LOGIC toggle", "feeds the 3 bucks", P, "#fff7ed"))
    b.append(arr(190, 300, 260, 405, P))
    b.append(f'<polyline points="347,380 347,370 450,370 450,213 435,213" fill="none" stroke="{P}" stroke-width="2" marker-end="url(#ar)"/>')
    b.append(arr(450, 277, 435, 277, P))
    b.append(arr(450, 341, 435, 341, P))
    # motor-side loads
    b.append(box(260, 460, 175, 54, "2 × TB6600", "steering steppers", C["buy"], C["buyf"]))
    b.append(box(260, 540, 175, 54, "2 × M0601 hub motor", "FOC · encoder · RS485", C["buy"], C["buyf"]))
    b.append(arr(190, 487, 260, 487, P))
    b.append(f'<polyline points="215,487 215,567 260,567" fill="none" stroke="{P}" stroke-width="2" marker-end="url(#ar)"/>')
    # compute
    b.append(box(520, 20, 200, 70, "Raspberry Pi 5 (8 GB)", "ROS 2 · nav · docking", "#3f6212", "#ecfccb"))
    b.append(box(520, 130, 200, 54, "Powered USB 3 hub", "7 ports, inside rear bay", C["buy"], C["buyf"]))
    b.append(arr(620, 90, 620, 130, D, "USB 3"))
    b.append(arr(435, 213, 520, 60, P))
    devs = ["RPLIDAR A2M12", "Front webcam", "Rear webcam (ArUco)", "USB–RS485", "Arduino Mega",
            "USB audio + mic", "3.5\" display touch"]
    for i, d in enumerate(devs):
        y = 220 + i * 52
        b.append(box(780, y, 190, 42, d, "", C["buy"], C["buyf"]))
        b.append(f'<polyline points="720,157 750,157 750,{y+21} 780,{y+21}" fill="none" stroke="{D}" stroke-width="1.6"/>')
    b.append(box(780, 40, 190, 50, "3.5\" HDMI display", "right side wall", C["buy"], C["buyf"]))
    b.append(arr(720, 55, 780, 65, D, "HDMI"))
    # RS485 -> motors
    b.append(f'<polyline points="780,397 750,397 750,600 470,600 470,567 435,567" fill="none" stroke="{D}" stroke-width="1.6" stroke-dasharray="6 4" marker-end="url(#ar)"/>')
    b.append(text(610, 590, "RS485 bus (IDs 1, 2)", 12, D))
    # Mega I/O
    b.append(box(480, 620, 520, 70, "Arduino Mega I/O",
                 "8 sonar · 4 bumper · IMU · 2 homing · step/dir · LEDs · e-stop/charge sense", "#3f6212", "#ecfccb"))
    b.append(f'<polyline points="970,449 1010,449 1010,640 1000,640" fill="none" stroke="{D}" stroke-width="1.6" marker-end="url(#ar)"/>')
    b.append(f'<polyline points="480,655 347,655 347,514" fill="none" stroke="{D}" stroke-width="1.6" stroke-dasharray="6 4" marker-end="url(#ar)"/>')
    b.append(text(430, 645, "STEP / DIR / EN", 12, D))
    # legend
    b.append(line(20, 640, 60, 640, P, 3) + text(68, 640, "power", 13, C["mute"], anchor="start"))
    b.append(line(20, 665, 60, 665, D, 3) + text(68, 665, "data", 13, C["mute"], anchor="start"))
    return svg((0, 0, 1030, 705), "".join(b))


if __name__ == "__main__":
    import pathlib
    out = pathlib.Path(__file__).parent / "svg"
    out.mkdir(exist_ok=True)
    for n, f in dict(plan=plan_view, left=left_view, right=right_view, front=front_view, rear=rear_view,
                     section=section_view, elec=elec_view).items():
        (out / f"{n}.svg").write_text(f())
    print("ok")
