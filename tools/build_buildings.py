#!/usr/bin/env python3
"""Build data/buildings.json: building footprints and heights for Lisbon from OpenStreetMap.

Source: OpenStreetMap, (c) OpenStreetMap contributors, licensed under the Open Database
License (ODbL) 1.0. data/buildings.json is a derived database and is also ODbL.

Steps
  1. --fetch: download every building inside the Lisbon municipality (OSM boundary
     "Lisboa", admin_level 7) from the public Overpass API, with geometry, into
     data/raw/osm-buildings.json (a large cache file, not committed to git).
  2. Convert the cache into a compact file:
     - outline: outer ring only (courtyards / inner rings are ignored), simplified
       with a 0.4 m tolerance, coordinates in metres from the map origin, rounded to
       0.5 m and delta-encoded;
     - height: OSM "height" tag if present; otherwise "building:levels" x 3 m;
       otherwise an estimate (3 m for small structures, 12 m for the rest).
       Each building records which of the three was used.
     Tiny outlines (under 8 m2) and open canopies (building=roof) are dropped.

Default (no --fetch): only step 2, from the cache.
Standard library only, Python 3.9+.
"""
import argparse
import json
import math
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OVERPASS = "https://overpass-api.de/api/interpreter"
QUERY = """[out:json][timeout:600];
area["name"="Lisboa"]["admin_level"="7"]["boundary"="administrative"]->.a;
(way["building"](area.a);relation["building"]["type"="multipolygon"](area.a););
out tags geom;"""

# Same map origin and scale as src/template.html (LAT0, LON0, KX*100, KZ*100)
LAT0, LON0 = 38.725, -9.14
M_PER_DEG_LON, M_PER_DEG_LAT = 86_900, 111_200
QUANT = 0.5            # metres per stored unit
SIMPLIFY_M = 0.4
MIN_AREA_M2 = 8
METRES_PER_LEVEL = 3.0
SMALL = {"garage", "garages", "shed", "kiosk", "hut", "cabin", "carport", "toilets",
         "container", "service", "transformer_tower", "bunker", "guardhouse"}
SKIP = {"roof", "no"}
# height source codes stored in the output
H_TAG, H_LEVELS, H_DEFAULT = 0, 1, 2


def fetch(cache: Path):
    body = urllib.parse.urlencode({"data": QUERY}).encode()
    req = urllib.request.Request(OVERPASS, data=body,
                                 headers={"User-Agent": "lisbon-underground-3d build script"})
    for attempt in range(5):
        try:
            print("downloading from Overpass (this can take a few minutes)...")
            with urllib.request.urlopen(req, timeout=900) as r:
                raw = r.read()
            break
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            if attempt == 4:
                raise
            wait = 30 * (attempt + 1)
            print(f"  failed ({e}); retrying in {wait} s")
            time.sleep(wait)
    data = json.loads(raw)
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_bytes(raw)
    print(f"wrote {cache} ({len(raw) / 1e6:.1f} MB, {len(data['elements'])} elements)")


def to_xy(lat, lon):
    return ((lon - LON0) * M_PER_DEG_LON, (lat - LAT0) * M_PER_DEG_LAT)


def join_rings(ways):
    """Join open way segments (lists of (lat, lon)) into closed rings."""
    ways = [list(w) for w in ways if len(w) >= 2]
    rings = []
    while ways:
        ring = ways.pop()
        changed = True
        while ring[0] != ring[-1] and changed:
            changed = False
            for i, w in enumerate(ways):
                if w[0] == ring[-1]:
                    ring += w[1:]
                elif w[-1] == ring[-1]:
                    ring += w[-2::-1]
                elif w[-1] == ring[0]:
                    ring = w[:-1] + ring
                elif w[0] == ring[0]:
                    ring = w[:0:-1] + ring
                else:
                    continue
                ways.pop(i)
                changed = True
                break
        if ring[0] == ring[-1] and len(ring) >= 4:
            rings.append(ring)
    return rings


def outer_rings(el):
    if el["type"] == "way":
        g = [(p["lat"], p["lon"]) for p in el.get("geometry", []) if p]
        return [g] if len(g) >= 4 and g[0] == g[-1] else []
    outers = [[(p["lat"], p["lon"]) for p in m.get("geometry", []) if p]
              for m in el.get("members", []) if m.get("role") == "outer" and m.get("type") == "way"]
    return join_rings(outers)


def simplify(pts, tol):
    """Douglas-Peucker on an open polyline of (x, y)."""
    if len(pts) < 3:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        (ax, ay), (bx, by) = pts[a], pts[b]
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy) or 1e-9
        best, bi = 0.0, None
        for i in range(a + 1, b):
            d = abs(dy * (pts[i][0] - ax) - dx * (pts[i][1] - ay)) / L
            if d > best:
                best, bi = d, i
        if bi is not None and best > tol:
            keep[bi] = True
            stack += [(a, bi), (bi, b)]
    return [p for p, k in zip(pts, keep) if k]


def simplify_ring(ring, tol):
    """Simplify a closed ring (first point not repeated at the end). Douglas-Peucker needs
    distinct end points, so split the ring at the vertex farthest from the first one."""
    if len(ring) < 4:
        return ring
    far = max(range(len(ring)), key=lambda i: math.hypot(ring[i][0] - ring[0][0], ring[i][1] - ring[0][1]))
    a = simplify(ring[:far + 1], tol)
    b = simplify(ring[far:] + [ring[0]], tol)
    return a[:-1] + b[:-1]


def area(ring):
    return sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(ring, ring[1:] + ring[:1])) / 2


def num(v):
    if v is None:
        return None
    m = re.match(r"^\s*(\d+(?:[.,]\d+)?)\s*(m|metres|meters)?\s*$", str(v))
    return float(m.group(1).replace(",", ".")) if m else None


def height_of(tags):
    h = num(tags.get("height"))
    if h and 1 <= h <= 300:
        return round(h), H_TAG
    lv = num(tags.get("building:levels"))
    if lv and 0 < lv <= 60:
        return max(3, round(lv * METRES_PER_LEVEL)), H_LEVELS
    return (3 if tags.get("building") in SMALL else 12), H_DEFAULT


def convert(cache: Path, out: Path):
    data = json.loads(cache.read_text(encoding="utf-8"))
    rows, stats = [], {H_TAG: 0, H_LEVELS: 0, H_DEFAULT: 0}
    dropped = 0
    for el in data["elements"]:
        tags = el.get("tags", {})
        if tags.get("building") in SKIP:
            continue
        for ring in outer_rings(el):
            xy = [to_xy(la, lo) for la, lo in ring[:-1]]
            xy = simplify_ring(xy, SIMPLIFY_M)
            q = []
            for x, y in xy:
                p = (round(x / QUANT), round(y / QUANT))
                if not q or p != q[-1]:
                    q.append(p)
            if len(q) > 1 and q[0] == q[-1]:
                q.pop()
            a = area([(x * QUANT, y * QUANT) for x, y in q]) if len(q) >= 3 else 0
            if len(q) < 3 or abs(a) < MIN_AREA_M2:
                dropped += 1
                continue
            if a < 0:                      # store counter-clockwise (x east, y north)
                q.reverse()
            flat = [q[0][0], q[0][1]]
            for (x0, y0), (x1, y1) in zip(q, q[1:]):
                flat += [x1 - x0, y1 - y0]
            h, src = height_of(tags)
            stats[src] += 1
            row = [flat, h, src]
            if tags.get("name"):
                row.append(tags["name"])
            rows.append(row)
    result = {
        "source": "OpenStreetMap via Overpass API",
        "attribution": "© OpenStreetMap contributors",
        "license": "ODbL 1.0 (https://opendatacommons.org/licenses/odbl/1-0/)",
        "osm_date": data.get("osm3s", {}).get("timestamp_osm_base"),
        "origin": [LAT0, LON0],
        "m_per_deg": [M_PER_DEG_LAT, M_PER_DEG_LON],
        "unit_m": QUANT,
        "format": "b: [[x0, y0, dx1, dy1, ...] in units of unit_m (east, north), height in m, "
                  "height source (0 = OSM height tag, 1 = from building:levels, 2 = estimate), name?]",
        "b": rows,
    }
    out.write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    n = len(rows)
    if not n:
        raise SystemExit("no buildings converted: check the cache file and the conversion settings")
    print(f"wrote {out} ({out.stat().st_size / 1e6:.1f} MB): {n} buildings, {dropped} tiny outlines dropped")
    print(f"  height from OSM tag: {stats[H_TAG]} ({100 * stats[H_TAG] / n:.0f}%), "
          f"from floors: {stats[H_LEVELS]} ({100 * stats[H_LEVELS] / n:.0f}%), "
          f"estimated: {stats[H_DEFAULT]} ({100 * stats[H_DEFAULT] / n:.0f}%)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fetch", action="store_true", help="download fresh data from Overpass first")
    ap.add_argument("--cache", type=Path, default=ROOT / "data/raw/osm-buildings.json")
    ap.add_argument("--out", type=Path, default=ROOT / "data/buildings.json")
    a = ap.parse_args()
    if a.fetch:
        fetch(a.cache)
    elif not a.cache.exists():
        raise SystemExit(f"{a.cache} not found: run with --fetch first")
    convert(a.cache, a.out)


if __name__ == "__main__":
    main()
