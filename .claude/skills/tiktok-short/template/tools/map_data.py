"""Natural Earth (public domain) -> map geometry for the EffectCraft build, in "map pixels".

Map pixels: equirectangular around (LON0, LAT0), K pixels per degree of latitude (x shrunk by cos LAT0), y down.
EffectCraft shape layers are parented to a camera null, so zoom 1 = these pixels on the 1080x1920 frame.

Run: uv run --with pyshp --with shapely --with numpy python tools/map_data.py <natural-earth dir>
Writes vm/map.json.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import shapefile
from shapely.geometry import LineString, MultiLineString, Polygon, box, shape
from shapely.ops import linemerge

HERE = Path(__file__).resolve().parent.parent
NE = Path(sys.argv[1])
LON0, LAT0, K = 104.6, 12.6, 330.0
COS0 = math.cos(math.radians(LAT0))
VIEW = box(99.0, 5.5, 111.0, 19.5)          # everything any camera move can show
N_LAKE = 180                                # vertices per lake outline (both shapes, so the path can morph)


def xy(lon: float, lat: float) -> list[float]:
    return [round((lon - LON0) * K * COS0, 1), round(-(lat - LAT0) * K, 1)]


def ring(coords) -> list[list[float]]:
    return [xy(x, y) for x, y in coords]


def read(name: str, enc: str = "utf-8"):
    r = shapefile.Reader(str(NE / name / f"{name}.shp"), encoding=enc)
    fields = [f[0] for f in r.fields[1:]]
    for sr in r.iterShapeRecords():
        yield dict(zip(fields, sr.record)), shape(sr.shape.__geo_interface__)


def polys(g, min_area: float) -> list:
    parts = [g] if g.geom_type == "Polygon" else list(getattr(g, "geoms", []))
    return [p for p in parts if p.geom_type == "Polygon" and p.area >= min_area]


out: dict = {"k": K, "lon0": LON0, "lat0": LAT0, "neighbors": [], "provinces": [], "rivers_minor": []}

for rec, g in read("ne_10m_admin_0_countries"):
    name = rec["ADMIN"]
    if name == "Cambodia":
        main = max(polys(g, 0), key=lambda p: p.area).simplify(0.006)
        out["cambodia"] = ring(main.exterior.coords)
    elif name in ("Thailand", "Laos", "Vietnam", "Malaysia", "Myanmar"):
        for p in polys(g.intersection(VIEW), 0.05):
            out["neighbors"].append({"name": name, "ring": ring(p.simplify(0.01).exterior.coords)})

for rec, g in read("ne_10m_admin_1_states_provinces"):
    if rec["admin"] == "Cambodia":
        for p in polys(g, 0.002):
            out["provinces"].append({"name": rec["name"], "ring": ring(p.simplify(0.006).exterior.coords),
                                     "c": xy(*p.representative_point().coords[0])})

for rec, g in read("ne_10m_rivers_lake_centerlines"):
    if not g.intersects(VIEW):
        continue
    name, cla = rec.get("name") or "", rec.get("featurecla") or ""
    g = g.intersection(VIEW)
    if name == "Mekong":
        # Natural Earth splits it: Laos pieces, Pakse -> Phnom Penh, then two delta branches out of Phnom Penh.
        # Chain north -> south: west Laos piece (reversed), Laos to Pakse, Pakse to Phnom Penh, main branch to the sea.
        parts = [list(q.coords) for q in (g.geoms if g.geom_type == "MultiLineString" else [g])]
        near = lambda a, b: abs(a[0] - b[0]) < 0.05 and abs(a[1] - b[1]) < 0.05
        pp = (104.95, 11.59)
        chain = []
        laos_w = next((c for c in parts if near(c[-1], (101.56, 17.82))), None)
        if laos_w:
            chain += laos_w[::-1]
        chain += next(c for c in parts if near(c[-1], (105.77, 15.13)))
        chain += next(c for c in parts if near(c[0], (105.78, 15.12)))
        sea_main = next(c for c in parts if near(c[-1], pp) and near(c[0], (106.12, 10.24)))
        chain += sea_main[::-1]
        out["mekong"] = ring(LineString(chain).simplify(0.004).coords)
        bassac = next(c for c in parts if near(c[-1], pp) and near(c[0], (105.84, 10.0)))
        out["bassac"] = ring(LineString(bassac[::-1]).simplify(0.004).coords)
    elif name == "Tonle Sap" and "River" in cla:
        c = list(g.coords)
        if c[0][1] < c[-1][1]:
            c.reverse()                                       # lake (north) -> Phnom Penh (south)
        out["tonle_sap_river"] = ring(LineString(c).simplify(0.002).coords)
    elif "Lake Centerline" not in cla:
        for part in (g.geoms if g.geom_type == "MultiLineString" else [g]):
            if part.length > 0.3 and part.intersects(box(101.5, 9.5, 108.0, 15.5)):
                out["rivers_minor"].append(ring(part.simplify(0.006).coords))

# the lake: dry season (Natural Earth outline) and wet season (about 5x the area)
lake = None
for rec, g in read("ne_10m_lakes"):
    if g.intersects(box(103.5, 12.2, 104.8, 13.4)):
        lake = max(polys(g, 0), key=lambda p: p.area)
pts = np.array(lake.exterior.coords)
c0 = pts.mean(axis=0)
cov = np.cov((pts - c0).T)
evals, evecs = np.linalg.eigh(cov)
major, minor = evecs[:, 1], evecs[:, 0]


def wet_shape(p: Polygon, ratio: float = 5.0) -> Polygon:
    """The flooded lake: an even ring around the dry shoreline, grown until the area is `ratio` times larger."""
    lo, hi = 0.0, 0.5
    for _ in range(40):
        d = (lo + hi) / 2
        lo, hi = (d, hi) if p.buffer(d, 32).area < ratio * p.area else (lo, d)
    return p.buffer(d, 32).simplify(0.004)


def resample(p: Polygon, n: int) -> list[list[float]]:
    """n points evenly along the outline, counter-clockwise, starting at the end the major axis points to."""
    ext = p.exterior
    if not ext.is_ccw:
        ext = LineString(list(ext.coords)[::-1])
    tip = c0 + major * 5.0
    start = ext.project(LineString([tuple(c0), tuple(tip)]).interpolate(1.0))
    total = ext.length
    out_pts = []
    for i in range(n):
        q = ext.interpolate((start + total * i / n) % total)
        out_pts.append(xy(q.x, q.y))
    return out_pts


dry = Polygon(lake.exterior.coords)
wet = wet_shape(dry)
out["lake_dry"] = resample(dry, N_LAKE)
out["lake_wet"] = resample(wet, N_LAKE)
km2 = lambda p: p.area * (111.32 ** 2) * COS0
out["lake_km2"] = {"dry": round(km2(dry)), "wet": round(km2(wet))}
out["lake_center"] = xy(*c0)

# places and label anchors (map pixels)
out["places"] = {
    "phnom_penh": xy(104.92, 11.56),
    "siem_reap": xy(103.86, 13.36),
    "label_cambodia": xy(104.9, 12.95),
    "label_lake": xy(103.95, 13.45),
    "label_mekong": xy(105.5, 12.85),
    "label_tonle_sap": xy(104.45, 11.95),
    "label_thailand": xy(101.6, 14.6),
    "label_laos": xy(105.2, 15.9),
    "label_vietnam": xy(107.6, 12.2),
}
(HERE / "vm").mkdir(exist_ok=True)
(HERE / "vm/map.json").write_text(json.dumps(out))
print("cambodia", len(out["cambodia"]), "| neighbors", len(out["neighbors"]), "| provinces", len(out["provinces"]),
      "| mekong", len(out["mekong"]), "| tonle sap river", len(out["tonle_sap_river"]),
      "| minor rivers", len(out["rivers_minor"]), "| lake km2", out["lake_km2"])
