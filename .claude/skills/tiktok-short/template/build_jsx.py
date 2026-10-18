"""Write vm/short.jsx: the whole picture of the short as one EffectCraft comp ("Short", 1080x1920, 30 fps).

Reads timeline.json (line/caption timing from the voice) and vm/map.json (Natural Earth geometry in map pixels).
The JSX builds, bottom to top: sea background, the animated map (all map layers are children of the "MapCam"
null, so a camera move is one position/scale track), rain, the lake counter, photo/video scenes with camera moves,
cut flashes, a caption shade, photo credits, the closing comment bubble, and the Khmer kinetic captions.
Every animation is sampled into keyframes by the JS helpers (eases computed here, no expressions needed).
Text layers are listed in vm/text_layers.json by the script's output; vm_build.sh bolds them afterwards.

Run: python3 build_jsx.py   (then vm_build.sh on the Mac pushes, builds and renders on the VM)
"""
from __future__ import annotations

import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
TL = json.loads((HERE / "timeline.json").read_text())
MAP = json.loads((HERE / "vm/map.json").read_text())
VM_DIR = "/home/ubuntu/money-printer/short-01-river"
ASSETS = f"{VM_DIR}/assets"

LEN = TL["length"]
SC = {s["scene"]: s for s in TL["scenes"]}
MK = TL["markers"]                       # caption row text -> time its first sound starts (minus a small lead)


def mk(text: str) -> float:
    return MK[text]


# ---------------------------------------------------------------- camera views (map pixels -> screen)
S0 = (540, 720)                          # where a view's centre lands on screen (map sits above the captions)


def view(cx: float, cy: float, z: float, sx: float = S0[0], sy: float = S0[1]) -> dict:
    return {"p": [round(sx - z * cx, 1), round(sy - z * cy, 1)], "z": round(z * 100, 2)}


PP = MAP["places"]["phnom_penh"]
LAKE_C = MAP["lake_center"]
river = MAP["tonle_sap_river"]
mid = len(river) // 2
V = {
    "wide": view(97, -10, 0.55, sy=760),
    "hook": view((river[mid][0] + LAKE_C[0]) / 2 + 10, (river[mid][1] + LAKE_C[1]) / 2, 1.55),
    "lake": view(35, 70, 1.12),
    "grow": view(-10, 20, 0.98),
    "pp": view(PP[0], PP[1], 3.2),
    "ask": view(97, -5, 0.6, sy=700),
}

# arrow on the Tonle Sap river: middle of the river, pointing downstream (towards Phnom Penh)
a, b = river[mid - 2], river[mid + 2]
ARROW_POS = river[mid]
ARROW_DOWN = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))

# ---------------------------------------------------------------- key times
T = {
    "hook_flip": mk("ហូរបញ្ច្រាសទិស។") + 0.35,
    "rain_in": SC["rain"]["start"] + 0.1,
    "mekong_up": mk("ឡើងទឹកខ្លាំង"),
    "push": mk("រហូតរុញទឹក"),
    "back_to_lake": mk("ហូរត្រឡប់"),
    "rain_out": SC["grow"]["start"],
    "grow": mk("រីកធំជាងមុន"),
    "count": mk("បួនទៅប្រាំដង។"),
    "fish": SC["fish"]["start"],
    "fisher": mk("ចូលមក"),
    "people": mk("ហើយចិញ្ចឹមជីវិត"),
    "turn": SC["turn"]["start"],
    "kadeuk": mk("ខែកត្តិក"),
    "flip_back": mk("ត្រឡប់ហូរចុះ") + 0.2,
    "fest": SC["fest"]["start"],
    "rowers": mk("ជាពេលដែលខ្មែរយើង"),
    "boat": mk("ពិធីបុណ្យអុំទូក"),
    "floats": mk("បណ្តែតប្រទីប"),
    "moon": mk("សំពះព្រះខែ"),
    "ambok": mk("និង"),
    "thanks": SC["thanks"]["start"],
    "ask": SC["ask"]["start"],
    "write": mk("សរសេរប្រាប់ខ្ញុំផង។"),
}
T["ambok"] = mk("អកអំបុក។") - 0.25
T["people"] = max(T["people"], T["fisher"] + 1.0)

# footage: (key, file, in, out, kind, fit, motion, credit)
# motion: (scale0 multiplier, scale1 multiplier, x0 frac, x1 frac) frac = which part of the picture is centred
FOOT = [
    ("fish", "pixabay/fish.mp4", T["fish"], T["fisher"], "video", 0.0, (1.0, 1.08, 0.5, 0.5), None),
    ("fisher", "commons/fisher_net.jpg", T["fisher"], T["turn"], "image", 0.0, (1.02, 1.12, 0.40, 0.46), "fisher_net"),
    ("rowers", "commons/boat_rowers.jpg", T["rowers"], T["boat"], "image", 0.0, (1.05, 1.12, 0.62, 0.42), "boat_rowers"),
    ("boat", "commons/boat_pink.jpg", T["boat"], T["floats"], "image", 0.0, (1.0, 1.06, 0.30, 0.66), "boat_pink"),
    ("floats", "commons/floats_3.jpg", T["floats"], T["moon"], "image", 0.0, (1.04, 1.14, 0.47, 0.52), "floats_3"),
    ("moon", "pixabay/moon.mp4", T["moon"], T["ambok"], "video", 2.0, (1.0, 1.10, 0.5, 0.5), None),
    ("ambok", "commons/ak_ambok.jpg", T["ambok"], T["thanks"], "image", 0.0, (1.04, 1.14, 0.5, 0.5), "ak_ambok"),
    ("river", "pixabay/river.mp4", T["thanks"], T["ask"], "video", 6.0, (1.0, 1.08, 0.5, 0.5), None),
]


def credit(name: str | None) -> str | None:
    if not name:
        return None
    j = json.loads((HERE / f"assets/commons/{name}.json").read_text())
    author = j["author"].replace("from Penang, Malaysia", "").strip()
    return f"រូបថត៖ {author} / Wikimedia Commons ({j['license']})"


FOOT = [f[:7] + (credit(f[7]),) for f in FOOT]

DATA = {
    "len": LEN, "fps": TL["fps"], "assets": ASSETS, "map": MAP, "V": V, "T": T,
    "arrow": {"pos": ARROW_POS, "down": ARROW_DOWN},
    "foot": FOOT, "blocks": TL["blocks"], "scenes": SC,
    "wet_scale": 1.0,
}

JS = r"""
// ===== generated by build_jsx.py: do not edit by hand =====
var D = __DATA__;
var LEN = D.len, T = D.T, V = D.V, M = D.map;
var comp = app.project.items.addComp("Short", 1080, 1920, 1, LEN, D.fps);
var TEXT_LAYERS = [];

// ---------- easing + keyframe baking (every 1/30 s inside a move, two keys for a hold)
function E(n, u) {
  if (n === "lin") return u;
  if (n === "o") return 1 - Math.pow(1 - u, 3);
  if (n === "i") return u * u * u;
  if (n === "back") { var c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(u - 1, 3) + c1 * Math.pow(u - 1, 2); }
  if (n === "o5") return 1 - Math.pow(1 - u, 5);
  return u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2;   // "io"
}
function lerp(a, b, u) {
  if (typeof a === "number") return a + (b - a) * u;
  var r = []; for (var i = 0; i < a.length; i++) r.push(a[i] + (b[i] - a[i]) * u); return r;
}
function same(a, b) {
  if (typeof a === "number") return a === b;
  for (var i = 0; i < a.length; i++) if (a[i] !== b[i]) return false; return true;
}
function track(prop, keys) {            // keys: [[t, value, ease-into-this-key], ...]
  prop.setValueAtTime(keys[0][0], keys[0][1]);
  for (var k = 1; k < keys.length; k++) {
    var A = keys[k - 1], B = keys[k];
    if (same(A[1], B[1])) { prop.setValueAtTime(B[0], B[1]); continue; }
    var n = Math.max(1, Math.round((B[0] - A[0]) * 30));
    for (var i = 1; i <= n; i++) {
      var u = i / n; prop.setValueAtTime(A[0] + (B[0] - A[0]) * u, lerp(A[1], B[1], E(B[2] || "io", u)));
    }
  }
}
function mkShape(pts, closed) { var s = new Shape(); s.vertices = pts; s.closed = closed; return s; }
function morph(prop, t0, t1, A, B, ease) {
  var n = Math.max(1, Math.round((t1 - t0) * 20));
  for (var i = 0; i <= n; i++) { var u = E(ease, i / n), pts = [];
    for (var j = 0; j < A.length; j++) pts.push([A[j][0] + (B[j][0] - A[j][0]) * u, A[j][1] + (B[j][1] - A[j][1]) * u]);
    prop.setValueAtTime(t0 + (t1 - t0) * i / n, mkShape(pts, true)); }
}
function P(layer, path) {               // property by "Transform/Opacity" style path
  var parts = path.split("/"), p = layer;
  for (var i = 0; i < parts.length; i++) p = p.property(parts[i]);
  return p;
}
function setp(group, name, v) { try { group.property(name).setValue(v); } catch (e) {} }
function fx(layer, match) { try { return layer.property("Effects").addProperty(match); } catch (e) { return null; } }
function hex(h) { return [parseInt(h.substr(1, 2), 16) / 255, parseInt(h.substr(3, 2), 16) / 255, parseInt(h.substr(5, 2), 16) / 255]; }
function show(layer, t0, t1) { layer.inPoint = Math.max(0, t0); layer.outPoint = Math.min(LEN, t1); }
function glow(layer, radius, intensity) {
  var g = fx(layer, "ADBE Glo2"); if (!g) return;
  setp(g, "Glow Threshold", 40); setp(g, "Glow Radius", radius); setp(g, "Glow Intensity", intensity);
}

// ---------- shapes
function shapeLayer(name, parent) {
  var L = comp.layers.addShape(); L.name = name;
  if (parent) L.parent = parent;
  P(L, "Transform/Anchor Point").setValue([0, 0]); P(L, "Transform/Position").setValue([0, 0]);
  return L;
}
function group(L) { return L.property("Contents").addProperty("ADBE Vector Group"); }
function path(g, pts, closed) { var p = g.property("Contents").addProperty("ADBE Vector Shape - Group");
  p.property("Path").setValue(mkShape(pts, closed)); return p; }
function stroke(g, color, w) { var s = g.property("Contents").addProperty("ADBE Vector Graphic - Stroke");
  s.property("Color").setValue(hex(color)); s.property("Stroke Width").setValue(w);
  try { s.property("Line Cap").setValue(2); s.property("Line Join").setValue(2); } catch (e) {} return s; }
function fill(g, color, op) { var f = g.property("Contents").addProperty("ADBE Vector Graphic - Fill");
  f.property("Color").setValue(hex(color)); if (op !== undefined) f.property("Opacity").setValue(op); return f; }
function trim(L) { return L.property("Contents").addProperty("ADBE Vector Filter - Trim"); }
function dashes(st, dash, gap) { var d = st.property("Dashes");
  d.addProperty("ADBE Vector Stroke Dash 1").setValue(dash); d.addProperty("ADBE Vector Stroke Gap 1").setValue(gap);
  return d.addProperty("ADBE Vector Stroke Offset"); }
function circle(cx, cy, r, n) { var pts = []; for (var i = 0; i < n; i++) { var a = 2 * Math.PI * i / n;
  pts.push([cx + r * Math.cos(a), cy + r * Math.sin(a)]); } return pts; }

// ---------- text
function text(str, size, color, just, parent) {
  var L = comp.layers.addText(str);
  var td = L.property("Source Text").value;
  td.font = "Google Sans"; td.fontSize = size; td.fillColor = hex(color); td.applyFill = true; td.applyStroke = false;
  td.justification = just === "left" ? ParagraphJustification.LEFT_JUSTIFY : ParagraphJustification.CENTER_JUSTIFY;
  L.property("Source Text").setValue(td);
  if (parent) L.parent = parent;
  return L;
}
function shadow(L, dist, soft, op) { var s = fx(L, "ADBE Drop Shadow"); if (!s) return;
  setp(s, "Shadow Color", [0, 0, 0]); setp(s, "Opacity", op === undefined ? 200 : op); setp(s, "Direction", 180);
  setp(s, "Distance", dist); setp(s, "Softness", soft); }
function bold(L, w) { TEXT_LAYERS.push({ id: L.id, w: w }); }

// ==================================================================== background
var bg = comp.layers.addSolid(hex("#050b16"), "Sea", 1080, 1920, 1, LEN);
var ramp = fx(bg, "ADBE Ramp");
if (ramp) { setp(ramp, "Start of Ramp", [540, 640]); setp(ramp, "Start Color", hex("#0f2a4d"));
  setp(ramp, "End of Ramp", [540, 1950]); setp(ramp, "End Color", hex("#040a14")); setp(ramp, "Ramp Shape", 2); }

var tex = comp.layers.addSolid([0.5, 0.5, 0.5], "Sea texture", 1080, 1920, 1, LEN);
var fn = fx(tex, "ADBE Fractal Noise");
if (fn) { setp(fn, "Contrast", 160); setp(fn, "Brightness", -10);
  try { track(fn.property("Evolution"), [[0, 0, "lin"], [LEN, 300, "lin"]]); } catch (e) {} }
try { tex.blendingMode = BlendingMode.OVERLAY; } catch (e) {}
P(tex, "Transform/Opacity").setValue(14);

// ==================================================================== map (children of MapCam)
var cam = comp.layers.addNull(LEN); cam.name = "MapCam";
P(cam, "Transform/Anchor Point").setValue([0, 0]); P(cam, "Transform/Position").setValue([0, 0]);

var nb = shapeLayer("Neighbours", cam);
for (var i = 0; i < M.neighbors.length; i++) { var g = group(nb); path(g, M.neighbors[i].ring, true);
  stroke(g, "#2a4468", 2); fill(g, "#13223b"); }

var kh = shapeLayer("Cambodia", cam);
var gk = group(kh); path(gk, M.cambodia, true);
var khFill = fill(gk, "#1d3a5f", 0); var khStroke = stroke(gk, "#7cc8ff", 3.5);
var khTrim = trim(kh);
track(khTrim.property("End"), [[0, 0], [1.1, 100, "o"]]);
track(khFill.property("Opacity"), [[0.5, 0], [1.3, 100, "o"]]);
glow(kh, 18, 0.8);

var prov = shapeLayer("Provinces", cam);
for (var i = 0; i < M.provinces.length; i++) { var g = group(prov); path(g, M.provinces[i].ring, true);
  stroke(g, "#3a6390", 1.2); }
track(P(prov, "Transform/Opacity"), [[0.8, 0], [1.6, 55, "o"]]);

// province ripple for the closing question
var HL = [];
var lc = M.lake_center;
var order = [];
for (var i = 0; i < M.provinces.length; i++) { var c = M.provinces[i].c;
  order.push({ i: i, d: Math.sqrt(Math.pow(c[0] - lc[0], 2) + Math.pow(c[1] - lc[1], 2)) }); }
order.sort(function (a, b) { return a.d - b.d; });
for (var k = 0; k < order.length; k++) {
  var pv = M.provinces[order[k].i];
  var L = shapeLayer("Province " + pv.name, cam); var g = group(L); path(g, pv.ring, true); fill(g, "#ffd54a");
  var t0 = T.ask + 0.5 + 0.075 * k;
  track(P(L, "Transform/Opacity"), [[0, 0], [t0, 0], [t0 + 0.16, 60, "o"], [t0 + 0.75, 0, "io"]]);
  show(L, T.ask, LEN);
}

var minor = shapeLayer("Rivers", cam);
for (var i = 0; i < M.rivers_minor.length; i++) { var g = group(minor); path(g, M.rivers_minor[i], false);
  stroke(g, "#2f78b0", 2.2); }
track(P(minor, "Transform/Opacity"), [[0.6, 0], [1.4, 80, "o"]]);

// lake (morphs dry -> flood -> dry)
var lake = shapeLayer("Lake", cam);
var gl = group(lake); var lakePath = path(gl, M.lake_dry, true).property("Path");
var lakeFill = fill(gl, "#2b8ef0"); stroke(gl, "#a8e0ff", 2.5);
morph(lakePath, T.grow, T.grow + 1.7, M.lake_dry, M.lake_wet, "io");
morph(lakePath, T.flip_back + 0.3, T.flip_back + 2.6, M.lake_wet, M.lake_dry, "io");
track(P(lake, "Transform/Opacity"), [[0.9, 0], [1.3, 100, "o"]]);
track(lakeFill.property("Color"), [[0, hex("#2b8ef0")], [T.back_to_lake, hex("#2b8ef0")],
  [T.back_to_lake + 0.4, hex("#55b4ff"), "o"], [T.flip_back + 2.6, hex("#55b4ff")], [T.flip_back + 3.0, hex("#2b8ef0")]]);
glow(lake, 30, 1.0);

// rivers: Bassac, Mekong (+ flow dashes), Tonle Sap (+ flow dashes)
var bas = shapeLayer("Bassac", cam); var gb = group(bas); path(gb, M.bassac, false); var basSt = stroke(gb, "#46c6f5", 4);
track(trim(bas).property("End"), [[0.4, 0], [1.5, 100, "o"]]);

var mek = shapeLayer("Mekong", cam); var gm = group(mek); path(gm, M.mekong, false);
var mekSt = stroke(gm, "#4fd8ff", 7);
track(trim(mek).property("End"), [[0.2, 0], [1.6, 100, "o"]]);
track(mekSt.property("Stroke Width"), [[0, 7], [T.mekong_up, 7], [T.mekong_up + 1.2, 17, "io"],
  [T.flip_back, 17], [T.flip_back + 2.0, 7, "io"]]);
glow(mek, 26, 1.1);

var mekF = shapeLayer("Mekong flow", cam); var gmf = group(mekF); path(gmf, M.mekong, false);
var mfSt = stroke(gmf, "#e8fbff", 3); var mOff = dashes(mfSt, 10, 34);
// offset falling = dashes moving north -> south (downstream); faster while the Mekong is in flood
mOff.setValueAtTime(0, 0);
mOff.setValueAtTime(T.mekong_up, -80 * T.mekong_up);
mOff.setValueAtTime(T.flip_back, -80 * T.mekong_up - 170 * (T.flip_back - T.mekong_up));
mOff.setValueAtTime(LEN, -80 * T.mekong_up - 170 * (T.flip_back - T.mekong_up) - 80 * (LEN - T.flip_back));
track(P(mekF, "Transform/Opacity"), [[1.4, 0], [1.9, 85, "o"]]);

var ts = shapeLayer("Tonle Sap river", cam); var gt = group(ts); path(gt, M.tonle_sap_river, false);
var tsSt = stroke(gt, "#ffcf4d", 6);
track(trim(ts).property("End"), [[0.9, 0], [1.7, 100, "o"]]);
track(tsSt.property("Stroke Width"), [[0, 6], [T.push, 6], [T.push + 0.6, 9, "o"], [T.flip_back, 9], [T.flip_back + 1.0, 6]]);
glow(ts, 22, 1.2);

var tsF = shapeLayer("Tonle Sap flow", cam); var gtf = group(tsF); path(gtf, M.tonle_sap_river, false);
var tfSt = stroke(gtf, "#ffffff", 3.5); var tOff = dashes(tfSt, 8, 20);
// path runs lake -> Phnom Penh: offset falling = towards Phnom Penh (normal), rising = back up to the lake
var o = 0; tOff.setValueAtTime(1.6, o);
o -= 45 * (T.hook_flip - 1.6); tOff.setValueAtTime(T.hook_flip, o);
o += 70 * (T.push - T.hook_flip); tOff.setValueAtTime(T.push, o);
o += 140 * (T.flip_back - T.push); tOff.setValueAtTime(T.flip_back, o);
o -= 70 * (LEN - T.flip_back); tOff.setValueAtTime(LEN, o);
track(P(tsF, "Transform/Opacity"), [[1.6, 0], [1.9, 100, "o"]]);

// Phnom Penh
var pp = shapeLayer("Phnom Penh", cam); var gp = group(pp);
path(gp, circle(M.places.phnom_penh[0], M.places.phnom_penh[1], 6, 24), true); fill(gp, "#ffffff"); stroke(gp, "#0b1a2e", 2);
track(P(pp, "Transform/Opacity"), [[1.6, 0], [2.0, 100, "o"]]);

// map labels (the wide views and the lake views use different sizes: labels scale with the camera)
function label(str, xy, size, color, t0, t1) {
  var L = text(str, size, color, "center", cam);
  P(L, "Transform/Position").setValue(xy);
  track(P(L, "Transform/Opacity"), [[t0, 0], [t0 + 0.4, 100, "o"], [t1 - 0.3, 100], [t1, 0]]);
  shadow(L, 2, 10, 180); bold(L, 200); show(L, t0, t1); return L;
}
var W1 = [0.0, 2.0], W2 = [T.ask + 0.2, LEN];
var wl = [["កម្ពុជា", M.places.label_cambodia, 64, "#ffffff"], ["ថៃ", M.places.label_thailand, 56, "#8aa5c8"],
  ["ឡាវ", M.places.label_laos, 56, "#8aa5c8"], ["វៀតណាម", M.places.label_vietnam, 56, "#8aa5c8"]];
for (var i = 0; i < wl.length; i++) { label(wl[i][0], wl[i][1], wl[i][2], wl[i][3], W1[0] + 0.3, W1[1]);
  label(wl[i][0], wl[i][1], wl[i][2], wl[i][3], W2[0], W2[1]); }
var L1 = [2.3, T.fish + 0.1], L2 = [T.turn - 0.1, T.rowers];
var ll = [["បឹងទន្លេសាប", M.places.label_lake, 30, "#d8f0ff"], ["ទន្លេមេគង្គ", M.places.label_mekong, 30, "#bdf1ff"],
  ["ទន្លេសាប", M.places.label_tonle_sap, 28, "#ffe08a"], ["ភ្នំពេញ", [M.places.phnom_penh[0] + 44, M.places.phnom_penh[1] + 6], 24, "#ffffff"]];
for (var i = 0; i < ll.length; i++) { label(ll[i][0], ll[i][1], ll[i][2], ll[i][3], L1[0], L1[1]);
  label(ll[i][0], ll[i][1], ll[i][2], ll[i][3], L2[0], L2[1]); }

// arrow on the Tonle Sap river: appears pointing downstream, flips upstream (the hook), flips back in Kadeuk
var ar = shapeLayer("Arrow", cam); var ga = group(ar);
path(ga, [[-26, -8], [2, -8], [2, -20], [28, 0], [2, 20], [2, 8], [-26, 8]], true);
fill(ga, "#ffffff"); stroke(ga, "#ffb300", 3);
P(ar, "Transform/Position").setValue(D.arrow.pos);
var dn = D.arrow.down, up = dn + 180;
track(P(ar, "Transform/Rotation"), [[0, dn], [T.hook_flip, dn], [T.hook_flip + 0.45, up, "back"],
  [T.flip_back, up], [T.flip_back + 0.45, up + 180, "back"]]);
track(P(ar, "Transform/Scale"), [[1.8, [0, 0]], [2.15, [100, 100], "back"], [T.hook_flip, [100, 100]],
  [T.hook_flip + 0.2, [135, 135], "o"], [T.hook_flip + 0.5, [100, 100], "io"], [T.push, [100, 100]],
  [T.push + 0.25, [125, 125], "o"], [T.push + 0.6, [100, 100], "io"]]);
glow(ar, 20, 1.4);

// ---------- camera moves (MapCam: world = position + scale * map px)
function camKeys(list) { var pk = [], sk = [];
  for (var i = 0; i < list.length; i++) { var v = V[list[i][1]];
    pk.push([list[i][0], v.p, list[i][2]]); sk.push([list[i][0], [v.z, v.z], list[i][2]]); }
  track(P(cam, "Transform/Position"), pk); track(P(cam, "Transform/Scale"), sk); }
camKeys([[0, "wide"], [0.5, "wide"], [2.7, "hook", "io"], [T.rain_in, "hook"], [T.rain_in + 1.2, "lake", "io"],
  [T.grow - 0.6, "lake"], [T.grow + 0.8, "grow", "io"], [T.flip_back + 0.4, "grow"], [T.flip_back + 2.6, "lake", "io"],
  [T.fest + 0.05, "lake"], [T.rowers + 0.05, "pp", "i"], [T.ask - 0.05, "pp"], [T.ask, "wide"], [T.ask + 1.2, "ask", "o"]]);

// ==================================================================== weather
var cloud = comp.layers.addSolid([0, 0.02, 0.05], "Rain shade", 1080, 1920, 1, LEN);
track(P(cloud, "Transform/Opacity"), [[T.rain_in, 0], [T.rain_in + 0.6, 38, "o"], [T.rain_out - 0.4, 38], [T.rain_out + 0.3, 0]]);
show(cloud, T.rain_in, T.rain_out + 0.4);
var rain = comp.layers.addSolid([0, 0, 0], "Rain", 1080, 1920, 1, LEN);
var rf = fx(rain, "CC Rainfall");
if (rf) { setp(rf, "Drops", 4000); setp(rf, "Size", 2); setp(rf, "Speed", 6000); setp(rf, "Wind", 300); setp(rf, "Opacity", 40); }
try { rain.blendingMode = BlendingMode.SCREEN; } catch (e) {}
track(P(rain, "Transform/Opacity"), [[T.rain_in, 0], [T.rain_in + 0.5, 42, "o"], [T.rain_out - 0.4, 42], [T.rain_out + 0.3, 0]]);
show(rain, T.rain_in, T.rain_out + 0.4);

// map vignette
var vig = comp.layers.addSolid([1, 1, 1], "Vignette", 1080, 1920, 1, LEN); vig.adjustmentLayer = true;
var cv = fx(vig, "CC Vignette"); if (cv) { setp(cv, "Amount", 55); }

// ==================================================================== lake counter (x1 -> x5)
var cnt = text("×1", 150, "#ffd54a", "center"); P(cnt, "Transform/Position").setValue([800, 420]);
var cTimes = [0, 0.26, 0.5, 0.72, 0.92];
for (var i = 0; i < 5; i++) { var td = cnt.property("Source Text").value; td.text = "×" + (i + 1);
  cnt.property("Source Text").setValueAtTime(T.count + cTimes[i], td); }
var ck = [[T.grow, [0, 0]], [T.grow + 0.35, [100, 100], "back"]];
for (var i = 1; i < 5; i++) { ck.push([T.count + cTimes[i], [100, 100]]); ck.push([T.count + cTimes[i] + 0.12, [118, 118], "o"]);
  ck.push([T.count + cTimes[i] + 0.24, [100, 100], "io"]); }
track(P(cnt, "Transform/Scale"), ck);
track(P(cnt, "Transform/Opacity"), [[T.grow, 0], [T.grow + 0.2, 100], [T.fish - 0.15, 100], [T.fish, 0]]);
shadow(cnt, 6, 18); glow(cnt, 16, 0.8); bold(cnt, 300); show(cnt, T.grow, T.fish);
var cntL = text("ទំហំបឹង", 46, "#ffffff", "center"); P(cntL, "Transform/Position").setValue([800, 290]);
track(P(cntL, "Transform/Opacity"), [[T.grow + 0.1, 0], [T.grow + 0.4, 100, "o"], [T.fish - 0.15, 100], [T.fish, 0]]);
shadow(cntL, 4, 12); bold(cntL, 300); show(cntL, T.grow, T.fish);

// ==================================================================== photos and video
var FLASH = [];
function cover(w, h) { return Math.max(1080 / w, 1920 / h) * 100; }
for (var i = 0; i < D.foot.length; i++) {
  var f = D.foot[i]; var key = f[0], file = f[1], t0 = f[2], t1 = f[3], kind = f[4], skip = f[5], mo = f[6], cr = f[7];
  var item = app.project.importFile(new ImportOptions(new File(D.assets + "/" + file)));
  var L = comp.layers.add(item); L.name = key;
  if (kind === "video") { L.startTime = t0 - skip; try { L.audioEnabled = false; } catch (e) {} }
  show(L, t0, t1 + 0.04);
  var s = cover(item.width, item.height), w = item.width * s / 100;
  var x0 = 540 + (0.5 - mo[2]) * w * mo[0], x1 = 540 + (0.5 - mo[3]) * w * mo[1];
  var lim = function (x, m) { var half = w * m / 2; return Math.min(half, Math.max(1080 - half, x)); };
  track(P(L, "Transform/Position"), [[t0, [lim(x0, mo[0]), 960]], [t1, [lim(x1, mo[1]), 960], "lin"]]);
  // a quick punch-in on the cut, then a slow push
  track(P(L, "Transform/Scale"), [[t0, [s * mo[0] * 1.12, s * mo[0] * 1.12]], [t0 + 0.32, [s * mo[0], s * mo[0]], "o5"],
    [t1, [s * mo[1], s * mo[1]], "lin"]]);
  if (key === "river") {
    var cb = fx(L, "ADBE Color Balance 2");
    var tint = comp.layers.addSolid(hex("#ff9a3c"), "Warm", 1080, 1920, 1, LEN);
    try { tint.blendingMode = BlendingMode.SOFT_LIGHT; } catch (e) {}
    P(tint, "Transform/Opacity").setValue(55); show(tint, t0, t1 + 0.04);
  }
  if (cr) { var C = text(cr, 24, "#ffffff", "left"); P(C, "Transform/Position").setValue([56, 236]);
    track(P(C, "Transform/Opacity"), [[t0, 0], [t0 + 0.25, 80], [t1 - 0.1, 80], [t1, 0]]); shadow(C, 2, 6);
    show(C, t0, t1); }
  FLASH.push(t0);
}
// photo grade: a little contrast and a vignette over the footage
var grade = comp.layers.addSolid([1, 1, 1], "Footage grade", 1080, 1920, 1, LEN); grade.adjustmentLayer = true;
var cvg = fx(grade, "CC Vignette"); if (cvg) setp(cvg, "Amount", 45);
show(grade, T.fish, T.ask);

// white flashes on the montage cuts, and when the map returns
var fl = comp.layers.addSolid([1, 1, 1], "Flash", 1080, 1920, 1, LEN);
var fk = [[0, 0]];
var cuts = FLASH.concat([T.turn, T.ask]);
cuts.sort(function (a, b) { return a - b; });
for (var i = 0; i < cuts.length; i++) { var c = cuts[i];
  fk.push([c - 0.001, 0]); fk.push([c + 0.04, 32, "o"]); fk.push([c + 0.2, 0, "io"]); }
track(P(fl, "Transform/Opacity"), fk);

// ==================================================================== closing comment bubble
var bub = shapeLayer("Comment bubble", null);
for (var d = -1; d <= 1; d++) { var gd = group(bub); path(gd, circle(d * 52, -6, 13, 20), true); fill(gd, "#0b1a2e"); }
var gbb = group(bub);
path(gbb, [[-110, -70], [110, -70], [124, -56], [124, 44], [110, 58], [-20, 58], [-58, 96], [-52, 58],
  [-110, 58], [-124, 44], [-124, -56]], true);
fill(gbb, "#ffd54a"); stroke(gbb, "#ffffff", 4);
P(bub, "Transform/Position").setValue([540, 1010]);
track(P(bub, "Transform/Scale"), [[T.write - 0.1, [0, 0]], [T.write + 0.35, [100, 100], "back"],
  [T.write + 1.0, [100, 100]], [T.write + 1.2, [108, 108], "o"], [T.write + 1.45, [100, 100], "io"]]);
track(P(bub, "Transform/Rotation"), [[T.write - 0.1, -12], [T.write + 0.4, 0, "back"]]);
shadow(bub, 8, 24); show(bub, T.write - 0.1, LEN);

// ==================================================================== caption shade + captions
var shade = comp.layers.addSolid([1, 1, 1], "Caption shade", 1080, 1920, 1, LEN);
var sr = fx(shade, "ADBE Ramp");
if (sr) { setp(sr, "Start of Ramp", [540, 1020]); setp(sr, "Start Color", [1, 1, 1]);
  setp(sr, "End of Ramp", [540, 1700]); setp(sr, "End Color", hex("#4a4a4a")); setp(sr, "Ramp Shape", 1); }
try { shade.blendingMode = BlendingMode.MULTIPLY; } catch (e) {}

var CX = 520, BOTTOM = 1435, MAXW = 840, NORMAL = 64, BIG = 98;
for (var b = 0; b < D.blocks.length; b++) {
  var blk = D.blocks[b], rows = [], tEnd = blk.end;
  for (var r = 0; r < blk.rows.length; r++) {
    var R = blk.rows[r], size = R.big ? BIG : NORMAL;
    var L = text(R.text, size, R.big ? "#ffd54a" : "#ffffff", "center");
    var rect = L.sourceRectAtTime(0, false);
    var wBold = rect.width * 1.07;                         // weight 700 sets ~7% wider than the measured 400
    if (wBold > MAXW) { size = Math.floor(size * MAXW / wBold);
      var td = L.property("Source Text").value; td.fontSize = size; L.property("Source Text").setValue(td);
      rect = L.sourceRectAtTime(0, false); }
    rows.push({ L: L, rect: rect, t: R.t, big: R.big, size: size });
  }
  // stack rows upwards from the bottom line
  var y = BOTTOM;
  for (var r = rows.length - 1; r >= 0; r--) {
    var Rw = rows[r], h = Rw.rect.height;
    var baseY = y - (Rw.rect.top + h);                     // baseline so the row's bottom sits at y
    Rw.y = baseY; y = y - h - (Rw.big ? 14 : 10);
  }
  for (var r = 0; r < rows.length; r++) {
    var Rw = rows[r], L = Rw.L, t0 = Math.max(0, Rw.t), t1 = tEnd;
    show(L, t0, t1);
    track(P(L, "Transform/Position"), [[t0, [CX, Rw.y + 26]], [t0 + 0.28, [CX, Rw.y], "o"]]);
    track(P(L, "Transform/Opacity"), [[t0, 0], [t0 + 0.12, 100, "o"], [t1 - 0.1, 100], [t1, 0, "lin"]]);
    if (Rw.big) track(P(L, "Transform/Scale"), [[t0, [128, 128]], [t0 + 0.32, [100, 100], "back"]]);
    shadow(L, 5, 16, 230);
    bold(L, 300);
  }
}

writeLn("TEXT_LAYERS=" + JSON.stringify(TEXT_LAYERS));
writeLn("layers " + comp.layers.length + " length " + LEN);
"""

# event times for the sound design (tools/sfx.py): cuts, counter steps, the closing bubble
COUNT_STEPS = [0, 0.26, 0.5, 0.72, 0.92]                 # must match cTimes in the JSX below
(HERE / "vm/times.json").write_text(json.dumps({
    "len": LEN, "T": T, "cuts": sorted([f[2] for f in FOOT] + [T["turn"], T["ask"]]),
    "count": [T["count"] + c for c in COUNT_STEPS],
    "map_spans": [[0, T["fish"]], [T["turn"], T["rowers"]], [T["ask"], LEN]],
}, indent=1))

out = JS.replace("__DATA__", json.dumps(DATA, ensure_ascii=False))
(HERE / "vm/short.jsx").write_text(out)
print(f"vm/short.jsx: {len(out) / 1024:.0f} KB, length {LEN:.2f}s, {len(TL['blocks'])} caption blocks, "
      f"{len(FOOT)} footage scenes")
for k, v in sorted(T.items(), key=lambda kv: kv[1]):
    print(f"  {v:6.2f}  {k}")
