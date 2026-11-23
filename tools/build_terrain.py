#!/usr/bin/env python3
"""Build data/terrain.json: a coarse terrain mesh of Lisbon.

Elevation samples (EU-DEM v1.1, 25 m, via the public Open Topo Data API) are taken on a
12 x 10 grid (about 1.4 km apart) plus at the 50 metro stations, then interpolated
(inverse-distance weighting, 8 nearest samples) on an 86 x 74 mesh. Cells inside the Tagus
polygon (data/shoreline.json) are set to 0 m.

Default: use the samples already stored in data/elevation_samples.json (offline).
--fetch: download fresh samples from the API (about 1 request per second) and save them.

Standard library only, Python 3.9+.
"""
import argparse
import json
import math
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BBOX = dict(lon0=-9.24, lon1=-9.07, lat0=38.68, lat1=38.80)
GRID_NX, GRID_NY = 12, 10
MESH_NX, MESH_NY = 86, 74
IDW_K = 8


def grid_axes():
    lons = [round(BBOX["lon0"] + (BBOX["lon1"] - BBOX["lon0"]) * i / (GRID_NX - 1), 5) for i in range(GRID_NX)]
    lats = [round(BBOX["lat1"] - (BBOX["lat1"] - BBOX["lat0"]) * j / (GRID_NY - 1), 5) for j in range(GRID_NY)]
    return lons, lats          # lats go from north to south


def fetch_elevations(points, api_url, dataset, batch=100, delay=1.1):
    """points: [(lat, lon)] -> [elevation or None]. Open Topo Data allows 100 points/request
    and about 1 request/second on the public instance."""
    out = []
    for k in range(0, len(points), batch):
        chunk = points[k:k + batch]
        body = json.dumps({"locations": "|".join(f"{a:.5f},{b:.5f}" for a, b in chunk)}).encode()
        req = urllib.request.Request(f"{api_url}/v1/{dataset}", data=body,
                                     headers={"Content-Type": "application/json"})
        for attempt in range(5):
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    data = json.load(r)
                break
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < 4:
                    time.sleep(2 + 2 * attempt)
                    continue
                raise
        out += [x["elevation"] for x in data["results"]]
        time.sleep(delay)
    return out


def point_in_polygon(lat, lon, poly):
    inside = False
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        if (a[1] > lon) != (b[1] > lon):
            t = (lon - a[1]) / (b[1] - a[1])
            if lat < a[0] + t * (b[0] - a[0]):
                inside = not inside
    return inside


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fetch", action="store_true", help="download new elevation samples")
    ap.add_argument("--stations", type=Path, default=ROOT / "data/raw/estacoes-de-metro.geojson")
    ap.add_argument("--samples", type=Path, default=ROOT / "data/elevation_samples.json")
    ap.add_argument("--shore", type=Path, default=ROOT / "data/shoreline.json")
    ap.add_argument("--out", type=Path, default=ROOT / "data/terrain.json")
    ap.add_argument("--api-url", default="https://api.opentopodata.org")
    ap.add_argument("--dataset", default="eudem25m")
    a = ap.parse_args()

    lons, lats = grid_axes()
    if a.fetch:
        gj = json.loads(a.stations.read_text(encoding="utf-8"))
        st = [(f["properties"]["NOME"], f["geometry"]["coordinates"][1], f["geometry"]["coordinates"][0])
              for f in gj["features"]]
        pts = [(la, lo) for la in lats for lo in lons] + [(la, lo) for _, la, lo in st]
        el = fetch_elevations(pts, a.api_url, a.dataset)
        g = len(lats) * len(lons)
        samples = {
            "source": "EU-DEM v1.1 25 m (Copernicus Land Monitoring Service) via Open Topo Data",
            "lons": lons, "lats": lats,
            "rows": [[None if v is None else round(v) for v in el[j * len(lons):(j + 1) * len(lons)]]
                     for j in range(len(lats))],
            "stations": [[n, la, lo, None if v is None else round(v)] for (n, la, lo), v in zip(st, el[g:])],
        }
        a.samples.write_text(json.dumps(samples, ensure_ascii=False), encoding="utf-8")
        print("wrote", a.samples)
    else:
        samples = json.loads(a.samples.read_text(encoding="utf-8"))

    # sample list: grid (null = sea = 0 m) + stations
    S = [(samples["lats"][j], samples["lons"][i], 0 if v is None else v)
         for j, row in enumerate(samples["rows"]) for i, v in enumerate(row)]
    S += [(la, lo, 0 if v is None else v) for _, la, lo, v in samples["stations"]]
    shore = json.loads(a.shore.read_text(encoding="utf-8"))

    heights = []
    for j in range(MESH_NY):
        la = BBOX["lat1"] - (BBOX["lat1"] - BBOX["lat0"]) * j / (MESH_NY - 1)
        for i in range(MESH_NX):
            lo = BBOX["lon0"] + (BBOX["lon1"] - BBOX["lon0"]) * i / (MESH_NX - 1)
            d = sorted((math.hypot((la - s[0]) * 111_200, (lo - s[1]) * 86_900), s[2]) for s in S)[:IDW_K]
            if d[0][0] < 1:
                h = d[0][1]
            else:
                w = [1 / x[0] ** 2 for x in d]
                h = sum(wi * x[1] for wi, x in zip(w, d)) / sum(w)
            if point_in_polygon(la, lo, shore):
                h = 0
            heights.append(max(0, int(round(h))))
    out = {"nx": MESH_NX, "ny": MESH_NY, "lon0": BBOX["lon0"], "lon1": BBOX["lon1"],
           "lat0": BBOX["lat0"], "lat1": BBOX["lat1"], "h": heights}
    a.out.write_text(json.dumps(out, separators=(",", ":")), encoding="utf-8")
    print(f"wrote {a.out}  (min {min(heights)} m, max {max(heights)} m)")


if __name__ == "__main__":
    main()
