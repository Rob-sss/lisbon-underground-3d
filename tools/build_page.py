#!/usr/bin/env python3
"""Assemble the web page from src/template.html and the files in data/.

Writes
  index.html                    loads three.js from a CDN (small file)
  lisbon-underground-3d.html    three.js inlined (opens offline, no server needed)

Standard library only, Python 3.9+.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CDN_THREE = '<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>'
CDN_ORBIT = '<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>'


def hexnum(colour: str) -> str:
    return "0x" + colour.lstrip("#")


def load(name):
    return json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))


def js_lines(lines):
    parts = []
    for key, L in lines.items():
        st = ",".join(json.dumps(s, ensure_ascii=False) for s in L["stations"])
        parts.append(f'  {key}:{{name:{json.dumps(L["name"], ensure_ascii=False)},color:{hexnum(L["color"])},st:[{st}]}}')
    return "{\n" + ",\n".join(parts) + "\n}"


def js_other(layers):
    parts = []
    for key, o in layers.items():
        parts.append(
            f'  {key}:{{name:{json.dumps(o["name"], ensure_ascii=False)},color:{hexnum(o["color"])},'
            f'layer:{json.dumps(o["layer"])},desc:{json.dumps(o["desc"], ensure_ascii=False)},'
            f'pts:{json.dumps(o["pts"])}}}')
    return "{\n" + ",\n".join(parts) + "\n}"


def main():
    t = (ROOT / "src/template.html").read_text(encoding="utf-8")
    t = t.replace("/*__LINES__*/", js_lines(load("lines.json")))
    t = t.replace("/*__OTHER__*/", js_other(load("hand_drawn_layers.json")))
    t = t.replace("/*__SHORE__*/", json.dumps(load("shoreline.json")))
    t = t.replace("/*__TERRAIN__*/", (ROOT / "data/terrain.json").read_text(encoding="utf-8").strip())
    for marker in ("/*__LINES__*/", "/*__OTHER__*/", "/*__SHORE__*/", "/*__TERRAIN__*/"):
        assert marker not in t, marker
    (ROOT / "index.html").write_text(t, encoding="utf-8")

    three = (ROOT / "vendor/three.min.js").read_text(encoding="utf-8")
    orbit = (ROOT / "vendor/OrbitControls.js").read_text(encoding="utf-8")
    assert CDN_THREE in t and CDN_ORBIT in t, "CDN script tags not found in template"
    s = t.replace(CDN_THREE, "<script>" + three.replace("</script>", "<\\/script>") + "</script>")
    s = s.replace(CDN_ORBIT, "<script>" + orbit.replace("</script>", "<\\/script>") + "</script>")
    (ROOT / "lisbon-underground-3d.html").write_text(s, encoding="utf-8")
    print("wrote index.html and lisbon-underground-3d.html")


if __name__ == "__main__":
    main()
