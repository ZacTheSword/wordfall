"""Draws the Rot & Thaw play-card sprites as SVG files in this folder.

Run:  python art/rot-card/make_sprites.py
Then: python art/rot-card/inline.py   (copies them into wordfall.html)

Original art: a frozen ritual courtyard (indigo stone, cyan rune light, ice crystals,
snow) with burning red rot breaking through it: rot blobs crowned with flame, red rot
pools, charred rubble, red roots, and a rot blob frozen in a thawing block of ice.
"""
import math, os, random

HERE = os.path.dirname(os.path.abspath(__file__))

# Palette
INK = '#15123a'
RINK = '#2a0f17'                         # outline around rot and flame
SNOW, SNOWSH, SNOWDK = '#f4f7ff', '#c6cdf6', '#949ee6'
ICE1, ICE2, ICE3, ICE4 = '#ecfcff', '#a9eaff', '#5ac9f4', '#2c86cf'
GLOW, GLOWHI = '#62f0ff', '#d4feff'
STONE1, STONE2, STONE3 = '#25236a', '#2f3088', '#3c3fa6'
R1, R2, R3, R4 = '#ff8c8c', '#e8505e', '#b8304a', '#7a1830'   # rot: highlight, body, shade, deep
RHOLE = '#3a0a16'
F1, F2, F3 = '#f8d35a', '#f2883a', '#d9503a'                  # flame: core, body, base
CHAR, CHARHI = '#3a2030', '#5a3040'


def svg(w, h, body, defs=''):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            + (f'<defs>{defs}</defs>' if defs else '') + body + '</svg>')


def pts(ps):
    return ' '.join(f'{x:.1f},{y:.1f}' for x, y in ps)


def save(name, text):
    with open(os.path.join(HERE, name), 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


BLUR = lambda i, s: f'<filter id="{i}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="{s}"/></filter>'


# ---------- shared pieces ----------
def crystal(x, y, ang, L, W, sw=2.6):
    """A faceted ice crystal growing from (x, y) at ang degrees."""
    a = math.radians(ang)
    d = (math.cos(a), math.sin(a))
    n = (-math.sin(a), math.cos(a))
    up = 1 if n[1] < 0 else -1
    P = lambda t, s: (x + d[0] * t + n[0] * s * up, y + d[1] * t + n[1] * s * up)
    sh, w = L * 0.74, W / 2
    bl, sl, tip, sr, br = P(0, w), P(sh, w), P(L, 0), P(sh, -w), P(0, -w)
    rb, rs = P(0, -w * 0.12), P(sh, -w * 0.12)
    o = f'<polygon points="{pts([bl, sl, rs, rb])}" fill="{ICE1}"/>'
    o += f'<polygon points="{pts([rb, rs, sr, br])}" fill="{ICE3}"/>'
    o += f'<polygon points="{pts([sl, tip, rs])}" fill="{ICE2}"/>'
    o += f'<polygon points="{pts([rs, tip, sr])}" fill="{ICE4}"/>'
    h1, h2 = P(L * 0.1, w * 0.55), P(sh * 0.9, w * 0.55)
    o += f'<line x1="{h1[0]:.1f}" y1="{h1[1]:.1f}" x2="{h2[0]:.1f}" y2="{h2[1]:.1f}" stroke="#fff" stroke-width="{max(1.2, W / 9):.1f}" stroke-linecap="round" opacity=".9"/>'
    o += f'<polyline points="{pts([rb, rs, tip])}" fill="none" stroke="{INK}" stroke-width="1" opacity=".35"/>'
    o += f'<polygon points="{pts([bl, sl, tip, sr, br])}" fill="none" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round"/>'
    glow = f'<polygon points="{pts([bl, sl, tip, sr, br])}"/>'
    return o, glow


def sparkle(x, y, r, col='#fff'):
    return (f'<path d="M{x} {y - r}Q{x + r * .18} {y - r * .18} {x + r} {y}Q{x + r * .18} {y + r * .18} {x} {y + r}'
            f'Q{x - r * .18} {y + r * .18} {x - r} {y}Q{x - r * .18} {y - r * .18} {x} {y - r}Z" fill="{col}"/>')


# Flame crown: three tongues on a 40 x 24 box, base along y = 24.
FLAME_OUT = 'M2 24C-.5 18 3 14 5.5 9.5C6.5 13.5 8.6 14.6 10 13.6C9.6 8.6 13.6 4.6 19 .6C18.8 5.8 21.6 9 23 12C24.8 9 27.4 7.4 30.6 5.6C30.2 10.8 33.6 13.6 34.8 17C36 15 37 13.4 38.4 12C40.6 17 40.4 21 38 24Z'
FLAME_IN = 'M8.4 24C7.4 20.4 9 18 10.4 16C11.2 18 12.8 19 14.2 18.2C14 14.2 16.8 11.2 19.8 8.6C20 12.4 22 14.6 23.2 17.4C25 15.4 26.8 14.4 28.8 13.4C28.8 17.4 31.4 19.6 31.6 24Z'
FLAME_CORE = 'M14 24C13.4 21.6 14.8 20 16 19C16.6 20.4 17.8 21 18.8 20.2C18.8 17.6 20.4 15.6 22 14.2C22.4 16.8 24 18.6 24.4 20.8C25.4 20 26.2 19.6 27 19.2C27.4 21.4 26.8 23 26.2 24Z'


def flame(cx, base_y, w, sw=2):
    """Flame crown centred on cx, sitting on base_y, w wide."""
    k = w / 40
    g = f'<g transform="translate({cx - w / 2:.1f} {base_y - 24 * k:.1f}) scale({k:.3f})" stroke-linejoin="round">'
    g += f'<path d="{FLAME_OUT}" fill="{F2}" stroke="{RINK}" stroke-width="{sw / k:.2f}"/>'
    g += f'<path d="{FLAME_IN}" fill="{F1}"/>'
    g += f'<path d="{FLAME_CORE}" fill="#fff6d6"/>'
    g += f'<path d="M5 20L7.5 17M33 19L35 16.4M12 22L14 19.6" stroke="{F3}" stroke-width="{1.2 / k * .5 + .6:.2f}" stroke-linecap="round"/>'
    g += '</g>'
    return g


_rid = [0]


def rotblob(cx, cy, r, face=True, fire=True, sw=2.4):
    """A blob of red rot with a flame crown and hollow eye sockets."""
    _rid[0] += 1
    cid = f'rb{_rid[0]}'
    w, h = r * 1.1, r
    d = (f'M{cx - w:.1f} {cy + h * .12:.1f}'
         f'C{cx - w:.1f} {cy - h * .78:.1f} {cx - w * .45:.1f} {cy - h:.1f} {cx:.1f} {cy - h:.1f}'
         f'C{cx + w * .5:.1f} {cy - h:.1f} {cx + w:.1f} {cy - h * .72:.1f} {cx + w:.1f} {cy + h * .08:.1f}'
         f'C{cx + w:.1f} {cy + h * .66:.1f} {cx + w * .62:.1f} {cy + h * .96:.1f} {cx + w * .28:.1f} {cy + h * .94:.1f}'
         f'C{cx + w * .2:.1f} {cy + h * 1.24:.1f} {cx - w * .06:.1f} {cy + h * 1.26:.1f} {cx - w * .1:.1f} {cy + h * .96:.1f}'
         f'C{cx - w * .58:.1f} {cy + h:.1f} {cx - w:.1f} {cy + h * .68:.1f} {cx - w:.1f} {cy + h * .12:.1f}Z')
    o = f'<clipPath id="{cid}"><path d="{d}"/></clipPath>'
    o += f'<path d="{d}" fill="{R2}"/>'
    o += f'<g clip-path="url(#{cid})">'
    o += f'<ellipse cx="{cx + w * .55:.1f}" cy="{cy + h * .62:.1f}" rx="{w * 1.05:.1f}" ry="{h * .78:.1f}" fill="{R3}"/>'
    o += f'<ellipse cx="{cx - w * .34:.1f}" cy="{cy - h * .52:.1f}" rx="{w * .42:.1f}" ry="{h * .3:.1f}" fill="{R1}"/>'
    o += f'<ellipse cx="{cx - w * .46:.1f}" cy="{cy - h * .6:.1f}" rx="{w * .12:.1f}" ry="{h * .08:.1f}" fill="#fff" opacity=".8"/>'
    hatch = ''.join(f'<path d="M{cx + w * (.35 + i * .14):.1f} {cy + h * (.28 + (i % 2) * .08):.1f}l{w * .16:.1f} {h * .22:.1f}"/>' for i in range(4))
    o += f'<g stroke="{R4}" stroke-width="{max(1, r / 14):.1f}" stroke-linecap="round" fill="none">{hatch}</g>'
    o += '</g>'
    if face:
        ey = cy + h * .02
        for ex, tilt in ((cx - w * .36, -8), (cx + w * .3, 8)):
            o += f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{w * .2:.1f}" ry="{h * .27:.1f}" transform="rotate({tilt} {ex:.1f} {ey:.1f})" fill="{RHOLE}" stroke="{RINK}" stroke-width="{sw * .6:.1f}"/>'
        o += f'<path d="M{cx - w * .36:.1f} {ey + h * .26:.1f}C{cx - w * .33:.1f} {ey + h * .42:.1f} {cx - w * .3:.1f} {ey + h * .5:.1f} {cx - w * .34:.1f} {ey + h * .54:.1f}C{cx - w * .4:.1f} {ey + h * .5:.1f} {cx - w * .4:.1f} {ey + h * .4:.1f} {cx - w * .36:.1f} {ey + h * .26:.1f}Z" fill="{RHOLE}"/>'
        o += f'<path d="M{cx - w * .06:.1f} {ey + h * .36:.1f}L{cx + w * .06:.1f} {ey + h * .36:.1f}L{cx:.1f} {ey + h * .46:.1f}Z" fill="{RHOLE}"/>'
    o += f'<path d="{d}" fill="none" stroke="{RINK}" stroke-width="{sw}" stroke-linejoin="round"/>'
    if fire:
        o = flame(cx + w * .05, cy - h * .62, w * 1.7, sw * .85) + o
    return o


def rotpool(cx, cy, rx, ry, flames=()):
    """A spreading pool of red rot, with small flames licking up from it."""
    d = (f'M{cx - rx} {cy}C{cx - rx} {cy - ry} {cx - rx * .4} {cy - ry * 1.3} {cx} {cy - ry}'
         f'C{cx + rx * .5} {cy - ry * 1.4} {cx + rx} {cy - ry * .6} {cx + rx} {cy}'
         f'C{cx + rx * .6} {cy + ry} {cx - rx * .5} {cy + ry * 1.1} {cx - rx} {cy}Z')
    o = ''.join(flame(fx, cy - ry * .75, fw, 1.6) for fx, fw in flames)
    o += f'<path d="{d}" fill="{R3}" stroke="{RINK}" stroke-width="2" stroke-linejoin="round"/>'
    o += f'<ellipse cx="{cx - rx * .25}" cy="{cy - ry * .3}" rx="{rx * .45}" ry="{ry * .4}" fill="{R2}"/>'
    o += f'<ellipse cx="{cx - rx * .4}" cy="{cy - ry * .45}" rx="{rx * .12}" ry="{ry * .14}" fill="{R1}"/>'
    o += f'<circle cx="{cx + rx * .45}" cy="{cy + 1}" r="1.6" fill="{R4}"/><circle cx="{cx + rx * .1}" cy="{cy + ry * .35}" r="1.2" fill="{R4}"/>'
    return o


def snowcap(x, y, w, h=7, sw=1.8):
    n = max(2, int(w // 9))
    seg = w / n
    d = f'M{x - 1.5} {y + 1.5}'
    d += f'C{x - 2} {y - h * .6} {x + seg * .3} {y - h} {x + seg * .5} {y - h}'
    for i in range(1, n):
        cx = x + seg * (i + .5)
        hh = h * (0.75 + 0.25 * ((i * 37) % 5) / 4)
        d += f'S{cx - seg * .25} {y - hh} {cx} {y - hh}'
    d += f'C{x + w + 1} {y - h * .7} {x + w + 2.5} {y - 1} {x + w + 1.5} {y + 1.5}'
    d += f'C{x + w * .7} {y + 3.2} {x + w * .55} {y + .6} {x + w * .4} {y + 2.4}C{x + w * .25} {y + 3.6} {x + w * .1} {y + 1} {x - 1.5} {y + 1.5}Z'
    return f'<path d="{d}" fill="{SNOW}" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round"/>'


def drip(x, y, s=1, col=ICE2):
    return (f'<path d="M{x} {y}C{x + 2.4 * s} {y + 3.6 * s} {x + 3 * s} {y + 5.6 * s} {x} {y + 6.4 * s}C{x - 3 * s} {y + 5.6 * s} {x - 2.4 * s} {y + 3.6 * s} {x} {y}Z" '
            f'fill="{col}" stroke="{INK}" stroke-width="1.2"/>')


def embers(xy):
    return ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/>' for x, y, r, c in xy)


def charred(cx, cy, s):
    return (f'<path d="M{cx - 9 * s} {cy + 6 * s}L{cx - 8 * s} {cy - 4 * s}L{cx - 2 * s} {cy - 8 * s}L{cx + 7 * s} {cy - 5 * s}L{cx + 9 * s} {cy + 4 * s}Z" '
            f'fill="{CHAR}" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>'
            f'<path d="M{cx - 4 * s} {cy - 4 * s}L{cx - 1 * s} {cy}L{cx + 3 * s} {cy - 2 * s}" fill="none" stroke="{F2}" stroke-width="{1.3 * s:.1f}" stroke-linecap="round"/>'
            f'<circle cx="{cx + 4 * s}" cy="{cy + 2 * s}" r="{1.5 * s}" fill="{CHARHI}"/>')


SNOWGRAD = f'<linearGradient id="sg" x1="0" y1="0" x2="0" y2="1"><stop offset=".3" stop-color="{SNOW}"/><stop offset="1" stop-color="{SNOWSH}"/></linearGradient>'


# ---------- 1. Corner crystals (top-left; mirrored for top-right) ----------
def make_crystals():
    specs = [(40, 38, -9, 112, 21), (37, 40, 97, 104, 19), (36, 34, 222, 44, 21), (40, 34, 252, 30, 15),
             (34, 40, 192, 32, 15), (46, 42, 7, 62, 14), (42, 46, 86, 54, 12), (50, 36, -24, 40, 12)]
    body, glows = '', ''
    for s in specs:
        o, g = crystal(*s)
        body += o
        glows += g
    clump = (f'<path d="M14 26C14 14 26 10 34 14C40 8 54 10 56 20C64 20 68 30 62 36C66 44 58 54 50 52'
             f'C48 60 36 62 32 56C24 60 14 54 16 46C8 42 8 30 14 26Z" fill="{SNOW}" stroke="{INK}" stroke-width="2.6" stroke-linejoin="round"/>')
    clump += f'<path d="M20 48C26 52 32 50 34 54C40 58 46 52 50 50C48 56 40 60 33 56C26 59 18 55 20 48Z" fill="{SNOWSH}"/>'
    clump += f'<path d="M38 47C43 43 51 45 54 50C52 53 48 52 46 55C43 52 39 52 38 47Z" fill="{R3}" stroke="{RINK}" stroke-width="1.5"/>'
    clump += f'<path d="M47 53C48.4 57 48 60 46.6 62.6C45.4 60 45.6 56 47 53Z" fill="{R2}" stroke="{RINK}" stroke-width="1.2"/>'
    clump += f'<ellipse cx="43" cy="47.5" rx="2.4" ry="1.4" fill="{R1}"/>'
    clump += f'<g fill="{SNOWSH}"><circle cx="30" cy="20" r="1.6"/><circle cx="46" cy="18" r="1.3"/><circle cx="56" cy="30" r="1.2"/></g>'
    sparks = sparkle(150, 24, 5) + sparkle(14, 120, 4) + sparkle(8, 6, 3.5, GLOWHI) + sparkle(96, 52, 3, GLOWHI)
    out = svg(160, 150, f'<g fill="{GLOW}" opacity=".55" filter="url(#b)">{glows}</g>' + body + clump + sparks, BLUR('b', 5))
    save('crystals.svg', out)


# ---------- 2. Snow cornice with icicles (repeats along the top) ----------
def make_cornice():
    W, H = 180, 44
    wave = [(180, 13), (166, 17), (152, 13), (138, 18), (122, 14), (106, 19), (90, 14), (74, 18), (58, 13), (42, 18), (26, 14), (12, 18), (0, 13)]
    d = 'M-2 -2H182V13'
    for (x0, y0), (x1, y1) in zip(wave, wave[1:]):
        d += f'Q{(x0 + x1) / 2:.1f} {max(y0, y1) + 4:.1f} {x1} {y1}'
    d += 'L-2 13Z'
    ics = [(8, 15, 13, 7), (28, 16, 24, 9), (47, 14, 11, 6), (68, 16, 30, 10), (91, 15, 15, 7), (113, 17, 21, 8), (134, 16, 12, 6), (154, 16, 27, 9), (172, 15, 14, 6)]
    icicles = ''
    for x, y, L, w in ics:
        p = [(x - w / 2, y - 3), (x + w / 2, y - 3), (x + .6, y + L)]
        icicles += f'<polygon points="{pts(p)}" fill="url(#ig)" stroke="{INK}" stroke-width="1.8" stroke-linejoin="round"/>'
        icicles += f'<line x1="{x - w * .18:.1f}" y1="{y}" x2="{x - w * .05 + .3:.1f}" y2="{y + L * .62:.1f}" stroke="#fff" stroke-width="1.2" stroke-linecap="round"/>'
    defs = (f'<linearGradient id="ig" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{ICE1}"/>'
            f'<stop offset=".6" stop-color="{ICE2}"/><stop offset="1" stop-color="{ICE3}"/></linearGradient>')
    body = icicles + f'<path d="{d}" fill="{SNOW}" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>'
    body += f'<g fill="{SNOWSH}"><circle cx="20" cy="7" r="1.5"/><circle cx="64" cy="5" r="1.2"/><circle cx="118" cy="8" r="1.4"/><circle cx="160" cy="6" r="1.1"/></g>'
    save('cornice.svg', svg(W, H, body, defs))


# ---------- 3. Ground: snow drifts with burning rot breaking through (repeats) ----------
def make_ground():
    W, H = 400, 72
    yf = lambda x: 24 + 5 * math.sin(2 * math.pi * x / W * 2) + 3.5 * math.sin(2 * math.pi * x / W * 5 + 1)
    xs = list(range(0, W + 1, 8))
    line = f'M-2 {yf(0):.1f}' + ''.join(f'L{x} {yf(x):.1f}' for x in xs) + f'L{W + 2} {yf(W):.1f}'
    body = f'<path d="{line}V{H + 2}H-2Z" fill="url(#sg)"/>'
    body += f'<path d="{line}" fill="none" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round"/>'
    body += rotpool(70, yf(70) + 13, 32, 8, flames=((60, 16), (80, 12)))
    body += f'<path d="M37 {yf(70) + 15}C52 {yf(70) + 24} 88 {yf(70) + 24} 105 {yf(70) + 15}" fill="none" stroke="{SNOWSH}" stroke-width="2.4"/>'
    body += rotpool(262, yf(262) + 13, 22, 6, flames=((266, 11),))
    for cx, s in ((178, 1), (192, .75), (166, .6)):
        body += charred(cx, yf(cx) + 6, s)
    body += snowcap(170, yf(178) + 2, 20, 5, 1.6)
    cx = 336; y = yf(cx) + 16
    body += f'<ellipse cx="{cx}" cy="{y}" rx="26" ry="6.5" fill="{ICE3}" stroke="{INK}" stroke-width="2"/>'
    body += f'<ellipse cx="{cx - 2}" cy="{y - 1}" rx="18" ry="3.6" fill="{ICE2}"/>'
    body += f'<path d="M{cx - 14} {y - 1.6}Q{cx - 6} {y - 3.4} {cx + 2} {y - 2.2}" stroke="#fff" stroke-width="1.6" fill="none" stroke-linecap="round"/>'
    body += f'<ellipse cx="{cx + 10}" cy="{y + 1}" rx="5" ry="1.4" fill="none" stroke="#fff" stroke-width="1" opacity=".7"/>'
    for args in ((132, yf(132) + 8, -78, 26, 9), (140, yf(140) + 8, -100, 16, 7), (366, yf(366) + 6, -96, 20, 8)):
        o, _ = crystal(*args, sw=2)
        body += o
    body += snowcap(124, yf(132) + 8, 22, 4, 1.6)
    body += f'<g fill="#fff" opacity=".8"><circle cx="30" cy="{yf(30) + 8:.1f}" r="1.3"/><circle cx="222" cy="{yf(222) + 6:.1f}" r="1.1"/><circle cx="300" cy="{yf(300) + 9:.1f}" r="1.2"/></g>'
    body += embers(((58, yf(58) - 10, 1.3, F1), (74, yf(74) - 16, 1, F2), (264, yf(264) - 8, 1, F1)))
    body += sparkle(214, yf(214) - 4, 3, GLOWHI)
    defs = f'<linearGradient id="sg" x1="0" y1="0" x2="0" y2="1"><stop offset=".25" stop-color="{SNOW}"/><stop offset=".7" stop-color="{SNOWSH}"/><stop offset="1" stop-color="{SNOWDK}"/></linearGradient>'
    save('ground.svg', svg(W, H, body, defs))


# ---------- 4. Burning rot breaking out of the snow (bottom-left) ----------
def make_rotpile():
    W, H = 170, 120
    body = f'<path d="M-4 124V98C18 86 52 92 76 98C104 104 128 96 146 104C158 110 164 116 172 124Z" fill="url(#sg)" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round"/>'
    body += rotpool(64, 106, 54, 9)
    body += rotblob(56, 76, 26)
    body += rotblob(108, 96, 14)
    body += rotblob(22, 102, 9, face=False)
    body += charred(136, 108, .8)
    body += snowcap(-2, 102, 16, 6)
    body += snowcap(124, 110, 30, 5)
    body += f'<g fill="none" stroke="#e9f3ff" stroke-width="2" stroke-linecap="round" opacity=".5"><path d="M90 70C86 64 92 60 88 54"/><path d="M128 76C125 72 130 69 127 64"/></g>'
    body += embers(((40, 20, 1.6, F1), (70, 12, 1.2, F2), (84, 28, 1.1, F1), (118, 56, 1, F2), (30, 40, 1, F2)))
    save('rotpile.svg', svg(W, H, body, SNOWGRAD))


# ---------- 5. Rot frozen in a thawing block of ice (bottom-right) ----------
def make_frozen():
    W, H = 170, 120
    body = ''
    for args in ((152, 100, -84, 66, 18), (164, 102, -64, 44, 13)):
        o, _ = crystal(*args)
        body += o
    body += f'<path d="M-2 124C6 116 14 106 28 102C46 97 60 100 76 98C104 96 140 90 174 96V124Z" fill="url(#sg)" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round"/>'
    body += f'<ellipse cx="58" cy="109" rx="34" ry="7" fill="{ICE3}" stroke="{INK}" stroke-width="2"/>'
    body += f'<ellipse cx="55" cy="108" rx="24" ry="4" fill="{ICE2}"/>'
    body += f'<path d="M40 107Q50 104.6 60 106" stroke="#fff" stroke-width="1.6" fill="none" stroke-linecap="round"/>'
    body += rotblob(100, 72, 20, fire=False)
    body += flame(101, 55, 18, 1.6)
    front = [(66, 44), (130, 40), (134, 104), (70, 106)]
    top = [(66, 44), (82, 30), (144, 28), (130, 40)]
    side = [(130, 40), (144, 28), (148, 90), (134, 104)]
    body += f'<polygon points="{pts(front)}" fill="{ICE2}" opacity=".5"/>'
    body += f'<polygon points="{pts(top)}" fill="{ICE1}" opacity=".85"/>'
    body += f'<polygon points="{pts(side)}" fill="{ICE3}" opacity=".7"/>'
    body += f'<g fill="none" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round"><polygon points="{pts(front)}"/><polygon points="{pts(top)}"/><polygon points="{pts(side)}"/></g>'
    body += f'<path d="M72 52L78 92M76 50L120 47" stroke="#fff" stroke-width="2" stroke-linecap="round" opacity=".85"/>'
    body += f'<path d="M134 58L120 66L124 74L112 82M120 66L128 72" fill="none" stroke="#fff" stroke-width="1.4"/>'
    body += f'<path d="M134 59L121 67L125 75L113 83" fill="none" stroke="{ICE4}" stroke-width=".8"/>'
    body += drip(76, 105, 1) + drip(98, 107, .8) + drip(124, 105, 1.1)
    body += snowcap(84, 30, 52, 5, 1.8)
    body += f'<g fill="none" stroke="#e9f3ff" stroke-width="2" stroke-linecap="round" opacity=".55"><path d="M96 26C92 22 98 18 94 12"/><path d="M108 24C105 20 110 17 107 12"/></g>'
    body += sparkle(158, 24, 4) + sparkle(56, 58, 2.6, GLOWHI)
    save('frozen.svg', svg(W, H, body, SNOWGRAD))


# ---------- 6. Frost lantern on a post ----------
def make_lantern():
    W, H = 44, 104
    body = '<circle cx="22" cy="40" r="22" fill="url(#halo)"/>'
    body += f'<g stroke="{INK}" stroke-width="2" stroke-linejoin="round">'
    body += f'<rect x="18.5" y="56" width="7" height="42" rx="1.5" fill="{STONE2}"/>'
    body += f'<path d="M12 104V98C12 95 32 95 32 98V104Z" fill="{STONE3}"/>'
    body += f'<path d="M13 30H31L29 52H15Z" fill="url(#lamp)"/>'
    body += f'<rect x="12" y="51" width="20" height="5" rx="1.5" fill="{STONE2}"/>'
    body += f'<path d="M7 31L22 17L37 31Z" fill="{STONE3}"/>'
    body += f'<path d="M22 17L20 11L22 5L24 11Z" fill="{ICE2}"/>'
    body += '</g>'
    body += f'<g stroke="{INK}" stroke-width="1.4"><line x1="18.5" y1="30" x2="19.4" y2="52"/><line x1="25.5" y1="30" x2="24.6" y2="52"/></g>'
    body += f'<path d="M22 46C19 46 18.4 43 20 40.6C20.6 42 21.6 42 22 41C21.6 39 22.6 37 24 35.6C24.4 38 26 39 26 41.6C26 44 24.4 46 22 46Z" fill="#fff"/>'
    body += f'<rect x="20" y="60" width="2" height="34" fill="{STONE3}" opacity=".9"/>'
    body += snowcap(8, 30.5, 28, 5, 1.6)
    body += f'<polygon points="15,56 18,56 16.3,63" fill="{ICE2}" stroke="{INK}" stroke-width="1.2"/><polygon points="27,56 30,56 28.6,61" fill="{ICE2}" stroke="{INK}" stroke-width="1.2"/>'
    body += snowcap(12, 98, 20, 4, 1.6)
    defs = (f'<radialGradient id="halo"><stop offset="0" stop-color="{GLOW}" stop-opacity=".55"/><stop offset="1" stop-color="{GLOW}" stop-opacity="0"/></radialGradient>'
            f'<linearGradient id="lamp" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{GLOWHI}"/><stop offset="1" stop-color="{GLOW}"/></linearGradient>')
    save('lantern.svg', svg(W, H, body, defs))


# ---------- 7. Frost wisp ----------
def make_wisp():
    W, H = 40, 52
    shape = 'M20 4C26 14 34 20 32 33C31 43 25 48 20 48C13 48 8 43 8 35C8 27 14 25 13 16C17 20 18 13 20 4Z'
    body = f'<path d="{shape}" fill="{GLOW}" opacity=".65" filter="url(#b)"/>'
    body += f'<path d="{shape}" fill="url(#wg)" stroke="#2c86cf" stroke-width="1.6"/>'
    body += '<path d="M20 20C23 26 27 30 26 36C25.4 41 23 43 20 43C16 43 14 40 14 36C14 31 18 30 17 25C19 27 19.6 24 20 20Z" fill="#fff" opacity=".85"/>'
    body += f'<ellipse cx="16.6" cy="35" rx="1.7" ry="2.6" fill="{INK}"/><ellipse cx="23.4" cy="35" rx="1.7" ry="2.6" fill="{INK}"/>'
    body += '<circle cx="17.1" cy="34" r=".6" fill="#fff"/><circle cx="23.9" cy="34" r=".6" fill="#fff"/>'
    defs = BLUR('b', 3.5) + f'<linearGradient id="wg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{GLOW}"/><stop offset="1" stop-color="{GLOWHI}"/></linearGradient>'
    save('wisp.svg', svg(W, H, body, defs))


# ---------- 8. Frost lightning ----------
def make_bolt():
    W, H = 200, 120
    main = 'M0 8L26 14L38 6L62 22L80 16L102 34L124 30L146 48L170 46L196 62'
    paths = [main, 'M62 22L66 40L82 48L86 64', 'M124 30L132 14L150 10', 'M102 34L98 52L110 60']
    body = ''.join(f'<path d="{p}" stroke="{GLOW}" stroke-width="7" opacity=".55" filter="url(#b)"/>' for p in paths)
    body += ''.join(f'<path d="{p}" stroke="{GLOW}" stroke-width="{2.6 if p == main else 1.8}"/>' for p in paths)
    body += ''.join(f'<path d="{p}" stroke="#fff" stroke-width="{1.1 if p == main else .8}"/>' for p in paths)
    save('bolt.svg', svg(W, H, f'<g fill="none" stroke-linejoin="round" stroke-linecap="round">{body}</g>', BLUR('b', 3)))


# ---------- 9. Rune ring under the Play button ----------
def make_ring():
    W, H = 640, 140
    cx, cy, rx, ry = 320, 70, 300, 56
    glyphs = ['M0 14V0M0 4L6 0M0 8L6 4', 'M0 14L5 0L10 14M2.4 8.6H7.6', 'M5 0V14M0 4H10M0 10H10', 'M0 0L10 14M10 0L0 14',
              'M0 14V0L8 5L0 9', 'M5 0L10 7L5 14L0 7Z', 'M0 0H10L0 14H10', 'M0 7H10M5 0V14M1 2L9 12']
    runes = ''
    N = 22
    for i in range(N):
        t = 2 * math.pi * i / N + .12
        x = cx + (rx - 22) * math.cos(t)
        y = cy + (ry - 6.5) * math.sin(t)
        runes += f'<path transform="translate({x - 5:.1f} {y - 7 * (0.5 + 0.5 * (ry / rx)):.1f}) scale(1 {0.55 + 0.25 * (1 + math.sin(t)) / 2:.2f})" d="{glyphs[i % len(glyphs)]}"/>'
    ring = f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}"/><ellipse cx="{cx}" cy="{cy}" rx="{rx - 44}" ry="{ry - 13}"/>'
    body = f'<g fill="none" stroke="{GLOW}" stroke-width="12" opacity=".4" filter="url(#b)">{ring}</g>'
    body += f'<g fill="none" stroke="{GLOW}" stroke-width="3">{ring}</g>'
    body += f'<ellipse cx="{cx}" cy="{cy}" rx="{rx - 10}" ry="{ry - 3}" fill="none" stroke="{GLOWHI}" stroke-width="1" stroke-dasharray="2 10" opacity=".8"/>'
    body += f'<g fill="none" stroke="{GLOWHI}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" opacity=".95">{runes}</g>'
    body += f'<ellipse cx="{cx}" cy="{cy}" rx="{rx - 50}" ry="{ry - 16}" fill="{GLOW}" opacity=".07"/>'
    save('ring.svg', svg(W, H, body, BLUR('b', 6)))


# ---------- 10. Red rot roots creeping up the side walls ----------
def make_roots():
    W, H = 26, 220
    main = 'M14 220C6 200 20 186 12 168C5 152 18 138 12 120C7 104 17 92 13 76C10 62 16 52 13 40'
    br = ['M12 168C18 162 22 164 24 156', 'M12 120C6 114 3 116 2 108', 'M13 76C18 72 21 74 22 66']
    body = f'<path d="{main}" fill="none" stroke="{RINK}" stroke-width="6.4" stroke-linecap="round"/>'
    body += ''.join(f'<path d="{b}" fill="none" stroke="{RINK}" stroke-width="4.4" stroke-linecap="round"/>' for b in br)
    body += f'<path d="{main}" fill="none" stroke="{R3}" stroke-width="3.4" stroke-linecap="round"/>'
    body += ''.join(f'<path d="{b}" fill="none" stroke="{R3}" stroke-width="2" stroke-linecap="round"/>' for b in br)
    body += f'<path d="{main}" fill="none" stroke="{R1}" stroke-width="1" stroke-linecap="round" stroke-dasharray="6 14" opacity=".8"/>'
    body += f'<g stroke="{RINK}" stroke-width="1.2"><circle cx="24" cy="155" r="2.8" fill="{R2}"/><circle cx="2" cy="107" r="2.4" fill="{R2}"/><circle cx="22" cy="65" r="2.2" fill="{R2}"/></g>'
    body += embers(((24, 150, .9, F1), (3, 102, .8, F1), (22, 60, .8, F2)))
    body += f'<g fill="{SNOW}" stroke="{INK}" stroke-width="1"><path d="M8 170C9 166 15 166 16 169Z"/><path d="M9 122C10 118 15 118 16 121Z"/></g>'
    save('roots.svg', svg(W, H, body))


# ---------- 11. Snow cap for the Play button (repeats) ----------
def make_btncap():
    W, H = 60, 16
    d = 'M-2 16V9C4 2 10 3 14 7C18 1 28 1 31 7C35 3 44 1 48 7C52 4 58 4 62 9V16Z'
    body = f'<path d="{d}" fill="{SNOW}"/><path d="M-2 9C4 2 10 3 14 7C18 1 28 1 31 7C35 3 44 1 48 7C52 4 58 4 62 9" fill="none" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>'
    body += f'<path d="M-2 14C8 12 18 15 30 13C42 11 52 14 62 12V16H-2Z" fill="{SNOWSH}"/>'
    save('btncap.svg', svg(W, H, body))


# ---------- 12. Emblem hanging at the top: an ice hexagon holding a burning rot core ----------
def make_medal():
    W, H = 72, 84
    cx, cy, R = 36, 38, 30
    hexp = [(cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))) for a in range(-90, 270, 60)]
    inner = [(cx + (R - 7) * math.cos(math.radians(a)), cy + (R - 7) * math.sin(math.radians(a))) for a in range(-90, 270, 60)]
    body = f'<polygon points="{pts(hexp)}" fill="{GLOW}" opacity=".5" filter="url(#b)"/>'
    for i in range(6):
        a, b2, c, d = hexp[i], hexp[(i + 1) % 6], inner[(i + 1) % 6], inner[i]
        body += f'<polygon points="{pts([a, b2, c, d])}" fill="{(ICE1, ICE2, ICE3, ICE4, ICE3, ICE2)[i]}"/>'
    body += f'<polygon points="{pts(inner)}" fill="#1a1748"/>'
    body += f'<circle cx="{cx}" cy="{cy + 3}" r="15" fill="url(#heat)"/>'
    body += rotblob(cx, cy + 6, 10.5, sw=1.8)
    body += f'<g fill="none" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round"><polygon points="{pts(hexp)}"/><polygon points="{pts(inner)}"/></g>'
    body += f'<g stroke="{INK}" stroke-width="1.2" opacity=".5">' + ''.join(f'<line x1="{hexp[i][0]:.1f}" y1="{hexp[i][1]:.1f}" x2="{inner[i][0]:.1f}" y2="{inner[i][1]:.1f}"/>' for i in range(6)) + '</g>'
    for x, L in ((22, 10), (30, 15), (42, 12), (50, 8)):
        body += f'<polygon points="{x - 3},{cy + R * .5 + 1} {x + 3},{cy + R * .5 + 1} {x + .4},{cy + R * .5 + 1 + L}" fill="{ICE2}" stroke="{INK}" stroke-width="1.4" stroke-linejoin="round"/>'
    body += snowcap(18, 12, 36, 6, 1.8)
    body += sparkle(62, 14, 3.4) + sparkle(9, 52, 2.6, GLOWHI)
    defs = BLUR('b', 4) + f'<radialGradient id="heat"><stop offset="0" stop-color="{F2}" stop-opacity=".55"/><stop offset="1" stop-color="{F2}" stop-opacity="0"/></radialGradient>'
    save('medal.svg', svg(W, H, body, defs))


# ---------- 13. Scene behind everything ----------
def make_bg():
    body = '<rect width="800" height="520" fill="url(#sky)"/>'
    body += '<ellipse cx="400" cy="-20" rx="360" ry="200" fill="url(#top)"/>'
    cliff = 'M0 250L0 120L30 150L52 96L80 140L104 110L128 170L150 150L170 200L200 190L230 236L260 228L290 260V300H0Z'
    body += f'<path d="{cliff}" fill="{STONE1}" opacity=".9"/>'
    body += f'<path d="{cliff}" transform="translate(800 0) scale(-1 1)" fill="{STONE1}" opacity=".9"/>'
    body += f'<path d="M52 96L60 130L80 140M104 110L112 150M748 96L740 130L720 140" fill="none" stroke="#3a3c9a" stroke-width="3"/>'
    body += '<rect x="356" y="-20" width="88" height="360" fill="url(#beam)" filter="url(#b8)"/>'
    body += '<rect x="390" y="-20" width="20" height="300" fill="url(#beam)" opacity=".8" filter="url(#b3)"/>'
    for rx, ry, col in ((720, 360, '#2a2a7a'), (560, 280, '#2f3088'), (420, 210, '#2b2c80'), (290, 150, '#31338e')):
        body += f'<ellipse cx="400" cy="640" rx="{rx}" ry="{ry}" fill="{col}"/>'
    joints = ''.join(f'<line x1="400" y1="640" x2="{400 + 760 * math.cos(math.radians(90 + k * 9.5)):.0f}" y2="{640 - 380 * math.sin(math.radians(90 + k * 9.5)):.0f}"/>' for k in range(-9, 10))
    body += f'<g stroke="#23226a" stroke-width="2.4" opacity=".75">{joints}</g>'
    for rx, ry in ((720, 360), (560, 280), (420, 210), (290, 150)):
        body += f'<ellipse cx="400" cy="640" rx="{rx}" ry="{ry}" fill="none" stroke="#1d1c58" stroke-width="3"/>'
    rnd = random.Random(11)
    stains = ''.join(f'<ellipse cx="{x}" cy="{y}" rx="{rnd.uniform(14, 34):.0f}" ry="{rnd.uniform(4, 9):.0f}"/>' for x, y in ((60, 470), (130, 500), (690, 480), (750, 445), (620, 505)))
    body += f'<g fill="{R4}" opacity=".45">{stains}</g>'
    flakes = ''.join(f'<ellipse cx="{rnd.uniform(0, 800):.0f}" cy="{rnd.uniform(300, 520):.0f}" rx="{rnd.uniform(3, 9):.1f}" ry="{rnd.uniform(1.4, 3):.1f}"/>' for _ in range(40))
    body += f'<g fill="{SNOW}" opacity=".22">{flakes}</g>'
    body += '<rect width="800" height="520" fill="url(#vig)"/>'
    defs = (f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#16133d"/><stop offset=".5" stop-color="#1f1c55"/><stop offset="1" stop-color="#2a2a74"/></linearGradient>'
            f'<radialGradient id="top"><stop offset="0" stop-color="{GLOW}" stop-opacity=".2"/><stop offset="1" stop-color="{GLOW}" stop-opacity="0"/></radialGradient>'
            f'<linearGradient id="beam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{GLOWHI}" stop-opacity=".45"/><stop offset=".55" stop-color="{GLOW}" stop-opacity=".14"/><stop offset="1" stop-color="{GLOW}" stop-opacity="0"/></linearGradient>'
            f'<radialGradient id="vig" cx=".5" cy=".45" r=".75"><stop offset=".55" stop-color="#0b0a24" stop-opacity="0"/><stop offset="1" stop-color="#0b0a24" stop-opacity=".7"/></radialGradient>'
            + BLUR('b8', 10) + BLUR('b3', 4))
    save('bg.svg', svg(800, 520, body, defs))


# ---------- 14. Flame crown for the in-game rot tile ----------
def make_tileflame():
    body = (f'<g stroke-linejoin="round"><path d="{FLAME_OUT}" fill="{F2}" stroke="{RINK}" stroke-width="2.2"/>'
            f'<path d="{FLAME_IN}" fill="{F1}"/><path d="{FLAME_CORE}" fill="#fff6d6"/></g>')
    save('tileflame.svg', f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-1.5 -1 43 26">{body}</svg>')


if __name__ == '__main__':
    for old in ('rot.svg', 'thaw.svg'):
        p = os.path.join(HERE, old)
        if os.path.exists(p):
            os.remove(p)
    for f in (make_crystals, make_cornice, make_ground, make_rotpile, make_frozen, make_lantern, make_wisp, make_bolt,
              make_ring, make_roots, make_btncap, make_medal, make_bg, make_tileflame):
        f()
    print('sprites written to', HERE)
