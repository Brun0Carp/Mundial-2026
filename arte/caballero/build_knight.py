#!/usr/bin/env python3
"""Genera caballero.pixelspec.json: un caballero de pixel art de perfil (mirando a la derecha).

Arte dibujado con código (codeart2d de agent-sprite-forge, sin modelo de imagen).
Cada fotograma se describe con un esqueleto: cadera, pies y manos (rodillas y codos por IK de
dos huesos), ángulo de la espada, vuelo de la capa y efectos. Las piezas se rasterizan en capas
(capa, brazo lejano, pierna lejana, pierna cercana, torso, cabeza, brazo cercano, arma, efectos)
y el renderizador de codeart2d añade el contorno y hace el control de calidad.

Uso: python3 build_knight.py  (escribe caballero.pixelspec.json junto a este archivo)
"""
import json, math, os

W, H = 48, 48            # lienzo
HIP_X, HIP_Y = 18, 35    # cadera en reposo
GROUND = 44              # fila superior de la bota apoyada (la suela queda en la fila 46)
ANCHOR = [18, 47]        # raíz: borde inferior del contorno de las botas

PALETTE = {
    "k": "#1a1c2c",                                   # contorno (el mismo que el resto del juego)
    "A": "#e2e8f0", "a": "#a9b8c8", "m": "#6b7d96",   # acero cercano: luz, base, sombra
    "M": "#46536b", "d": "#333c57",                   # acero lejano (más oscuro para que se lea la zancada)
    "b": "#3b5dc9", "B": "#29366f",                   # sobreveste azul (el color de Aldren)
    "y": "#ffcd75", "Y": "#c98a3b",                   # oro: emblema, guarda, hebilla
    "r": "#d0465a", "R": "#7a2337",                   # capa y penacho rojos
    "n": "#8b5a2b", "N": "#4a2c14", "D": "#2e1c0e",   # cuero: botas, cinturón, arco
    "w": "#f4f4f4", "e": "#94b0c2",                   # hoja de la espada
    "c": "#41a6f6", "C": "#73eff7", "W": "#ffffff",   # magia
    "g": "#c2c3c7",                                    # polvo
}

HELMET = [
    "..AAAAA...",
    ".AaaaaaA..",
    "Aaaaaaaaa.",
    "aaaayyyyy.",
    "aaaakkkkkk",
    "maaaaaaaaa",
    "maaaakkkaa",
    ".mmaaaaam.",
    "..mmmmmm..",
]
PLUME = [".rrr", "rrR.", "rR..", "R..."]
TORSO = [
    "..mAAaam..",
    ".AAaaaaaam",
    ".Aaaaaaaam",
    ".abbbbbbbm",
    ".bbbbybbbB",
    ".bbbyyybbB",
    ".bbbbybbbB",
    ".NnnnynnnN",
    ".bbbbbbbbB",
    ".bbbbbbbbB",
    "..BbbbbbB.",
]
BOOT_NEAR = ["NNN..", "NnnNn", "NNNNN"]
BOOT_FAR = ["DDD..", "DNNDN", "DDDDD"]


class Canvas:
    def __init__(self):
        self.g = [["." for _ in range(W)] for _ in range(H)]

    def put(self, x, y, ch):
        x, y = int(round(x)), int(round(y))
        if 1 <= x < W - 1 and 1 <= y < H - 1:      # deja 1 px de margen para el contorno
            self.g[y][x] = ch

    def get(self, x, y):
        return self.g[y][x] if 0 <= x < W and 0 <= y < H else "."

    def stamp(self, rows, ox, oy):
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch != ".":
                    self.put(ox + i, oy + j, ch)

    def line(self, x0, y0, x1, y1, ch, brush=1):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        n = int(math.ceil(n))
        for s in range(n + 1):
            t = s / n
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            if brush == 1:
                self.put(x, y, ch)
            elif brush == 2:
                for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
                    self.put(math.floor(x) + dx, math.floor(y) + dy, ch)
            else:  # 3: cruz
                for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                    self.put(round(x) + dx, round(y) + dy, ch)

    def shade(self, base, light, dark):
        """Luz desde arriba a la izquierda: borde superior/izquierdo claro, inferior/derecho oscuro."""
        src = [r[:] for r in self.g]
        for y in range(H):
            for x in range(W):
                if src[y][x] != base:
                    continue
                if src[y - 1][x] == "." or src[y][x - 1] == ".":
                    self.g[y][x] = light
                elif src[y + 1][x] == "." or src[y][x + 1] == ".":
                    self.g[y][x] = dark

    def poly(self, pts, ch):
        ys = [p[1] for p in pts]
        for y in range(int(min(ys)), int(max(ys)) + 1):
            xs = []
            for i in range(len(pts)):
                (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % len(pts)]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for a, b in zip(xs[::2], xs[1::2]):
                for x in range(int(round(a)), int(round(b)) + 1):
                    self.put(x, y, ch)

    def empty(self):
        return all(ch == "." for row in self.g for ch in row)


def ik(root, target, l1, l2, bend):
    """IK de dos huesos: devuelve la articulación intermedia. bend=+1 dobla hacia delante (rodilla)."""
    dx, dy = target[0] - root[0], target[1] - root[1]
    d = max(0.01, min(math.hypot(dx, dy), l1 + l2 - 0.01))
    a = math.atan2(dy, dx)
    cos_k = (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d)
    k = math.acos(max(-1, min(1, cos_k)))
    ang = a - bend * k
    return (root[0] + l1 * math.cos(ang), root[1] + l1 * math.sin(ang))


def draw_frame(p):
    """p: diccionario del esqueleto de un fotograma. Devuelve {capa: Canvas}."""
    bx, by = p.get("dx", 0), p.get("dy", 0)
    lean = p.get("lean", 0)                      # el torso y la cabeza se adelantan al correr
    hip = (HIP_X + bx, HIP_Y + by)
    top_x = hip[0] + lean
    L = {n: Canvas() for n in ("cape", "far_arm", "far_leg", "near_leg", "torso", "head", "near_arm", "weapon", "fx")}

    # capa (detrás de todo): un triángulo que vuela hacia atrás según p["cape"] (0 quieta .. 1 al viento)
    f = p.get("cape", 0.3)
    sx, sy = top_x - 3, hip[1] - 10
    tail_x = sx - 2 - 9 * f
    tail_y = min(hip[1] + 6 - 5 * f, GROUND + 1)
    L["cape"].poly([(sx, sy), (sx + 4, sy), (sx + 2, tail_y), (tail_x + 2, tail_y + 1 - 2 * f), (tail_x, tail_y - 2 * f)], "r")
    L["cape"].shade("r", "r", "R")

    # piernas: la cadera es la raíz, el pie (tobillo) es el objetivo; la rodilla dobla hacia delante
    for side, layer, col, boot in (("ff", "far_leg", "M", BOOT_FAR), ("nf", "near_leg", "a", BOOT_NEAR)):
        foot = p[side]
        root = (hip[0] + (-1 if side == "ff" else 1), hip[1])
        knee = ik(root, foot, 5, 5, +1)
        c = L[layer]
        c.line(root[0], root[1], knee[0], knee[1], col, 3)
        c.line(knee[0], knee[1], foot[0], foot[1] - 1, col, 2 if side == "ff" else 3)
        c.stamp(boot, round(foot[0]) - 1, round(foot[1]))
        if side == "nf":
            c.shade("a", "A", "m")
            c.put(knee[0] + 1, knee[1], "A")          # rodillera
        else:
            c.shade("M", "M", "d")

    # torso y cabeza
    L["torso"].stamp(TORSO, top_x - 5, hip[1] - 11)
    hy = hip[1] - 20 + p.get("head_dy", 0)
    L["head"].stamp(HELMET, top_x - 4, hy)
    L["head"].stamp(PLUME, top_x - 6, hy - 3)

    # brazos: hombro -> mano (el codo dobla hacia atrás)
    for side, layer, col in (("fh", "far_arm", "M"), ("nh", "near_arm", "a")):
        sh = (top_x + (-2 if side == "fh" else 1), hip[1] - 9)
        hand = p[side]
        elbow = ik(sh, hand, 4, 4, -1)
        c = L[layer]
        c.line(sh[0], sh[1], elbow[0], elbow[1], col, 2)
        c.line(elbow[0], elbow[1], hand[0], hand[1], col, 2)
        if side == "nh":
            c.shade("a", "A", "m")
            c.put(hand[0], hand[1], "m"); c.put(hand[0] + 1, hand[1], "a")   # guantelete
        else:
            c.shade("M", "M", "d")

    # arma
    hx, hyy = p["nh"]
    if p.get("sword") is not None:
        a = math.radians(p["sword"]); ca, sa = math.cos(a), math.sin(a)
        L["weapon"].line(hx - ca * 2, hyy - sa * 2, hx, hyy, "N")                 # empuñadura
        L["weapon"].put(hx - ca * 3, hyy - sa * 3, "y")                             # pomo
        for t in (-1.5, -0.5, 0.5, 1.5):                                             # guarda perpendicular
            L["weapon"].put(hx + ca + (-sa) * t, hyy + sa + ca * t, "y")
        L["weapon"].line(hx + ca * 2, hyy + sa * 2, hx + ca * 12, hyy + sa * 12, "w")  # hoja
        L["weapon"].put(hx + ca * 12, hyy + sa * 12, "e")
    if p.get("bow"):
        draw = p.get("draw", 0)                 # 0 cuerda recta .. 4 tensada
        bxx, byy = hx + 1, hyy
        pts = [(bxx - 1 + 3 * math.cos(math.pi * (t / 12 - 0.5)) , byy + 6 * math.sin(math.pi * (t / 12 - 0.5))) for t in range(13)]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            L["weapon"].line(x0, y0, x1, y1, "n")
        top, bot = pts[0], pts[-1]
        pull = (bxx - 1 - draw, byy)
        L["weapon"].line(top[0], top[1], pull[0], pull[1], "w")
        L["weapon"].line(pull[0], pull[1], bot[0], bot[1], "w")
        if p.get("nock"):
            L["weapon"].line(pull[0], byy, bxx + 4, byy, "n")
            L["weapon"].put(bxx + 5, byy, "e"); L["weapon"].put(pull[0], byy - 1, "r"); L["weapon"].put(pull[0], byy + 1, "r")

    # efectos
    fx = L["fx"]
    for kind, *args in p.get("fx", []):
        if kind == "arc":            # estela del tajo: media luna maciza que se afina hacia la cola
            cx, cy, r, a0, a1 = args
            steps = int(abs(a1 - a0) * r / 25) + 12
            for k in range(steps + 1):
                t = k / steps                                   # 0 = cola, 1 = filo de la espada
                a = math.radians(a0 + (a1 - a0) * t)
                width = 1 if t < 0.3 else (2 if t < 0.6 else 3)
                for w_i in range(width):
                    col = ("W", "C", "c")[w_i] if t > 0.5 else ("C", "c", "c")[w_i]
                    fx.put(cx + (r - w_i) * math.cos(a), cy + (r - w_i) * math.sin(a), col)
        elif kind == "arrow":
            x, y = args
            fx.line(x, y, x + 8, y, "n"); fx.put(x + 9, y, "w"); fx.put(x + 10, y, "e")
            fx.put(x, y - 1, "r"); fx.put(x, y + 1, "r")
        elif kind == "orb":
            x, y, r = args
            for j in range(-r, r + 1):
                for i in range(-r, r + 1):
                    d = math.hypot(i, j)
                    if d <= r + 0.3:
                        fx.put(x + i, y + j, "W" if d < r * 0.4 else ("C" if d < r * 0.75 else "c"))
        elif kind == "spark":
            for x, y in args[0]:
                fx.put(x, y, "W"); fx.put(x - 1, y, "C"); fx.put(x + 1, y, "C"); fx.put(x, y - 1, "C"); fx.put(x, y + 1, "C")
        elif kind == "dust":
            for x, y in args[0]:
                fx.put(x, y, "g"); fx.put(x + 1, y, "g"); fx.put(x, y - 1, "e")
    return L


# ------------------------------------------------------------------- poses de cada acción
def walk(i, n=8, stride=4, lift=2, run=False):
    ph = 2 * math.pi * i / n
    def foot(off):
        c = math.cos(ph + off)
        swing = math.sin(ph + off) < 0           # la pierna que va hacia delante se levanta
        up = lift * abs(math.sin(ph + off)) if swing else 0
        return (HIP_X + stride * c, GROUND - up)
    contact = abs(math.cos(ph)) > 0.9
    p = {"nf": foot(0), "ff": foot(math.pi), "dy": (1 if contact else 0) if not run else (1 if contact else -1)}
    sw = -math.cos(ph - 0.7)                     # brazos desfasados de las piernas: el paso se lee mejor
    if run:
        p.update(lean=1, cape=0.85 + 0.15 * math.sin(ph * 2))
        p["nh"] = (HIP_X + 4 + 3 * sw, HIP_Y - 5 + p["dy"] - abs(sw) * 2)
        p["fh"] = (HIP_X - 1 - 3 * sw, HIP_Y - 4 + p["dy"])
        p["sword"] = 200 + 10 * sw              # espada hacia atrás al correr
        if contact:
            p["fx"] = [("dust", [(HIP_X - 6, GROUND + 2), (HIP_X - 9, GROUND + 1)])]
    else:
        p.update(cape=0.3 + 0.1 * math.sin(ph))
        p["nh"] = (HIP_X + 3 + 2 * sw, HIP_Y - 2 + p["dy"])
        p["fh"] = (HIP_X - 2 - 2 * sw, HIP_Y - 2 + p["dy"])
        p["sword"] = 35
    return p


REST = {"nf": (HIP_X + 2, GROUND), "ff": (HIP_X - 2, GROUND), "nh": (HIP_X + 4, HIP_Y - 2), "fh": (HIP_X - 2, HIP_Y - 2), "sword": 35, "cape": 0.3}


def pose(**kw):
    p = dict(REST); p.update(kw)
    dy = p.get("dy", 0)
    # las manos se describen relativas al cuerpo en reposo: siguen al cuerpo cuando sube o baja
    for k in ("nh", "fh"):
        if k in kw:
            p[k] = (kw[k][0] + p.get("dx", 0), kw[k][1] + dy)
        else:
            p[k] = (REST[k][0] + p.get("dx", 0), REST[k][1] + dy)
    return p


FRAMES = {}
FRAMES["idle"] = [pose(dy=0, cape=0.3), pose(dy=0, cape=0.35), pose(dy=1, cape=0.3), pose(dy=1, cape=0.25)]
FRAMES["walk"] = [walk(i) for i in range(8)]
FRAMES["run"] = [walk(i, stride=6, lift=4, run=True) for i in range(8)]

air = lambda dy, tuck: {"nf": (HIP_X + 2, HIP_Y + dy + 9 - tuck), "ff": (HIP_X - 2, HIP_Y + dy + 8 - tuck)}
FRAMES["jump"] = [
    pose(dy=3, nh=(HIP_X + 3, HIP_Y - 1), fh=(HIP_X - 3, HIP_Y - 1), cape=0.3),
    pose(dy=5, nh=(HIP_X - 1, HIP_Y + 1), fh=(HIP_X - 5, HIP_Y), sword=150, cape=0.35, fx=[("dust", [(HIP_X - 4, GROUND + 2), (HIP_X + 5, GROUND + 2)])]),
    {**pose(dy=-3, nh=(HIP_X + 6, HIP_Y - 9), fh=(HIP_X + 1, HIP_Y - 8), sword=-60, cape=0.6), **air(-3, 0)},
    {**pose(dy=-8, nh=(HIP_X + 6, HIP_Y - 9), fh=(HIP_X + 1, HIP_Y - 8), sword=-45, cape=0.8), **air(-8, 3)},
    {**pose(dy=-11, nh=(HIP_X + 6, HIP_Y - 7), fh=(HIP_X, HIP_Y - 7), sword=-20, cape=0.9), **air(-11, 4)},
    {**pose(dy=-8, nh=(HIP_X + 5, HIP_Y - 5), fh=(HIP_X - 1, HIP_Y - 6), sword=10, cape=1.0), **air(-8, 1)},
    pose(dy=4, nh=(HIP_X + 5, HIP_Y - 1), fh=(HIP_X - 4, HIP_Y - 3), sword=40, cape=0.6, fx=[("dust", [(HIP_X - 6, GROUND + 2), (HIP_X + 6, GROUND + 2), (HIP_X - 9, GROUND + 1), (HIP_X + 9, GROUND + 1)])]),
    pose(dy=1, cape=0.35),
]
# agacharse: baja en 4 fotogramas, aguanta 2 (respira y apoya la espada) y se levanta en 2
CROUCH = [(1, 40, 0.30, 0), (3, 50, 0.28, 0), (5, 60, 0.25, 0), (7, 75, 0.22, 0),
          (7, 85, 0.20, 1), (6, 80, 0.22, 0), (4, 60, 0.26, 0), (2, 45, 0.30, 0)]
FRAMES["crouch"] = [pose(dy=d, nh=(HIP_X + 4 + d // 2, HIP_Y - 2 + d // 3 + hd), fh=(HIP_X - 2 - d // 4, HIP_Y - 2), sword=sw_a, cape=cp,
                         nf=(HIP_X + 3 + d // 3, GROUND), ff=(HIP_X - 3, GROUND), head_dy=hd) for d, sw_a, cp, hd in CROUCH]
FRAMES["attack"] = [
    pose(nh=(HIP_X + 5, HIP_Y - 6), sword=-30),
    pose(dx=-1, nh=(HIP_X - 1, HIP_Y - 13), fh=(HIP_X + 2, HIP_Y - 6), sword=-140, cape=0.4),
    pose(dx=-1, dy=1, nh=(HIP_X - 3, HIP_Y - 14), fh=(HIP_X + 3, HIP_Y - 6), sword=-170, cape=0.45),
    pose(dx=1, nh=(HIP_X + 4, HIP_Y - 13), fh=(HIP_X, HIP_Y - 5), sword=-70, cape=0.6, nf=(HIP_X + 4, GROUND),
         fx=[("arc", HIP_X + 1, HIP_Y - 11, 12, -165, -75)]),
    pose(dx=2, dy=1, nh=(HIP_X + 8, HIP_Y - 5), fh=(HIP_X - 4, HIP_Y - 5), sword=25, cape=0.8, nf=(HIP_X + 6, GROUND),
         fx=[("arc", HIP_X + 2, HIP_Y - 10, 13, -100, 35)]),
    pose(dx=2, dy=1, nh=(HIP_X + 7, HIP_Y - 1), fh=(HIP_X - 4, HIP_Y - 5), sword=70, cape=0.7, nf=(HIP_X + 6, GROUND)),
    pose(dx=1, nh=(HIP_X + 6, HIP_Y - 3), sword=30, cape=0.5, nf=(HIP_X + 4, GROUND)),
    pose(nh=(HIP_X + 5, HIP_Y - 5), sword=-10, cape=0.35),
]
B = dict(sword=None, bow=True)
FRAMES["shoot"] = [
    pose(nh=(HIP_X + 5, HIP_Y - 3), **B),
    pose(nh=(HIP_X + 8, HIP_Y - 7), fh=(HIP_X + 1, HIP_Y - 6), **B),
    pose(nh=(HIP_X + 9, HIP_Y - 8), fh=(HIP_X + 6, HIP_Y - 8), nock=True, **B),
    pose(nh=(HIP_X + 9, HIP_Y - 8), fh=(HIP_X + 4, HIP_Y - 8), nock=True, draw=1, **B),
    pose(nh=(HIP_X + 9, HIP_Y - 8), fh=(HIP_X + 1, HIP_Y - 8), nock=True, draw=4, dx=-1, **B),
    pose(nh=(HIP_X + 9, HIP_Y - 8), fh=(HIP_X - 1, HIP_Y - 9), draw=0, dx=-1, fx=[("arrow", HIP_X + 17, HIP_Y - 8)], **B),
    pose(nh=(HIP_X + 8, HIP_Y - 7), fh=(HIP_X - 1, HIP_Y - 7), fx=[("arrow", HIP_X + 26, HIP_Y - 8)], **B),
    pose(nh=(HIP_X + 6, HIP_Y - 5), fh=(HIP_X - 3, HIP_Y - 4), **B),
]
up = (HIP_X + 4, HIP_Y - 15)
FRAMES["cast"] = [
    pose(nh=(HIP_X + 5, HIP_Y - 6), sword=-60),
    pose(nh=up, sword=-90, fh=(HIP_X + 2, HIP_Y - 10), cape=0.4, fx=[("spark", [(HIP_X - 4, HIP_Y - 26), (HIP_X + 12, HIP_Y - 20)])]),
    pose(nh=up, sword=-90, fh=(HIP_X + 2, HIP_Y - 10), cape=0.5, fx=[("spark", [(HIP_X + 1, HIP_Y - 30), (HIP_X + 9, HIP_Y - 28), (HIP_X + 13, HIP_Y - 33)])]),
    pose(nh=up, sword=-90, fh=(HIP_X + 2, HIP_Y - 10), cape=0.6, fx=[("orb", HIP_X + 5, HIP_Y - 30, 1)]),
    pose(nh=up, sword=-90, fh=(HIP_X + 2, HIP_Y - 10), cape=0.7, dy=-1, fx=[("orb", HIP_X + 5, HIP_Y - 31, 3), ("spark", [(HIP_X - 1, HIP_Y - 34), (HIP_X + 11, HIP_Y - 26)])]),
    pose(dx=1, nh=(HIP_X + 8, HIP_Y - 8), sword=-15, fh=(HIP_X - 3, HIP_Y - 6), cape=0.9, nf=(HIP_X + 5, GROUND), fx=[("orb", HIP_X + 26, HIP_Y - 12, 3)]),
    pose(dx=1, nh=(HIP_X + 8, HIP_Y - 7), sword=-5, fh=(HIP_X - 3, HIP_Y - 6), cape=0.7, nf=(HIP_X + 5, GROUND), fx=[("orb", HIP_X + 33, HIP_Y - 11, 2), ("spark", [(HIP_X + 30, HIP_Y - 16), (HIP_X + 36, HIP_Y - 6)])]),
    pose(nh=(HIP_X + 5, HIP_Y - 4), sword=20, cape=0.4),
]

CLIPS = {
    "idle":   {"duration_ms": 220, "loop": True},
    "walk":   {"duration_ms": 100, "loop": True},
    "run":    {"duration_ms": 70, "loop": True},
    "jump":   {"duration_ms": [90, 90, 70, 70, 110, 80, 90, 110], "loop": False},
    "crouch": {"duration_ms": [70, 70, 70, 120, 160, 120, 80, 80], "loop": False},
    "attack": {"duration_ms": [70, 70, 110, 50, 90, 80, 80, 90], "loop": False},
    "shoot":  {"duration_ms": [80, 80, 80, 90, 150, 60, 80, 100], "loop": False},
    "cast":   {"duration_ms": [80, 90, 90, 90, 140, 70, 80, 100], "loop": False},
}
EVENTS = {"attack": [{"at": 4, "name": "hit"}], "shoot": [{"at": 5, "name": "custom:release"}], "cast": [{"at": 5, "name": "custom:release"}]}
LAYERS = ["cape", "far_arm", "far_leg", "near_leg", "torso", "head", "near_arm", "weapon", "fx"]


def crop(c):
    pts = [(x, y) for y in range(H) for x in range(W) if c.g[y][x] != "."]
    if not pts:
        return None
    x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
    y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
    return x0, y0, ["".join(c.g[y][x0:x1 + 1]) for y in range(y0, y1 + 1)]


def build():
    frames = []
    for clip, poses in FRAMES.items():
        for i, p in enumerate(poses):
            layers = draw_frame(p)
            fl = {}
            for name in LAYERS:
                cr = crop(layers[name])
                fl[name] = {"hidden": True} if cr is None else {"rows": cr[2], "dx": cr[0], "dy": cr[1]}
            frames.append({"name": f"{clip}_{i}", "layers": fl})
    spec = {
        "schema": "codeart2d.pixelspec.v1",
        "name": "caballero",
        "canvas": [W, H],
        "anchor_px": ANCHOR,
        "palette": PALETTE,
        "outline": {"mode": "solid", "color": "k"},
        # capas por defecto: una pieza de 1 px que cada fotograma sustituye (origen en 0,0: dx/dy son absolutos)
        "layers": [{"name": n, "z": z, "origin": [0, 0], "rows": ["."]} for z, n in enumerate(LAYERS)],
        "frames": frames,
        "clips": {k: {**v, "frames": [f"{k}_{i}" for i in range(len(FRAMES[k]))], **({"events": EVENTS[k]} if k in EVENTS else {})} for k, v in CLIPS.items()},
    }
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "caballero.pixelspec.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(spec, fh, ensure_ascii=False, indent=1)
    print(out, len(frames), "fotogramas")


if __name__ == "__main__":
    build()
