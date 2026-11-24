"""Builds the AMR design proposal (HTML -> PDF via headless Chrome)."""
import pathlib
import subprocess
import drawings as D

HERE = pathlib.Path(__file__).parent
OUT_HTML = HERE / "proposal.html"
OUT_PDF = HERE.parent / "AMR_Design_Proposal_RevB.pdf"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CSS = """
@page { size: A4; margin: 0; }
* { box-sizing: border-box; }
body { margin: 0; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #1f2937; font-size: 9.6pt; line-height: 1.42; }
.page { width: 210mm; height: 297mm; padding: 14mm 15mm 16mm; position: relative; page-break-after: always; overflow: hidden; }
.page:last-child { page-break-after: auto; }
.foot { position: absolute; bottom: 8mm; left: 15mm; right: 15mm; display: flex; justify-content: space-between; font-size: 7.5pt; color: #9ca3af; border-top: 0.3mm solid #e5e7eb; padding-top: 2mm; }
h1 { font-size: 25pt; line-height: 1.1; margin: 0 0 3mm; letter-spacing: -0.3px; }
h2 { font-size: 14pt; margin: 0 0 3mm; padding-bottom: 1.5mm; border-bottom: 0.6mm solid #111; display: flex; gap: 3mm; align-items: baseline; }
h2 .n { color: #f59e0b; }
h3 { font-size: 10.5pt; margin: 4mm 0 1.5mm; }
p { margin: 0 0 2.2mm; }
.kicker { font-size: 8.5pt; letter-spacing: 1.6px; text-transform: uppercase; color: #6b7280; font-weight: 700; }
.lede { font-size: 11pt; color: #374151; max-width: 160mm; }
table { width: 100%; border-collapse: collapse; margin: 1mm 0 3mm; font-size: 8.4pt; }
th { text-align: left; background: #111827; color: #fff; font-weight: 600; padding: 1.4mm 2mm; }
td { padding: 1.3mm 2mm; border-bottom: 0.25mm solid #e5e7eb; vertical-align: top; }
tr:nth-child(even) td { background: #f9fafb; }
td.num, th.num { text-align: right; white-space: nowrap; }
.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 6mm; }
.grid3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 3mm; }
.spec { border: 0.3mm solid #e5e7eb; border-radius: 2mm; padding: 2.5mm 3mm; }
.spec b { display: block; font-size: 13pt; }
.spec span { font-size: 7.8pt; color: #6b7280; text-transform: uppercase; letter-spacing: 0.6px; }
.fig { border: 0.3mm solid #e5e7eb; border-radius: 2mm; padding: 2mm; margin: 0 0 2mm; }
.cap { font-size: 7.8pt; color: #6b7280; margin: 0 0 3mm; }
.note { background: #fffbeb; border-left: 1mm solid #f59e0b; padding: 2mm 3mm; margin: 2mm 0 3mm; font-size: 8.8pt; }
.warn { background: #fef2f2; border-left: 1mm solid #dc2626; padding: 2mm 3mm; margin: 2mm 0 3mm; font-size: 8.8pt; }
.ok { background: #f0fdf4; border-left: 1mm solid #15803d; padding: 2mm 3mm; margin: 2mm 0 3mm; font-size: 8.8pt; }
.legend { columns: 2; column-gap: 6mm; font-size: 8.3pt; margin: 0; padding: 0; list-style: none; }
.legend li { break-inside: avoid; margin: 0 0 1.4mm; display: flex; gap: 2mm; }
.b { display: inline-flex; min-width: 4.6mm; height: 4.6mm; border-radius: 50%; background: #1f2937; color: #fff; font-size: 7pt; font-weight: 700; align-items: center; justify-content: center; flex: none; }
.keys { display: flex; flex-wrap: wrap; gap: 4mm; font-size: 7.8pt; color: #4b5563; margin: 1mm 0 2mm; }
.keys i { display: inline-block; width: 4mm; height: 3mm; vertical-align: -0.4mm; margin-right: 1.2mm; border-radius: 0.6mm; }
.tag { display: inline-block; font-size: 7pt; font-weight: 700; padding: 0.3mm 1.6mm; border-radius: 1mm; }
.t-chg { background: #fef3c7; color: #92400e; } .t-add { background: #dbeafe; color: #1e40af; } .t-keep { background: #dcfce7; color: #166534; } .t-drop { background: #fee2e2; color: #991b1b; }
.cover-band { height: 5mm; background: repeating-linear-gradient(45deg, #facc15 0 5mm, #111 5mm 10mm); margin: 0 -15mm 8mm; }
ol.steps { margin: 0; padding-left: 5mm; } ol.steps li { margin-bottom: 1.6mm; }
.small { font-size: 8pt; color: #6b7280; }
table.dense { font-size: 7.6pt; } table.dense td { padding: 0.8mm 1.6mm; line-height: 1.28; }
.fig.narrow { width: 78%; margin-left: auto; margin-right: auto; }
"""

KEYS = """<div class="keys"><span><i style="background:#c2410c"></i>MS skeleton</span><span><i style="background:#dbeafe;border:1px solid #2563eb"></i>Bought part (BOM)</span>
<span><i style="background:#dcfce7;border:1px solid #15803d"></i>3D-printed part</span><span><i style="background:#f59e0b"></i>LED light bar</span>
<span><i style="background:#eef0f3;border:1px solid #2b2f36"></i>Outer shell</span><span><i style="border:1px dashed #9ca3af"></i>Hidden / swept</span>
<span><i style="background:#dc2626;height:1px"></i>LiDAR scan plane</span></div>"""


def page(n, body, title="ACI · Indoor AMR — Design Proposal Rev B"):
    return f'<section class="page">{body}<div class="foot"><span>{title}</span><span>24 Nov 2026 · page {n}</span></div></section>'


def legend(items):
    return '<ul class="legend">' + "".join(f'<li><span class="b">{k}</span><span>{v}</span></li>' for k, v in items) + "</ul>"


pages = []

# ---------------- 1. cover ----------------
pages.append(page(1, f"""
<div class="cover-band"></div>
<div class="kicker">ACI · AGV Design · Rev B for review (part dimensions checked against the BOM links)</div>
<h1>Indoor AMR, 30 kg class<br>Design proposal</h1>
<p class="lede">A steered-hub-wheel AMR in an H layout, built on a welded mild-steel skeleton with bolt-on shells and a full-perimeter LiDAR band. It is sized to your 32 × 23 × 12 in envelope and built from the parts in <i>AGV Budget Plan.xlsx</i>.</p>
<div class="grid3" style="margin:5mm 0 4mm">
 <div class="spec"><span>Envelope (L × W × H)</span><b>813 × 584 × 305 mm</b></div>
 <div class="spec"><span>Payload (rated / frame)</span><b>30 kg / 60 kg</b></div>
 <div class="spec"><span>Robot mass (est.)</span><b>≈ 46 kg</b></div>
 <div class="spec"><span>Drive</span><b>2 × M0601, stepper-steered</b></div>
 <div class="spec"><span>Top speed (14.8 V)</span><b>≈ 0.5 m/s</b></div>
 <div class="spec"><span>LiPo runtime (driving)</span><b>≈ 1.8 h</b></div>
</div>
<div class="fig">{D.left_view()}</div>
<p class="cap">Left elevation, to scale. Lower bay (40–185 mm), open LiDAR band (185–240 mm, only the 4 corner posts cross it) and upper section with deck (240–305 mm). The front upper face is sloped; the Pi 5 port cover (P) sits on the left wall.</p>
<h3>What this proposal asks you to decide</h3>
<ol class="steps">
 <li><b>Casters:</b> 100 mm (4 in) low-profile casters to match the 100.7 mm drive wheel, instead of 6 in (§1).</li>
 <li><b>Battery for auto-docking:</b> the LiPo packs need a BMS before the dock can charge them unattended (§6).</li>
 <li><b>Payload:</b> the BOM is sized for 20–30 kg. A higher payload needs a different drive motor (§9).</li>
</ol>
"""))

# ---------------- 2. design basis & changes ----------------
pages.append(page(2, """
<h2><span class="n">1</span>Design basis and recommended changes</h2>
<p style="font-size:8.8pt">The brief and the spreadsheet differ in a few places. This table shows how each one is settled. <span class="tag t-keep">KEEP</span> follows your brief, <span class="tag t-chg">CHANGE</span> is a recommendation, <span class="tag t-add">ADD</span> is a part missing from the BOM and <span class="tag t-drop">DROP</span> removes a BOM line.</p>
<table class="dense">
<tr><th style="width:17%">Topic</th><th style="width:25%">Brief / BOM says</th><th style="width:29%">Proposal</th><th>Why</th></tr>
<tr><td><b>Envelope</b> <span class="tag t-keep">KEEP</span></td><td>Brief 32×23×12 in. BOM chassis tab costed 600×450 mm.</td><td>813 × 584 × 305 mm shell, 800 × 570 mm skeleton.</td><td>At 700×500 the caster swivel circles hit the battery bays. Steel quantity in the Chassis tab must go up (§10).</td></tr>
<tr><td><b>Drive wheel</b> <span class="tag t-keep">KEEP</span></td><td>Brief: 15×15×12 cm. BOM: M0601 hub motor, Ø100.7 × 65.5 mm wide.</td><td>15×15×12 cm is the <b>steered module envelope</b> (Ø150 × 120 high). The real wheel + hanger sweeps Ø128.</td><td>The M0601 is in stock and has FOC, an encoder and RS485 built in. A true 150 mm drive wheel needs a different motor (§9).</td></tr>
<tr><td><b>Casters</b> <span class="tag t-chg">CHANGE</span></td><td>Brief: 6 in, same as drive wheel. BOM: 5 in.</td><td><b>100 mm (4 in)</b> PU swivel casters, about 125–130 mm overall height, plate mount.</td><td>A 6 in caster is about 190 mm tall. Its mounting plate would sit inside the LiDAR band. 4 in matches the drive wheel and keeps the frame level.</td></tr>
<tr><td><b>Wheel layout</b> <span class="tag t-keep">KEEP</span></td><td>H shape: 4 casters at the corners, drive wheels mid-left and mid-right.</td><td>Casters at x = ±260, y = ±175 mm. Drive modules at x = 0, y = ±185 mm.</td><td>The steered wheels also allow sideways (crab) moves, which help with dock alignment.</td></tr>
<tr><td><b>Drive suspension</b> <span class="tag t-chg">CHANGE</span></td><td>BOM: hinged motor plates with springs.</td><td><b>Vertical-slide carriage</b>: 2 × Ø12 rods, LM12UU bushings, 2 springs, ±10 mm travel.</td><td>A hinge tilts the steering axis as it moves. A slide keeps it vertical. Spring preload of about 80 N per wheel stays under the M0601's ~10 kg wheel-load limit.</td></tr>
<tr><td><b>Steering pivot</b> <span class="tag t-chg">CHANGE</span></td><td>BOM: 2 × UCFL204 + thrust bearing.</td><td>2 × 6004-2RS in a welded cartridge + 51104 thrust. 4:1 HTD-5M belt at 130 mm centres.</td><td>A stack of two UCFL204s is about 70 mm tall and would push the 60T pulley into the LiDAR band. The cartridge keeps the whole module below 181 mm.</td></tr>
<tr><td><b>Shell</b> <span class="tag t-chg">CHANGE</span></td><td>BOM: SS304 1 mm panels, 2 mm deck.</td><td>Panels in 1.2 mm CRCA, laser-cut, bent and powder-coated matte black. Deck 1.5 mm SS304 + rubber mat.</td><td>Matches the black reference look, costs less and is easier to bend. Saves about 2 kg on the deck.</td></tr>
<tr><td><b>Signal tower</b> <span class="tag t-drop">DROP</span></td><td>BOM row 24.</td><td>Use the 4 corner light bars instead.</td><td>A tower on the deck breaks the flat payload surface.</td></tr>
<tr><td><b>LED strip</b> <span class="tag t-keep">KEEP</span></td><td>WS2812B, 30 LED/m (IP67).</td><td>4 corner bars (front L/R, rear L/R) from the BOM strip: 7 LEDs front, 6 rear.</td><td>RoboticsBD lists no 60/m strip. 30/m is enough for indication; a 60/m strip from another shop would double the density.</td></tr>
<tr><td><b>3.5 in display</b> <span class="tag t-add">ADD</span></td><td>Not in BOM.</td><td>3.5 in <b>HDMI</b> touch LCD (USB touch) on the right wall.</td><td>An SPI/GPIO display has to plug onto the Pi header, but the Pi is on the opposite (left) wall. HDMI works over a 0.6 m cable.</td></tr>
<tr><td><b>Pi 5 power</b> <span class="tag t-add">ADD</span></td><td>Row 8 refers to "row 25", which is missing.</td><td>5.1 V 5 A buck (USB-C) + Pi active cooler.</td><td>The 5 V 3 A modules in the BOM cannot power a Pi 5 under load.</td></tr>
<tr><td><b>USB ports</b> <span class="tag t-add">ADD</span></td><td>Pi 5 has 4 USB ports.</td><td>Powered 7-port USB 3 hub in the rear bay.</td><td>7 USB devices: LiDAR, 2 webcams, RS485, Mega, audio, touch.</td></tr>
<tr><td><b>Audio</b> <span class="tag t-add">ADD</span></td><td>Brief: audio output + microphone.</td><td>USB sound card + MEMS/USB mic + PAM8403 amp + 40 mm 3 W speaker.</td><td>The Pi 5 has no 3.5 mm audio jack.</td></tr>
<tr><td><b>E-stop</b> <span class="tag t-add">ADD</span></td><td>2 × CR-257R (5 A).</td><td>Both in series, driving a 40 A DC contactor on the motor bus. Plus a 30 A main fuse.</td><td>As the BOM notes, a 5 A switch cannot carry the motor current. The contactor cuts drive power only; the Pi keeps running.</td></tr>
<tr><td><b>Dock charging</b> <span class="tag t-add">ADD</span></td><td>BOM: 2 × 4S LiPo + IMAX B6 bench charger.</td><td>4S BMS (or Li-ion packs with BMS), 16.8 V 5 A dock charger, contacts, funnel.</td><td>LiPo packs must not be charged unattended through 2 dock pins without balancing and protection (§6).</td></tr>
</table>
"""))

# ---------------- 3. plan layout ----------------
pages.append(page(3, f"""
<h2><span class="n">2</span>Internal layout — plan view of the lower bay</h2>
{KEYS}
<div class="fig">{D.plan_view()}</div>
<p class="cap">Plan section at about z = 120 mm, to scale, front to the right. The skeleton bottom ring and the 2 cross-members form 5 bays: front power, front battery, drive bay (centre), rear battery and rear MCU/PCB. The corner posts stand on the side rails where the chamfers start.</p>
{legend([
 (1, "Drive module L/R at y = ±185: M0601 on a single-sided hanger (red bar), Ø150 envelope / Ø128 real sweep, vertical-slide carriage (● = guide rods)"),
 (2, "Steering stepper NEMA 23 (23HS5628), 15T → 60T HTD-5M belt, 4:1"),
 (3, "4 × 100 mm swivel casters in welded 5 mm pockets (Ø170 swivel circle)"),
 (4, "Battery bays, 180 × 80 × 75 mm: fit a 4S 4200 LiPo or a 4S Li-ion pack, strapped on foam"),
 (5, "Front power bay: 2 × TB6600, E-stop contactor, main fuse, speaker behind the grille"),
 (6, "Rear MCU/PCB bay: Arduino Mega, I/O vero board, 4 bucks, USB hub, RS485 and audio"),
 (7, "Raspberry Pi 5, rear-left. The USB/Ethernet edge faces the left wall behind the printed cover"),
 (8, "3.5 in HDMI touch display, front-right wall, printed bezel"),
 (9, "MPU-9250 IMU on the base plate at the centre, under the LiDAR (use gyro + accel only)"),
 (10, "Charge funnel and 2 female contacts, rear centre, z = 92 mm"),
 (11, "8 × HC-SR04: 2 front, 2 rear, 2 per side"),
 (12, "Light bars at the 4 corners: chamfer plus a 100 mm wrap onto the side"),
 (13, "Bottom cross-members x = ±100 mm: carry the battery trays, guide-rod brackets and base plate"),
 (14, "LiPo/Li-ion straps and the cable trunk run along the cross-members"),
 (15, "Corner posts 25×25 (4 only) on the side rails, clear of the caster swivel circles. They are the only parts that cross the LiDAR band"),
])}
"""))

# ---------------- 4. height stack & drive module ----------------
pages.append(page(4, f"""
<h2><span class="n">3</span>Height stack and steered drive module</h2>
<div class="fig">{D.section_view()}</div>
<p class="cap">Section A–A at x = 0 through both drive modules, looking forward, to scale.
<span class="b">1</span> M0601 Ø100.7 × 65.5 hub wheel &nbsp;<span class="b">8</span> 6 mm MS hanger + yoke bolted to the Ø19 boss (3 × M2.5) &nbsp;<span class="b">2</span> carriage plate 5 mm, rides on the guide rods &nbsp;<span class="b">3</span> 60T pulley above the bearing cartridge, max height 181 mm &nbsp;<span class="b">4</span> NEMA 23 (57 sq × 51) hanging under its L-bracket &nbsp;<span class="b">5</span> Ø12 guide rod + spring &nbsp;<span class="b">6</span> RPLIDAR A2M12, base recessed 3 mm into the mid plate &nbsp;<span class="b">7</span> IMU.</p>
<div class="grid2">
<div>
<h3>Vertical budget (305 mm total)</h3>
<table>
<tr><th>Zone</th><th class="num">z (mm)</th><th>Contents</th></tr>
<tr><td>Ground clearance</td><td class="num">0–40</td><td>Caster and drive wheels only</td></tr>
<tr><td>Lower bay</td><td class="num">40–185</td><td>Batteries, drive modules, all electronics, Pi, display, sonars</td></tr>
<tr><td>LiDAR band (open)</td><td class="num">185–240</td><td>LiDAR alone. 4 corner posts; cables run inside the posts</td></tr>
<tr><td>Upper section</td><td class="num">240–305</td><td>Front + rear camera, 2 e-stops, toggles, voltmeter, top ring, deck</td></tr>
</table>
<p>The scan plane sits at <b>213 mm</b>, the middle of the 53.5 mm opening (Slamtec: scan plane = base + 31 mm, 6 mm laser window). That leaves room for the A2's ±1.5° scan tilt out to the shell edge. The 4 posts cast 4 shadows of about 5° each, so about 340° of the scan is usable. Low obstacles below 213 mm are covered by the 8 sonars at 110–140 mm and the corner bumpers.</p>
<div class="note">From the Slamtec drawing: body Ø76 × 41 mm, fixed base 18.6 mm, rotor Ø72.5 mm, 4 × M3 on an R29.5 circle (screws must not go deeper than 4 mm). The LiDAR sits on a 3 mm plate under a Ø80 hole in the mid plate, base at z = 182, so the window is centred in the band.</div>
</div>
<div>
<h3>Drive module (×2, mirrored)</h3>
<table>
<tr><th>Part</th><th>Spec</th></tr>
<tr><td>Hub motor</td><td>DFRobot M0601 L/R: tyre Ø100.7, 65.5 wide, 765 g, 10 kg wheel load, 18 V, 0.96 / 2.0 N·m, RS485, 255 mm cable out of the boss</td></tr>
<tr><td>Hanger</td><td><b>Single-sided</b>: the motor fixes only by its Ø19 boss (Ø15.2 D-pilot, 3 × M2.5 × 5 deep). 6 mm MS hanger + yoke puts the Ø20 steering shaft on the tyre centreline</td></tr>
<tr><td>Bearings</td><td>2 × 6004-2RS (40 mm apart) in a welded tube cartridge, 51104 thrust under the yoke</td></tr>
<tr><td>Steering drive</td><td>23HS5628 + TB6600, HTD-5M 15 mm belt 15T:60T, 130 mm centres, about 2 N·m at the wheel</td></tr>
<tr><td>Homing</td><td>LJ12A3-4 inductive sensor reading a flag on the 60T pulley</td></tr>
<tr><td>Suspension</td><td>Vertical slide: 2 × Ø12 rods, LM12UU, springs preloaded to about 80 N, ±10 mm</td></tr>
<tr><td>Stepper</td><td>23HS5628: 57 × 57 × 51 mm, Ø8 × 20.6 shaft, 650 g, on the 50 × 62 × 64 L-bracket</td></tr>
<tr><td>Envelope</td><td>Ø128 real sweep (Ø150 allowed) × 120 high, 150 × 220 mm with the stepper</td></tr>
</table>
<div class="note">The steppers sit <b>inboard</b> at y = ±55 mm, below the mid plate, so nothing in the drive train enters the LiDAR band. The mid plate has 2 relief cut-outs over the 60T pulleys for the top of the suspension travel.</div>
</div></div>
"""))

# ---------------- 5. skeleton & shell ----------------
pages.append(page(5, """
<h2><span class="n">4</span>MS skeleton, shells and printed parts</h2>
<p>Everything bolts to the <b>skeleton</b>: motor carriages, casters, trays, posts, shells and the deck. The skeleton is one welded mild-steel frame made of three rings joined by four corner posts. It is powder-coated after welding and fitted with M5 rivet nuts so every other part can be removed with a hex key.</p>
<div class="grid2"><div>
<h3>Skeleton members</h3>
<table>
<tr><th>Member</th><th>Section</th><th class="num">Length</th></tr>
<tr><td>Bottom ring (z 42–67), chamfered 90/60</td><td>25×25×1.5</td><td class="num">≈ 2.65 m</td></tr>
<tr><td>Bottom cross-members x = ±100</td><td>25×25×1.5</td><td class="num">2 × 0.52 m</td></tr>
<tr><td>Mid ring (z 165–185)</td><td>20×20×1.5</td><td class="num">≈ 2.65 m</td></tr>
<tr><td>Mid cross-members x = ±62 (LiDAR plate + rod tops)</td><td>20×20×1.5</td><td class="num">2 × 0.52 m</td></tr>
<tr><td>Corner posts (z 42–303) on the side rails at the chamfer starts, cables inside</td><td>25×25×1.5</td><td class="num">4 × 0.26 m</td></tr>
<tr><td>Top ring (z 278–303), front at x = 345 behind the slope, 35 mm chamfers</td><td>25×25×1.5</td><td class="num">≈ 2.55 m</td></tr>
<tr><td>Deck cross tubes</td><td>25×25×1.5</td><td class="num">2 × 0.52 m</td></tr>
<tr><td>Caster pockets (×4), carriage brackets (×4)</td><td>5 mm plate</td><td class="num">—</td></tr>
<tr><td><b>Total tube</b></td><td></td><td class="num"><b>≈ 13.3 m → 3 × 20 ft</b></td></tr>
</table>
<h3>Joining rules</h3>
<ul class="small" style="padding-left:4mm;margin:0">
<li>Weld on a flat jig plate. Tack all 4 posts, check diagonals (≤ 2 mm difference), then finish the welds.</li>
<li>Drill and fit rivet nuts <b>after</b> powder coat: M5 every ≤ 150 mm on the shell lines, M4 on the trays.</li>
<li>Caster plates are machined flat after welding. Use shims to level the frame to the drive-wheel ride height.</li>
<li>Guide rods are clamped top and bottom (bottom cross-member → mid cross-member), so the rods also stiffen the frame.</li>
</ul>
</div><div>
<h3>Shells (bolt-on, 1.2 mm CRCA, matte black)</h3>
<table>
<tr><th>Panel</th><th>Features</th></tr>
<tr><td>Front lower</td><td>2 sonars, speaker grille, front light-bar slots on the chamfers</td></tr>
<tr><td>Front slope (≈ 43°)</td><td>Camera window (looks 10–15° down), e-stop #1, mic hole</td></tr>
<tr><td>Left lower</td><td>2 sonars, Pi port window 64 × 30 mm, 4 × M3 rivet nuts for the cover</td></tr>
<tr><td>Right lower</td><td>2 sonars, display window 76 × 52 mm</td></tr>
<tr><td>Rear lower</td><td>2 sonars, charge-funnel opening 120 × 45 mm</td></tr>
<tr><td>Rear upper</td><td>Rear camera, e-stop #2, MAIN + LOGIC toggles, voltmeter</td></tr>
<tr><td>Side upper skirts</td><td>Black-yellow hazard strip</td></tr>
<tr><td>Deck</td><td>1.5 mm SS304, 20 mm lip, 8 × M5 countersunk screws into the top ring (lifts off for service)</td></tr>
<tr><td>Mid plate</td><td>1.5 mm Al 5052, Ø80 LiDAR hole + 3 mm mount plate, 2 pulley reliefs, cable grommets</td></tr>
<tr><td>Base plate</td><td>1.5 mm MS, 4 caster and 2 wheel openings, vents</td></tr>
</table>
<h3>3D-printed parts (PETG, Bambu P2S)</h3>
<p class="small">Pi port cover (4 × M3), display bezel, 2 camera housings with tilt wedge, 8 sonar bezels, 4 light-bar diffuser channels (white PETG 0.8 mm), charge funnel, 4 TPU corner bumpers on micro-switches, post cable caps, LiDAR cable clip. Use PETG rather than PLA+ for outside parts; PLA softens around 55 °C in a hot warehouse.</p>
</div></div>
<div class="ok"><b>Service access:</b> lift the deck (8 screws) to reach the LiDAR and mid plate. Remove one lower side panel to reach that side's bays. The base plate never needs to come off in normal service.</div>
"""))

# ---------------- 6. front & rear ----------------
pages.append(page(6, f"""
<h2><span class="n">5</span>Face-by-face features</h2>
{KEYS}
<h3>Front</h3>
<div class="fig narrow">{D.front_view()}</div>
{legend([("C", "Front webcam (Rapoo C260) on the sloped face, printed wedge housing, tilted 10–15° down"),
 ("E", "E-stop #1 (CR-257R), robot's right-front. Sits on the slope, below the deck line"),
 ("M", "Microphone pinhole"), ("S", "Speaker grille, 40 mm 3 W"), ("U", "2 front sonars at z = 110 mm. Light bars on both chamfers, TPU bumpers on the corners")])}
<h3>Rear</h3>
<div class="fig narrow">{D.rear_view()}</div>
{legend([("Q", "Charge funnel: 30° lead-in that corrects ±12 mm, 2 recessed female contacts 80 mm apart at z = 92"),
 ("C", "Rear webcam, centred: reads the ArUco marker on the dock"), ("V", "Battery voltmeter / ammeter (BOM row 25, chassis)"),
 ("T", "MAIN and LOGIC toggle switches"), ("E", "E-stop #2, robot's left-rear (diagonally opposite e-stop #1)")])}
"""))

# ---------------- 7. left & right ----------------
pages.append(page(7, f"""
<h2><span class="n">5</span>Face-by-face features (continued)</h2>
<h3>Left side — Raspberry Pi 5 service port</h3>
<div class="fig">{D.left_view()}</div>
<p>The Pi 5 lies flat on standoffs at z ≈ 120 mm with its USB/Ethernet edge against the left wall. A 64 × 30 mm window exposes <b>Ethernet and the 2 USB 2.0 ports</b> for service. The 2 USB 3.0 ports take short 90° adapters that turn back through a slot inside the cover footprint, feeding the internal hub. The <b>printed cover</b> (100 × 64 mm, PETG) closes the pocket with <b>4 × M3</b> screws into M3 rivet nuts in the panel. A TPU grommet notch lets a laptop cable stay plugged in with the cover on.</p>
<h3>Right side — 3.5 in status display</h3>
<div class="fig">{D.right_view()}</div>
<p>The 3.5 in HDMI touch LCD sits behind a printed bezel at the front-right, between the drive wheel and the front caster. It shows battery %, charge state, current task, IP address and faults. Touch is over USB and the micro-HDMI cable is about 0.6 m. The sonars sit at z = 140 mm, above the caster pockets.</p>
"""))

# ---------------- 8. docking & lights ----------------
pages.append(page(8, """
<h2><span class="n">6</span>Auto-docking and charging</h2>
<div class="grid2"><div>
<h3>Robot side (female)</h3>
<ul class="small" style="padding-left:4mm;margin:0 0 2mm">
<li>2 × 8 mm brass sockets, recessed 8 mm (finger-safe), 80 mm apart, z = 92 mm, inside a PETG funnel with a 30° lead-in.</li>
<li>Charge path: socket → Schottky/ideal diode → 15 A fuse → BMS charge port. A voltage divider tells the Mega when charging has started.</li>
<li>Rear webcam centred at z ≈ 259 mm, looking straight back.</li>
</ul>
<h3>Dock side (male)</h3>
<ul class="small" style="padding-left:4mm;margin:0 0 2mm">
<li>Floor plate with a V-guide, a 350 mm tower and 2 × Ø8 brass pins on 10 mm spring compliance.</li>
<li><b>ArUco DICT_4X4_50, id 0, 120 mm</b>, centred at z = 259 mm so it is level with the rear camera.</li>
<li>16.8 V 5 A CC/CV charger. The pins are <b>dead until a robot is sensed</b>: a small dock MCU checks for an ID resistor across the pins at low current, then closes a relay.</li>
</ul>
</div><div>
<h3>Docking sequence</h3>
<ol class="steps small">
<li>Navigate (map) to a pre-dock pose 1.0 m in front of the dock, then rotate so the rear faces the dock.</li>
<li>The rear camera finds the ArUco marker. Solve the marker pose with solvePnP.</li>
<li>Visual servo while reversing at 0.05 m/s. The steered wheels allow <b>lateral crab correction</b> without turning the body.</li>
<li>Stop when the charge-detect line goes high (or after a 30 mm over-travel limit). Drive power off.</li>
<li>The dock relay closes and the BMS charges. LED bars breathe blue, then show solid green when full.</li>
<li>To undock: drive forward 0.3 m, then resume the mission.</li>
</ol>
</div></div>
<div class="warn"><b>Battery decision.</b> The BOM uses 2 × Wild Scorpion 4S 4200 mAh LiPo with an IMAX B6 bench charger. That is fine for Phase 1 with manual charging off the robot. For <b>unattended dock charging</b>, either fit a 4S BMS with balancing to each LiPo, or (recommended) switch to 2 × 4S Li-ion packs with a built-in BMS. 4S3P 21700 packs give about 2 × 170 Wh against 2 × 62 Wh today, and runtime rises from about 1.8 h to about 5 h. The bays (180 × 80 × 75 mm) are sized to take either.</div>

<h2 style="margin-top:6mm"><span class="n">7</span>Light bars — front and back, both sides</h2>
<p>Four WS2812B bars cut from the BOM 30 LED/m strip, one at each corner: <b>front-left, front-right, rear-left, rear-right</b>. Each bar wraps from the chamfer 100 mm onto the side, so it is visible from the front/back and from the side, like the reference robot. Front bars have 7 LEDs and rear bars 6 (14 + 12 = 26 LEDs, about 1 A at full white). They are chained on 1 Mega pin (330 Ω series resistor, 1000 µF capacitor at the strip) and powered by their own 5 V 3 A buck, with brightness capped at 40% (≈ 1.5 A max).</p>
<table>
<tr><th>State</th><th>Front bars</th><th>Rear bars</th></tr>
<tr><td>Boot</td><td colspan="2">White sweep front → rear</td></tr>
<tr><td>Ready / idle</td><td colspan="2">Dim solid green</td></tr>
<tr><td>Driving forward</td><td>White (headlight)</td><td>Dim red</td></tr>
<tr><td>Turning / crabbing</td><td colspan="2">Amber blink 1.5 Hz on that side (front + rear bar)</td></tr>
<tr><td>Reversing / docking</td><td>Dim red</td><td>White + amber pulse</td></tr>
<tr><td>Obstacle slow-down</td><td colspan="2">Solid amber</td></tr>
<tr><td>E-stop / fault</td><td colspan="2">Red flash 4 Hz, all bars</td></tr>
<tr><td>Charging / full</td><td colspan="2">Blue breathing / solid green</td></tr>
<tr><td>Low battery (&lt; 20%)</td><td colspan="2">Slow red pulse; the display shows "return to dock"</td></tr>
</table>
"""))

# ---------------- 9. electrical ----------------
pages.append(page(9, f"""
<h2><span class="n">8</span>Electrical architecture and power budget</h2>
<div class="fig">{D.elec_view()}</div>
<p class="cap">The e-stop contactor switches only the 14.8 V motor bus (hub motors and steppers). The LOGIC branch is taken before the contactor, so the Pi, sensors and lights stay alive, report the fault and log the event.</p>
<div class="grid2"><div>
<table>
<tr><th>Load (average while driving)</th><th class="num">W</th></tr>
<tr><td>Raspberry Pi 5 (peak 12 W)</td><td class="num">7</td></tr>
<tr><td>RPLIDAR A2M12</td><td class="num">2.5</td></tr>
<tr><td>2 webcams, display, hub, audio</td><td class="num">4</td></tr>
<tr><td>Mega, 8 sonars, IMU, prox sensors</td><td class="num">1.5</td></tr>
<tr><td>LED bars (40% cap, average)</td><td class="num">3</td></tr>
<tr><td>2 steering steppers at 2.0 A (de-energised when parked)</td><td class="num">16</td></tr>
<tr><td>2 hub motors at 0.4 m/s, 76 kg, with acceleration</td><td class="num">20</td></tr>
<tr><td><b>Total</b></td><td class="num"><b>≈ 54</b></td></tr>
</table>
</div><div>
<table>
<tr><th>Battery option</th><th class="num">Wh</th><th class="num">Drive h</th><th class="num">Idle h</th></tr>
<tr><td>2 × 4S 4200 LiPo (BOM)</td><td class="num">124</td><td class="num">1.8</td><td class="num">≈ 5</td></tr>
<tr><td>2 × 4S3P 21700 Li-ion + BMS</td><td class="num">≈ 340</td><td class="num">≈ 5</td><td class="num">≈ 14</td></tr>
</table>
<p class="small">Both use 80% of the stored energy. The TB6600 has <b>no automatic idle-current reduction</b>: at 2.8 A the 2 steppers alone would draw about 28 W. Set the drivers to 2.0 A and drop ENA whenever the wheel angle is not changing; the belt friction holds the angle. The MPU-9250 magnetometer will be unreliable next to the hub magnets and steel frame, so use the gyro and accelerometer only.</p>
<div class="note">RS485: both M0601s share one bus (IDs 1 and 2), with 120 Ω termination at the far motor and the twisted pair kept away from the stepper cables.</div>
</div></div>
"""))

# ---------------- 10. mass, performance, BOM delta ----------------
pages.append(page(10, """
<h2><span class="n">9</span>Mass and performance</h2>
<div class="grid2"><div>
<table>
<tr><th>Group</th><th class="num">kg</th></tr>
<tr><td>MS skeleton (≈ 13 m tube)</td><td class="num">12.0</td></tr>
<tr><td>Caster pockets, carriage brackets</td><td class="num">2.5</td></tr>
<tr><td>Base plate 1.5 MS / mid plate 1.5 Al</td><td class="num">6.1</td></tr>
<tr><td>Deck 1.5 mm SS304</td><td class="num">6.0</td></tr>
<tr><td>Shell panels 1.2 mm CRCA</td><td class="num">5.2</td></tr>
<tr><td>2 drive modules (incl. M0601 ≈ 0.77 each)</td><td class="num">4.8</td></tr>
<tr><td>2 steering steppers (650 g each)</td><td class="num">1.3</td></tr>
<tr><td>4 casters</td><td class="num">1.8</td></tr>
<tr><td>Batteries (LiPo)</td><td class="num">0.9</td></tr>
<tr><td>Electronics, LiDAR, cameras, wiring</td><td class="num">3.0</td></tr>
<tr><td>Printed parts, fasteners, mat</td><td class="num">2.5</td></tr>
<tr><td><b>Robot</b> / <b>+ 30 kg payload</b></td><td class="num"><b>≈ 46 / 76</b></td></tr>
</table>
<p class="small">The Chassis tab estimates 29 kg because it assumes the smaller 600 × 450 mm frame. Al 5052 panels instead of CRCA would save about 3 kg.</p>
</div><div>
<table>
<tr><th>Check (76 kg, 14.8 V)</th><th class="num">Value</th></tr>
<tr><td>Drive force, rated / stall (2 wheels)</td><td class="num">37.6 / 78 N</td></tr>
<tr><td>Rolling resistance (Crr 0.015)</td><td class="num">11.3 N</td></tr>
<tr><td>Max acceleration at rated torque</td><td class="num">0.35 m/s²</td></tr>
<tr><td>Max ramp, continuous / short burst</td><td class="num">2.0° / 5°</td></tr>
<tr><td>Top speed</td><td class="num">≈ 0.5 m/s</td></tr>
<tr><td>Spring preload per drive wheel</td><td class="num">≈ 80 N (&lt; 10 kg limit)</td></tr>
<tr><td>Traction per wheel (μ 0.6)</td><td class="num">48 N ≥ stall 39 N ✓</td></tr>
<tr><td>Load per caster</td><td class="num">≈ 15 kg (rated 60+)</td></tr>
</table>
<div class="warn">Compared with the SEIT100 reference (100 kg, 1.5 m/s), this platform runs at about one third of the speed and payload. That suits a lab or indoor-logistics prototype. For <b>&gt; 30 kg or &gt; 0.6 m/s</b>, swap the M0601s for 6.5 in (165 mm) hub motors with BLDC drivers on a 10S pack. That really is a 15 cm drive wheel and fits the same H skeleton with taller caster pockets.</div>
</div></div>

<h2 style="margin-top:4mm"><span class="n">10</span>Changes to <i>AGV Budget Plan.xlsx</i></h2>
<table>
<tr><th style="width:24%">Line</th><th style="width:36%">Change</th><th>Note</th></tr>
<tr><td>Chassis #1 Frame tube</td><td>2 → <b>3</b> lengths 25×25×1.5, + 1 length 20×20×1.5</td><td>About 13.3 m needed at 800 × 570 mm</td></tr>
<tr><td>Chassis #3–5 Deck, panels, base</td><td>Resize blanks to 813 × 584. Panels to 1.2 mm CRCA, deck to 1.5 mm SS</td><td>Sheet area is about 1.7× the 600 × 450 estimate</td></tr>
<tr><td>Chassis #7 Motor mounts</td><td>Hinged → vertical slide: 4 × Ø12 rod, 4 × LM12UU, 4 springs</td><td>§3</td></tr>
<tr><td>Chassis #8 Casters</td><td>5 in → <b>100 mm</b> low-profile PU swivel ×4</td><td>§1</td></tr>
<tr><td>Chassis #21 Steering pivots</td><td>UCFL204 → 2 × 6004-2RS + 51104 + welded cartridge, per wheel</td><td>§3</td></tr>
<tr><td>Chassis #23 LED strip</td><td>Keep 30/m (about 0.9 m used)</td><td>§7</td></tr>
<tr><td>Chassis #24 Signal tower</td><td>Remove</td><td>Light bars replace it</td></tr>
<tr><td>New electronics</td><td>3.5 in HDMI touch LCD; 5.1 V 5 A buck; Pi 5 active cooler; 7-port powered USB 3 hub; USB audio + mic + PAM8403 + 40 mm speaker; 40 A DC contactor; 30 A + 15 A fuses; 4th 5 V 3 A buck</td><td>§1, §8</td></tr>
<tr><td>New, docking</td><td>16.8 V 5 A charger, 4S BMS ×2 (or Li-ion packs), 2 + 2 brass contacts, dock MCU + relay</td><td>§6</td></tr>
<tr><td>New, hardware</td><td>M5 and M3 rivet nuts, PETG 1 kg (white + black), opal diffuser, cable glands</td><td>§4</td></tr>
</table>
"""))

# ---------------- 11. Fusion plan & decisions ----------------
pages.append(page(11, """
<h2><span class="n">11</span>Fusion 360 build plan (via the Fusion MCP)</h2>
<p>The model is <b>parametric from one parameter table</b>, the same constants used for every drawing in this document (envelope, clearance, band heights, tube sizes, chamfers, caster and module positions). Changing L or W in Fusion then moves the skeleton, shells and bays together.</p>
<table>
<tr><th style="width:5%">#</th><th style="width:24%">Step</th><th>Content</th><th style="width:20%">Done when</th></tr>
<tr><td>0</td><td>User parameters</td><td>L, W, H, GC, Z_MID, Z_BAND, TUBE, CH_F, CH_R, CAS_X/Y, DRV_Y, STP_Y, SLOPE</td><td>Table set up in Fusion</td></tr>
<tr><td>1</td><td>Skeleton component</td><td>3 rings from chamfered sketches, posts, cross-members, caster pockets, carriage brackets. One body per member, MS material</td><td>Mass ≈ 14.5 kg, no gaps at the joints</td></tr>
<tr><td>2</td><td>Bought parts</td><td>STEP files where the vendor provides them (RPi 5, Slamtec A2, M0601, NEMA 23, Mega). Simple bodies for the others (TB6600, casters, LiPo, webcams, e-stop, sonar)</td><td>Each one placed in its bay</td></tr>
<tr><td>3</td><td>Drive modules</td><td>Fork, cartridge, pulleys, carriage, rods. Revolute joint (steering) + slider joint (suspension), mirrored L/R</td><td>Full 360° steer with no collision</td></tr>
<tr><td>4</td><td>Plates</td><td>Base, mid and deck as sheet metal, with openings and reliefs</td><td>Flat patterns export to DXF</td></tr>
<tr><td>5</td><td>Shells</td><td>Sheet-metal panels with flanges, all feature holes, rivet-nut pattern</td><td>DXF + bend table for the laser shop</td></tr>
<tr><td>6</td><td>Printed parts</td><td>Port cover, bezels, funnel, diffusers, bumpers, camera wedges</td><td>STL / 3MF for the P2S</td></tr>
<tr><td>7</td><td>Checks</td><td>Interference; LiDAR line-of-sight sketch at z = 213; CG and mass from materials; caster swivel clearance</td><td>Report with screenshots</td></tr>
<tr><td>8</td><td>Dock</td><td>Floor plate, tower, ArUco plate, spring pins, charger box</td><td>Matching heights checked against the robot</td></tr>
</table>
<p class="small">After you approve: (1) an interactive 3D HTML viewer built from the same parameters (exploded view, toggles for shell/skeleton/electronics, LiDAR band visualiser), then (2) the Fusion model, step by step through the MCP.</p>

<h2 style="margin-top:5mm"><span class="n">12</span>Decisions needed before modelling</h2>
<table>
<tr><th style="width:5%">#</th><th style="width:30%">Decision</th><th style="width:30%">Recommended</th><th>Alternative</th></tr>
<tr><td>1</td><td>Envelope</td><td>Keep 813 × 584 × 305 mm</td><td>Compact 700 × 500 (tight; batteries move under the drive bay)</td></tr>
<tr><td>2</td><td>Payload / drive</td><td>30 kg, M0601 (as in the BOM)</td><td>60–100 kg with 6.5 in hub motors on 10S</td></tr>
<tr><td>3</td><td>Casters</td><td>100 mm low-profile</td><td>6 in (needs a taller body or a lower LiDAR band)</td></tr>
<tr><td>4</td><td>Battery</td><td>2 × 4S Li-ion with BMS (dock-chargeable)</td><td>Keep LiPo + add BMS, or manual charging only in Phase 1</td></tr>
<tr><td>5</td><td>Shell material</td><td>1.2 mm CRCA, powder-coated black</td><td>1 mm SS304 as in the BOM (silver look, costs more)</td></tr>
<tr><td>6</td><td>LiDAR position</td><td>Plan centre, 360° band (≈ 340° usable)</td><td>Front-centre in a front-only slot (about 200° usable, simpler upper frame)</td></tr>
<tr><td>7</td><td>Display</td><td>3.5 in HDMI touch LCD</td><td>DSI 3.5 in (needs a long FFC; no USB port used)</td></tr>
</table>
<p class="small">Sources: DFRobot M0601 wiki (FIT1042) and the Waveshare DDSM115 page for wheel load and mass; Slamtec RPLIDAR A2M12 datasheet; Raspberry Pi 5 drawing; every RoboticsBD / StarTech / electronics.com.bd link in the spreadsheet (see §13); <i>AGV Budget Plan.xlsx</i> (Budget + Chassis tabs) for parts, prices and the 20–30 kg payload.</p>
"""))

# ---------------- 12. component dimension register ----------------
REG = [
 ("M0601 hub motor L/R", "Tyre Ø100.7 ±1.5, overall width 65.5 ±0.5. Stator boss Ø19 with Ø15.2 D-pilot (6.5 flat), 3 × M2.5 × 5 deep. Cable 255 mm out of the boss. 765 g, 10 kg wheel load", "DFRobot diagram; mass/load: Waveshare DDSM115", "ok"),
 ("NEMA 23 23HS5628", "57 × 57 frame, body 51 long, shaft Ø8 × 20.6, 650 g. Bolt pattern not listed: standard NEMA 23 is 47.14 sq, Ø38.1 pilot", "RoboticsBD #817", "chk"),
 ("NEMA 23 L-bracket", "50 × 62 × 64, Ø5 holes. Page gives both 90 g and 117 g", "RoboticsBD #1533", "chk"),
 ("TB6600 driver", "Not listed (packed 100 × 80 × 40). Drawn as the common 96 × 71 × 37 case", "RoboticsBD #2419", "meas"),
 ("RPLIDAR A2M12", "Ø76 × 41; fixed base 18.6; rotor Ø72.5; scan plane at base + 31; 6 mm window; 4 × M3 ≤ 4 mm deep on R29.5; 190 g; 2.25–3 W", "Slamtec datasheet fig. 5-1", "ok"),
 ("Raspberry Pi 5", "85 × 56 board; Ø2.7 holes on a 58 × 49 grid, 3.5 from the edge; USB + Ethernet on the short edge, overhanging 3 mm; 105 g", "Raspberry Pi drawing", "ok"),
 ("Pi 5 Active Cooler", "63.5 × 42.5 footprint, 13.7 tall", "Raspberry Pi product brief", "ok"),
 ("Arduino Mega 2560", "Not on the store page. Standard outline 101.6 × 53.3", "Arduino board standard", "chk"),
 ("Rapoo C260 webcam", "Body size not listed. FOV given as both 80° and 95°. 97.5 g", "StarTech", "meas"),
 ("Wild Scorpion 4S 4200 LiPo", "Page template is unfilled (no size, weight or plug)", "electronics.com.bd", "meas"),
 ("RS485 USB adapter", "60 × 18 × 12, 20 g", "RoboticsBD #566", "ok"),
 ("5 V 3 A buck", "18.3 × 10.2 × 6.7. Page gives both 2 A and 3 A", "RoboticsBD #1545", "chk"),
 ("Veroboard", "145 × 65 × 1.1, 2.54 pitch (page also says 145 × 60)", "RoboticsBD #840", "chk"),
 ("E-stop CR-257R", "Head Ø39, mounting neck Ø25 (panel hole about Ø25), 26 g", "RoboticsBD #1889", "chk"),
 ("Toggle switch 6 A", "13 × 13 × 29 (page also 12 × 12 × 10)", "RoboticsBD #1430", "chk"),
 ("Micro limit switch", "20 × 15 × 6", "RoboticsBD #1369", "ok"),
 ("HC-SR04", "PCB 45 × 20, Ø16 transducers, 15° beam", "RoboticsBD #22", "ok"),
 ("HC-SR04 housing", "70 × 30 × 20, no hole data", "RoboticsBD #2696", "ok"),
 ("MPU-9250", "25 × 15 × 3.5 (page also 22 × 17), 5 g", "RoboticsBD #680", "chk"),
 ("LJ12A3-4 prox", "M12 × ~60, 4 mm sensing distance", "RoboticsBD #3208", "ok"),
 ("Voltmeter / ammeter", "Module size and cut-out not listed", "RoboticsBD #2677", "meas"),
 ("WS2812B 30/m strip", "IP67, 5 m, 150 LEDs, ≈ 1.1 A/m at full white. Width not listed", "RoboticsBD #3860", "chk"),
 ("LiPo strap", "20 × 2 cm", "RoboticsBD #3070", "ok"),
 ("Casters 100 mm", "No link (Chassis tab estimate)", "—", "meas"),
]
ST = {"ok": '<span class="tag t-keep">OK</span>', "chk": '<span class="tag t-chg">CHECK</span>', "meas": '<span class="tag t-drop">MEASURE</span>'}
rows = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td><td>{ST[d]}</td></tr>" for a, b, c, d in REG)
pages.append(page(12, f"""
<h2><span class="n">13</span>Component dimension register (from the spreadsheet links)</h2>
<p style="font-size:8.8pt">Each link in <i>AGV Budget Plan.xlsx</i> was opened, along with the manufacturer drawing where the store page pointed to one. The store pages warn of up to 5% measuring deviation, and several contradict themselves. Status: <span class="tag t-keep">OK</span> from a drawing or a clear listing, <span class="tag t-chg">CHECK</span> the page contradicts itself or a standard value is used, <span class="tag t-drop">MEASURE</span> not listed, so measure the part before releasing its bracket or cut-out.</p>
<table class="dense">
<tr><th style="width:18%">Part</th><th style="width:52%">Dimensions used in the model (mm)</th><th style="width:21%">Source</th><th>Status</th></tr>
{rows}
</table>
<div class="note" style="font-size:8pt;margin-top:1mm"><b>What these numbers changed in Rev B:</b> (1) The M0601 fixes on <b>one side only</b> (Ø19 boss, 3 × M2.5), so the fork became a single-sided hanger. Use 10.9-grade screws with threadlocker and keep the spring preload ≤ 80 N. (2) The real sweep (Ø128) let the drive modules move in to y = ±185, clear of the bottom ring. (3) The stepper is 51 mm long, not 76, so it now ends 104 mm above the floor. (4) The LiDAR scan plane is base + 31 mm, so the LiDAR is recessed to put the scan plane at 213 mm, the centre of the band. (5) RoboticsBD has no 60/m LED strip, so the bars use the BOM 30/m strip. (6) The e-stop needs a Ø25 panel hole. (7) The steppers weigh 650 g each, so the robot is now about 46 kg.</div>
"""))

html = f'<!doctype html><html><head><meta charset="utf-8"><title>AMR Design Proposal Rev B</title><style>{CSS}</style></head><body>{"".join(pages)}</body></html>'
OUT_HTML.write_text(html)
subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                f"--print-to-pdf={OUT_PDF}", OUT_HTML.as_uri()], check=True,
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(OUT_PDF)
