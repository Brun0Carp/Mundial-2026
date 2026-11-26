#!/usr/bin/env python3
"""Empaqueta los fotogramas renderizados por codeart2d en una hoja (8 columnas, una fila por acción)
y la incrusta en rpg-medieval.html como data URI, junto con los tiempos de cada clip.

Uso: python3 build_sheet.py   (después de render_pixelspec.py --output-dir render)
"""
import base64, io, json, os, re
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
spec = json.load(open(os.path.join(HERE, "caballero.pixelspec.json"), encoding="utf-8"))
meta = json.load(open(os.path.join(HERE, "render", "codeart-meta.json"), encoding="utf-8"))
assert meta["art_source"] == "code" and meta["qa"]["status"] == "pass", "el render no pasó el control de calidad"
size = spec["canvas"][0]
order = ["idle", "walk", "run", "jump", "crouch", "attack", "shoot", "cast"]
sheet = Image.new("RGBA", (size * 8, size * len(order)), (0, 0, 0, 0))
clips = {}
for row, name in enumerate(order):
    c = spec["clips"][name]
    for col, fname in enumerate(c["frames"]):
        sheet.paste(Image.open(os.path.join(HERE, "render", "base", "frames", fname + ".png")), (col * size, row * size))
    n = len(c["frames"])
    dur = c["duration_ms"] if isinstance(c["duration_ms"], list) else [c["duration_ms"]] * n
    clips[name] = {"row": row, "n": n, "dur": dur, "loop": c["loop"], "events": {e["name"].replace("custom:", ""): e["at"] for e in c.get("events", [])}}
sheet.save(os.path.join(HERE, "caballero-sheet.png"), optimize=True)
json.dump({"size": size, "anchor": spec["anchor_px"], "clips": clips}, open(os.path.join(HERE, "caballero-clips.json"), "w"), indent=1)

buf = io.BytesIO(); sheet.save(buf, format="PNG", optimize=True)
data = {"size": size, "anchor": spec["anchor_px"], "clips": clips, "src": "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()}
html_path = os.path.join(HERE, "..", "..", "rpg-medieval.html")
html = open(html_path, encoding="utf-8").read()
block = "/*CABALLERO_INICIO*/" + json.dumps(data, separators=(",", ":")) + "/*CABALLERO_FIN*/"
if "/*CABALLERO_INICIO*/" in html:
    html = re.sub(r"/\*CABALLERO_INICIO\*/.*?/\*CABALLERO_FIN\*/", lambda m: block, html, flags=re.S)
    open(html_path, "w", encoding="utf-8").write(html)
    print("hoja incrustada:", len(buf.getvalue()), "bytes PNG,", sum(c["n"] for c in clips.values()), "fotogramas")
else:
    print("hoja escrita (aún no hay marcador en el HTML):", len(buf.getvalue()), "bytes")
