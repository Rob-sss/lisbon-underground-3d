#!/usr/bin/env python3
"""Build data/lines.json: ordered stations per metro line.

Inputs
  --stations  GeoJSON of the Lisbon metro stations (Câmara Municipal de Lisboa,
              dataset "Estações de Metro", resource POITransportes). Official positions.
  --gtfs      Metropolitano de Lisboa GTFS .zip (needs routes, trips and shapes).
              Used only for the ORDER of the stations along each line.
  --depths    JSON {normalized station name: depth in metres}. Depths are
              ILLUSTRATIVE (no open dataset with real tunnel depths was found).

Output: data/lines.json   (standard library only, Python 3.9+)
"""
import argparse
import csv
import io
import json
import math
import sys
import unicodedata
import zipfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# key -> (display name, colour). The key must match the start of the GTFS route
# name ("Azul - ...") after removing accents and lower-casing.
LINE_META = {
    "azul": ("Linha Azul", "#2f8cff"),
    "amarela": ("Linha Amarela", "#f5c400"),
    "verde": ("Linha Verde", "#2bb04a"),
    "vermelha": ("Linha Vermelha", "#ea4040"),
}
DEFAULT_DEPTH = 18      # metres, used when a station is missing from depths.json
MAX_SNAP_M = 250        # a GTFS shape point must be within this distance of a station


def norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.replace("-", " ").strip()


def dist_m(a, b):
    """Approximate distance in metres between (lat, lon) pairs, fine at Lisbon's latitude."""
    return math.hypot((a[0] - b[0]) * 111_200, (a[1] - b[1]) * 86_900)


def read_gtfs(zf: zipfile.ZipFile, name: str):
    matches = [n for n in zf.namelist() if n == name or n.endswith("/" + name)]
    if not matches:
        sys.exit(f"{name} not found in the GTFS zip")
    with zf.open(matches[0]) as fh:
        return list(csv.DictReader(io.TextIOWrapper(fh, encoding="utf-8-sig")))


def load_stations(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    out = []
    for f in data["features"]:
        lon, lat = f["geometry"]["coordinates"][:2]
        p = f["properties"]
        out.append({
            "name": p["NOME"],
            "lat": lat,
            "lon": lon,
            "lines": {norm(x) for x in p["LINHA"].split("/")},
        })
    return out


def pick_shapes(zf):
    """For every line pick one direction: among shapes used by trips of routes whose
    name starts with the line key, the one with most points (ties: lowest id)."""
    routes = {r["route_id"]: r["route_long_name"] for r in read_gtfs(zf, "routes.txt")}
    shape_of_route = defaultdict(set)
    for t in read_gtfs(zf, "trips.txt"):
        if t.get("shape_id"):
            shape_of_route[t["route_id"]].add(t["shape_id"])
    shapes = defaultdict(list)
    for r in read_gtfs(zf, "shapes.txt"):
        shapes[r["shape_id"]].append((int(r["shape_pt_sequence"]),
                                      float(r["shape_pt_lat"]), float(r["shape_pt_lon"])))
    chosen = {}
    for key in LINE_META:
        cands = []
        for rid, long_name in routes.items():
            if norm(long_name).startswith(key):
                for sid in shape_of_route.get(rid, ()):
                    cands.append((-len(shapes[sid]), int(sid) if sid.isdigit() else 0, sid))
        if not cands:
            sys.exit(f"no GTFS shape found for line '{key}'")
        sid = sorted(cands)[0][2]
        chosen[key] = [(la, lo) for _, la, lo in sorted(shapes[sid])]
        print(f"{key}: shape {sid} with {len(chosen[key])} points")
    return chosen


def snap(points, stations, key):
    seq = []
    for p in points:
        best = min(stations, key=lambda s: dist_m(p, (s["lat"], s["lon"])))
        d = dist_m(p, (best["lat"], best["lon"]))
        if d > MAX_SNAP_M:
            sys.exit(f"{key}: shape point {p} is {d:.0f} m from the nearest station")
        if not seq or seq[-1] is not best:
            seq.append(best)
    return seq


def insert_missing(seq, stations, key):
    """Some GTFS shapes skip a station (e.g. Arroios on the Green line). Stations that
    the official file assigns to this line but are absent from the sequence are
    inserted where they add the least extra length."""
    names = {s["name"] for s in seq}
    for s in stations:
        if key in s["lines"] and s["name"] not in names:
            pt = (s["lat"], s["lon"])
            best_i, best_cost = None, None
            for i in range(len(seq) + 1):
                a = seq[i - 1] if i > 0 else None
                b = seq[i] if i < len(seq) else None
                if a and b:
                    cost = (dist_m((a["lat"], a["lon"]), pt) + dist_m(pt, (b["lat"], b["lon"]))
                            - dist_m((a["lat"], a["lon"]), (b["lat"], b["lon"])))
                else:
                    e = a or b
                    cost = dist_m((e["lat"], e["lon"]), pt)
                if best_cost is None or cost < best_cost:
                    best_i, best_cost = i, cost
            seq.insert(best_i, s)
            names.add(s["name"])
            print(f"{key}: inserted {s['name']} at position {best_i} (missing from GTFS shape)")
    return seq


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stations", type=Path, default=ROOT / "data/raw/estacoes-de-metro.geojson")
    ap.add_argument("--gtfs", type=Path, required=True, help="Metropolitano de Lisboa GTFS .zip")
    ap.add_argument("--depths", type=Path, default=ROOT / "data/depths.json")
    ap.add_argument("--out", type=Path, default=ROOT / "data/lines.json")
    a = ap.parse_args()

    stations = load_stations(a.stations)
    depths = json.loads(a.depths.read_text(encoding="utf-8"))
    with zipfile.ZipFile(a.gtfs) as zf:
        shapes = pick_shapes(zf)

    out = {}
    for key, (title, colour) in LINE_META.items():
        seq = insert_missing(snap(shapes[key], stations, key), stations, key)
        out[key] = {
            "name": title,
            "color": colour,
            "stations": [[s["name"], round(s["lat"], 5), round(s["lon"], 5),
                          depths.get(norm(s["name"]), DEFAULT_DEPTH)] for s in seq],
        }
        print(f"{key}: {len(seq)} stations")
    a.out.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print("wrote", a.out)


if __name__ == "__main__":
    main()
