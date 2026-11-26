"""Draws the Rot & Thaw play-card sprites as SVG files in this folder.

Run:  python art/rot-card/make_sprites.py
Then: python art/rot-card/inline.py   (copies them into wordfall.html)

Original art: a frozen ritual courtyard (indigo stone, cyan rune light, ice crystals,
snow) with the game's own rot creeping through it: brown rotting letter tiles, rubble,
snowy mushrooms, meltwater and an Ignite ember thawing the ice.
"""
import math, os

HERE = os.path.dirname(os.path.abspath(__file__))

# Palette
INK = '#15123a'
SNOW, SNOWSH, SNOWDK = '#f4f7ff', '#c6cdf6', '#949ee6'
ICE1, ICE2, ICE3, ICE4 = '#ecfcff', '#a9eaff', '#5ac9f4', '#2c86cf'
GLOW, GLOWHI = '#62f0ff', '#d4feff'
STONE1, STONE2, STONE3 = '#25236a', '#2f3088', '#3c3fa6'
ROT1, ROT2, ROT3, ROTDK = '#a07e3c', '#7a5a2a', '#5e4420', '#3b2a12'
RUB, RUBHI = '#5a4630', '#7a6040'
CAP, CAP2 = '#8c2246', '#b5395f'
TILE, TILEEDGE = '#f2e9d6', '#c4b693'
E1, E2, E3 = '#fff3c4', '#ffbe5c', '#ff6a1f'


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
    up = 1 if n[1] < 0 else -1           # which side faces the sky
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


def mushroom(x, y, s=1, cap=CAP, snow=True):
    """Stem foot at (x, y)."""
    g = f'<g transform="translate({x} {y}) scale({s})" stroke="{INK}" stroke-width="2" stroke-linejoin="round">'
    g += f'<path d="M-3 0C-3.6-5-2.6-9-2-12H2C2.6-9 3.6-5 3 0Z" fill="{TILE}"/>'
    g += f'<path d="M-10-11C-10-20 10-20 10-11C4-9.5-4-9.5-10-11Z" fill="{cap}"/>'
    g += '</g>'
    g += f'<g transform="translate({x} {y}) scale({s})">'
    g += f'<circle cx="-4" cy="-14.5" r="1.6" fill="#f6d9c8"/><circle cx="3.5" cy="-15.5" r="1.3" fill="#f6d9c8"/><circle cx="0" cy="-12.2" r="1" fill="#f6d9c8"/>'
    if snow:
        g += f'<path d="M-6.5-16.5C-5-19.6 5-19.6 6.5-16.5C4-15.3 2-16.6 0-15.6C-2-16.6-4-15.3-6.5-16.5Z" fill="{SNOW}" stroke="{INK}" stroke-width="1.4"/>'
    g += '</g>'
    return g


LETTERS = {
    'R': 'M6 16V4H11.5A3.6 3.6 0 0 1 11.5 11.2H6M10.6 11.2L14.6 16',
    'O': 'M10 4A5.6 6 0 1 0 10.01 4Z',
    'T': 'M4.5 4.5H15.5M10 4.5V16',
    'H': 'M5.5 4V16M14.5 4V16M5.5 10H14.5',
    'A': 'M4.5 16L10 4L15.5 16M6.8 11.5H13.2',
    'W': 'M3.5 4.5L6.5 16L10 8L13.5 16L16.5 4.5',
}


def tile(x, y, s, ch, kind, rot=0, tid='t'):
    """A game letter tile. kind: 'rot' (some rot), 'rotbad' (badly rotted), 'ice', 'icecrack'."""
    k = s / 20
    r = 3.6
    ice = kind.startswith('ice')
    face = f'url(#{tid}g)' if ice else TILE
    edge = '#2f9fd6' if ice else TILEEDGE
    lc = '#073a5a' if ice else '#1b1930'
    defs = ''
    if ice:
        defs += (f'<linearGradient id="{tid}g" x1="0" y1="0" x2=".6" y2="1"><stop offset="0" stop-color="#fff"/>'
                 f'<stop offset=".42" stop-color="#b8ecff"/><stop offset="1" stop-color="#5cc8f5"/></linearGradient>')
    defs += f'<clipPath id="{tid}c"><rect width="20" height="20" rx="{r}"/></clipPath>'
    g = f'<g transform="translate({x} {y}) rotate({rot} {s / 2} {s / 2}) scale({k})">'
    g += f'<rect width="20" height="20" rx="{r}" fill="{edge}"/><rect width="20" height="16.6" rx="{r}" fill="{face}"/>'
    if kind == 'rot' or kind == 'rotbad':
        heavy = kind == 'rotbad'
        g += f'<g clip-path="url(#{tid}c)">'
        g += f'<path d="M-2 20V12C3 10 6 15 10 13C14 11 17 14 22 12V20Z" fill="{ROT2}" opacity="{.95 if heavy else .8}"/>'
        g += f'<ellipse cx="4.5" cy="6" rx="{4 if heavy else 2.6}" ry="{3 if heavy else 2}" fill="{ROT1}" opacity=".75"/>'
        if heavy:
            g += f'<path d="M-2 10C4 6 9 9 13 5C16 2 19 4 22 2V-2H-2Z" fill="{ROT3}" opacity=".55"/>'
        g += f'<circle cx="15" cy="15" r="1.6" fill="{ROTDK}"/><circle cx="6" cy="16.5" r="1.2" fill="{ROTDK}"/><circle cx="3.5" cy="5.5" r="1" fill="{ROTDK}"/>'
        g += '</g>'
    g += f'<path d="{LETTERS[ch]}" fill="none" stroke="{lc}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>'
    if ice:
        g += (f'<g stroke="#0a6fa8" stroke-width=".8" stroke-linecap="round" opacity=".85" transform="translate(16.4 3.6)">'
              f'<path d="M0-2.2V2.2M-1.9-1.1L1.9 1.1M-1.9 1.1L1.9-1.1"/></g>')
        g += f'<path d="M2.4 3.2Q2.4 2 3.6 1.8" stroke="#fff" stroke-width="1.1" fill="none" stroke-linecap="round"/>'
    if kind == 'icecrack':
        g += f'<path d="M20 5L14 8.5L15.5 11.5L10.5 14.5M14 8.5L11 6.6" fill="none" stroke="#fff" stroke-width="1.1"/>'
        g += f'<path d="M20 5.6L14.6 9L16 12L11 15" fill="none" stroke="{ICE4}" stroke-width=".6"/>'
    if kind == 'rotbad':
        g += f'<path d="M15 0L20 0L20 6C18.6 5 18.4 3.6 17 3.6C15.8 3.6 15.6 1.4 15 0Z" fill="{INK}" opacity=".9"/>'  # crumbled corner
        g += f'<path d="M3 20L6 14.5L9 16" fill="none" stroke="{INK}" stroke-width=".9"/>'
    g += f'<rect width="20" height="20" rx="{r}" fill="none" stroke="{INK}" stroke-width="{2.4 / k * 0.5 + 1.2:.2f}"/>'
    g += '</g>'
    return g, defs


def snowcap(x, y, w, h=7, sw=1.8):
    """A lumpy cap of snow sitting on a surface from x to x+w at height y."""
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


def flame(x, y, s=1):
    g = f'<g transform="translate({x} {y}) scale({s})" stroke-linejoin="round">'
    g += f'<path d="M0 0C-8 0-10-8-6-14C-5-10-3-9-2-10C-4-15-1-21 3-25C3-19 9-16 9-8C9-3 5 0 0 0Z" fill="{E3}" stroke="{INK}" stroke-width="2"/>'
    g += f'<path d="M0-2C-4-2-5.5-6-3.5-9C-2.6-7-1-6.6 0-7.6C-.6-11 1-14 3-16C3.4-12 6-10.6 6-6.6C6-3.4 3.4-2 0-2Z" fill="{E2}"/>'
    g += f'<path d="M.6-3.4C-1.4-3.4-2-5.4-.6-7C0-5.6 1.4-5.6 1.6-7.4C3-6.4 3.6-3.4 .6-3.4Z" fill="{E1}"/>'
    g += '</g>'
    return g


def drip(x, y, s=1):
    return (f'<path d="M{x} {y}C{x + 2.4 * s} {y + 3.6 * s} {x + 3 * s} {y + 5.6 * s} {x} {y + 6.4 * s}C{x - 3 * s} {y + 5.6 * s} {x - 2.4 * s} {y + 3.6 * s} {x} {y}Z" '
            f'fill="{ICE2}" stroke="{INK}" stroke-width="1.2"/>')


# ---------- 1. Corner crystals (top-left; mirrored for top-right) ----------
def make_crystals():
    # Card corner sits at (30, 22) in this sprite.
    specs = [  # base x, base y, angle, length, width
        (40, 38, -9, 112, 21),
        (37, 40, 97, 104, 19),
        (36, 34, 222, 44, 21),
        (40, 34, 252, 30, 15),
        (34, 40, 192, 32, 15),
        (46, 42, 7, 62, 14),
        (42, 46, 86, 54, 12),
        (50, 36, -24, 40, 12),
    ]
    body, glows = '', ''
    for s in specs:
        o, g = crystal(*s)
        body += o
        glows += g
    # Snow drift packed into the corner, with rot seeping through it and a frosted mushroom.
    clump = (f'<path d="M14 26C14 14 26 10 34 14C40 8 54 10 56 20C64 20 68 30 62 36C66 44 58 54 50 52'
             f'C48 60 36 62 32 56C24 60 14 54 16 46C8 42 8 30 14 26Z" fill="{SNOW}" stroke="{INK}" stroke-width="2.6" stroke-linejoin="round"/>')
    clump += f'<path d="M20 48C26 52 32 50 34 54C40 58 46 52 50 50C48 56 40 60 33 56C26 59 18 55 20 48Z" fill="{SNOWSH}"/>'
    clump += f'<path d="M40 46C44 44 50 46 52 50C50 52 47 51 45 53C43 51 40 50 40 46Z" fill="{ROT2}" stroke="{INK}" stroke-width="1.4"/>'
    clump += f'<path d="M47 52C48 56 47.5 59 46.4 61C45.4 59 45.6 55 47 52Z" fill="{ROT3}" stroke="{INK}" stroke-width="1.2"/>'
    clump += f'<circle cx="44" cy="48" r="1.1" fill="{ROTDK}"/><circle cx="49" cy="49.5" r=".9" fill="{ROTDK}"/>'
    clump += mushroom(24, 28, .62, CAP)
    clump += f'<g fill="{SNOWSH}"><circle cx="30" cy="20" r="1.6"/><circle cx="46" cy="18" r="1.3"/><circle cx="56" cy="30" r="1.2"/></g>'
    sparks = sparkle(150, 24, 5) + sparkle(14, 120, 4) + sparkle(8, 6, 3.5, GLOWHI) + sparkle(96, 52, 3, GLOWHI)
    defs = BLUR('b', 5)
    out = svg(160, 150, f'<g fill="{GLOW}" opacity=".55" filter="url(#b)">{glows}</g>' + body + clump + sparks, defs)
    save('crystals.svg', out)


# ---------- 2. Snow cornice with icicles (repeats along the top) ----------
def make_cornice():
    W, H = 180, 44
    top = 'M-2 -2H182V13'
    wave = [(180, 13), (166, 17), (152, 13), (138, 18), (122, 14), (106, 19), (90, 14), (74, 18), (58, 13), (42, 18), (26, 14), (12, 18), (0, 13)]
    d = top
    for (x0, y0), (x1, y1) in zip(wave, wave[1:]):
        mx = (x0 + x1) / 2
        d += f'Q{mx:.1f} {max(y0, y1) + 4:.1f} {x1} {y1}'
    d += 'L-2 13Z'
    shadow = 'M-2 9' + ''.join(f'Q{(x0 + x1) / 2:.1f} {max(y0, y1) + 1:.1f} {x1} {y1 - 3}' for (x0, y0), (x1, y1) in zip(wave[::-1], wave[::-1][1:])) + 'L182 10V13'
    for (x0, y0), (x1, y1) in zip(wave, wave[1:]):
        shadow += f'Q{(x0 + x1) / 2:.1f} {max(y0, y1) + 4:.1f} {x1} {y1}'
    shadow += 'L-2 13Z'
    ics = [(8, 15, 13, 7), (28, 16, 24, 9), (47, 14, 11, 6), (68, 16, 30, 10), (91, 15, 15, 7), (113, 17, 21, 8), (134, 16, 12, 6), (154, 16, 27, 9), (172, 15, 14, 6)]
    icicles = ''
    for x, y, L, w in ics:
        p = [(x - w / 2, y - 3), (x + w / 2, y - 3), (x + .6, y + L)]
        icicles += f'<polygon points="{pts(p)}" fill="url(#ig)" stroke="{INK}" stroke-width="1.8" stroke-linejoin="round"/>'
        icicles += f'<line x1="{x - w * .18:.1f}" y1="{y}" x2="{x - w * .05 + .3:.1f}" y2="{y + L * .62:.1f}" stroke="#fff" stroke-width="1.2" stroke-linecap="round"/>'
    icicles += drip(68.6, 50 - 2, .8) if False else ''
    defs = (f'<linearGradient id="ig" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{ICE1}"/>'
            f'<stop offset=".6" stop-color="{ICE2}"/><stop offset="1" stop-color="{ICE3}"/></linearGradient>')
    body = icicles + f'<path d="{d}" fill="{SNOW}" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>'
    body += f'<g fill="{SNOWSH}"><circle cx="20" cy="7" r="1.5"/><circle cx="64" cy="5" r="1.2"/><circle cx="118" cy="8" r="1.4"/><circle cx="160" cy="6" r="1.1"/></g>'
    save('cornice.svg', svg(W, H, body, defs))


# ---------- 3. Ground: snow drifts with rot breaking through (repeats along the bottom) ----------
def make_ground():
    W, H = 400, 72
    yf = lambda x: 24 + 5 * math.sin(2 * math.pi * x / W * 2) + 3.5 * math.sin(2 * math.pi * x / W * 5 + 1)
    xs = list(range(0, W + 1, 8))
    d = f'M-2 {yf(0):.1f}' + ''.join(f'L{x} {yf(x):.1f}' for x in xs) + f'L{W + 2} {yf(W):.1f}V{H + 2}H-2Z'
    body = f'<path d="{d}" fill="url(#sg)"/>'
    body += '<path d="' + f'M-2 {yf(0):.1f}' + ''.join(f'L{x} {yf(x):.1f}' for x in xs) + f'L{W + 2} {yf(W):.1f}" fill="none" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round"/>'
    # rot patch with mushrooms
    def patch(cx, rx, ry):
        y = yf(cx) + 13
        p = f'<path d="M{cx - rx} {y}C{cx - rx} {y - ry} {cx - rx * .4} {y - ry * 1.3} {cx} {y - ry}C{cx + rx * .5} {y - ry * 1.4} {cx + rx} {y - ry * .6} {cx + rx} {y}'
        p += f'C{cx + rx * .6} {y + ry} {cx - rx * .5} {y + ry * 1.1} {cx - rx} {y}Z" fill="{ROT3}" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>'
        p += f'<ellipse cx="{cx - rx * .3}" cy="{y - ry * .35}" rx="{rx * .35}" ry="{ry * .4}" fill="{ROT2}"/>'
        p += f'<circle cx="{cx + rx * .4}" cy="{y + 1}" r="1.6" fill="{ROTDK}"/><circle cx="{cx - rx * .6}" cy="{y + 2}" r="1.2" fill="{ROTDK}"/><circle cx="{cx + rx * .1}" cy="{y - ry * .5}" r="1" fill="{ROTDK}"/>'
        p += f'<path d="M{cx - rx - 3} {y + 1}C{cx - rx * .4} {y + ry + 4} {cx + rx * .5} {y + ry + 4} {cx + rx + 3} {y + 1}" fill="none" stroke="{SNOWSH}" stroke-width="2.4"/>'
        return p, y
    p, y = patch(70, 30, 8); body += p
    body += mushroom(60, y - 3, .78) + mushroom(76, y - 5, 1.0) + mushroom(88, y - 1, .55, CAP2)
    p, y = patch(262, 22, 6); body += p
    body += mushroom(268, y - 2, .7)
    # rubble half-buried in snow
    for cx, s in ((178, 1), (192, .75), (166, .6)):
        y = yf(cx) + 6
        body += (f'<path d="M{cx - 9 * s} {y + 6 * s}L{cx - 8 * s} {y - 4 * s}L{cx - 2 * s} {y - 8 * s}L{cx + 7 * s} {y - 5 * s}L{cx + 9 * s} {y + 4 * s}Z" '
                 f'fill="{RUB}" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>'
                 f'<circle cx="{cx - 3 * s}" cy="{y - 2 * s}" r="{2 * s}" fill="{RUBHI}"/><circle cx="{cx + 4 * s}" cy="{y + 1 * s}" r="{1.4 * s}" fill="#3e2f1e"/>')
    body += snowcap(170, yf(178) + 2, 20, 5, 1.6)
    # meltwater puddle
    cx = 336; y = yf(cx) + 16
    body += f'<ellipse cx="{cx}" cy="{y}" rx="26" ry="6.5" fill="{ICE3}" stroke="{INK}" stroke-width="2"/>'
    body += f'<ellipse cx="{cx - 2}" cy="{y - 1}" rx="18" ry="3.6" fill="{ICE2}"/>'
    body += f'<path d="M{cx - 14} {y - 1.6}Q{cx - 6} {y - 3.4} {cx + 2} {y - 2.2}" stroke="#fff" stroke-width="1.6" fill="none" stroke-linecap="round"/>'
    body += f'<ellipse cx="{cx + 10}" cy="{y + 1}" rx="5" ry="1.4" fill="none" stroke="#fff" stroke-width="1" opacity=".7"/>'
    # ice shards poking up
    for args in ((132, yf(132) + 8, -78, 26, 9), (140, yf(140) + 8, -100, 16, 7), (366, yf(366) + 6, -96, 20, 8)):
        o, _ = crystal(*args, sw=2)
        body += o
    body += snowcap(124, yf(132) + 8, 22, 4, 1.6)
    body += f'<g fill="#fff" opacity=".8"><circle cx="30" cy="{yf(30) + 8:.1f}" r="1.3"/><circle cx="222" cy="{yf(222) + 6:.1f}" r="1.1"/><circle cx="300" cy="{yf(300) + 9:.1f}" r="1.2"/></g>'
    body += sparkle(214, yf(214) - 4, 3, GLOWHI)
    defs = f'<linearGradient id="sg" x1="0" y1="0" x2="0" y2="1"><stop offset=".25" stop-color="{SNOW}"/><stop offset=".7" stop-color="{SNOWSH}"/><stop offset="1" stop-color="{SNOWDK}"/></linearGradient>'
    save('ground.svg', svg(W, H, body, defs))


# ---------- 4. ROT: rotting letter tiles sinking into snow (bottom-left) ----------
def make_rot():
    W, H = 170, 120
    defs, body = '', ''
    body += f'<path d="M-4 124V96C18 84 52 90 76 96C104 102 128 94 146 102C158 108 164 116 172 124Z" fill="url(#sg)" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round"/>'
    for x, y, s, ch, kind, rot, tid in ((20, 54, 38, 'R', 'rot', -4, 'a'), (58, 62, 36, 'O', 'rotbad', 7, 'b'), (94, 72, 32, 'T', 'rotbad', 24, 'c')):
        g, dd = tile(x, y, s, ch, kind, rot, tid)
        body += g; defs += dd
    # rubble crumbling off the T
    for cx, cy, s in ((136, 108, 1), (128, 113, .7), (147, 111, .6)):
        body += (f'<path d="M{cx - 7 * s} {cy + 4 * s}L{cx - 6 * s} {cy - 3 * s}L{cx} {cy - 6 * s}L{cx + 6 * s} {cy - 3 * s}L{cx + 7 * s} {cy + 4 * s}Z" fill="{RUB}" stroke="{INK}" stroke-width="1.8" stroke-linejoin="round"/>'
                 f'<circle cx="{cx - 2 * s}" cy="{cy - 1 * s}" r="{1.6 * s}" fill="{RUBHI}"/>')
    # rot mud spilling into the snow
    body += f'<path d="M14 100C22 94 40 96 52 100C66 104 84 100 96 104C88 110 62 110 46 108C32 110 18 108 14 100Z" fill="{ROT3}" stroke="{INK}" stroke-width="1.8"/>'
    body += f'<circle cx="34" cy="103" r="1.6" fill="{ROTDK}"/><circle cx="70" cy="104" r="1.4" fill="{ROTDK}"/>'
    # snow sitting on the tiles, mushrooms sprouting through
    body += snowcap(21, 54.5, 32, 6)
    body += snowcap(62, 61, 28, 5)
    body += mushroom(30, 50, .82) + mushroom(44, 51, .58, CAP2) + mushroom(80, 62, .7)
    body += snowcap(2, 100, 30, 6)
    body += snowcap(146, 102, 22, 5)
    # spores drifting up
    body += '<g fill="#d9b46a" opacity=".85"><circle cx="58" cy="36" r="1.6"/><circle cx="70" cy="28" r="1.1"/><circle cx="40" cy="30" r="1.2"/><circle cx="88" cy="44" r="1"/></g>'
    defs += f'<linearGradient id="sg" x1="0" y1="0" x2="0" y2="1"><stop offset=".3" stop-color="{SNOW}"/><stop offset="1" stop-color="{SNOWSH}"/></linearGradient>'
    save('rot.svg', svg(W, H, body, defs))


# ---------- 5. THAW: ice tiles melting under an Ignite ember (bottom-right) ----------
def make_thaw():
    W, H = 170, 120
    defs, body = '', ''
    # a crystal growing behind the stack
    for args in ((150, 98, -84, 70, 18), (162, 100, -66, 46, 13), (138, 100, -108, 38, 12)):
        o, _ = crystal(*args)
        body += o
    body += f'<path d="M-2 124C6 116 14 106 28 102C46 97 60 100 76 98C104 96 140 90 174 96V124Z" fill="url(#sg)" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round"/>'
    # meltwater pooling in front
    body += f'<ellipse cx="54" cy="108" rx="34" ry="7" fill="{ICE3}" stroke="{INK}" stroke-width="2"/>'
    body += f'<ellipse cx="51" cy="107" rx="24" ry="4" fill="{ICE2}"/>'
    body += f'<path d="M36 106Q46 103.6 56 105" stroke="#fff" stroke-width="1.6" fill="none" stroke-linecap="round"/>'
    body += f'<ellipse cx="70" cy="109" rx="6" ry="1.6" fill="none" stroke="#fff" stroke-width="1" opacity=".75"/>'
    s = 30
    for x, y, ch, kind, rot, tid in ((66, 70, 'A', 'ice', -3, 'p'), (97, 70, 'W', 'icecrack', 2, 'q'), (72, 38, 'T', 'ice', -6, 'r'), (103, 39, 'H', 'ice', 5, 's')):
        g, dd = tile(x, y, s, ch, kind, rot, tid)
        body += g; defs += dd
    # drips running off the bottom row
    body += drip(72, 101, 1) + drip(90, 100, .8) + drip(118, 101, 1.1)
    body += f'<path d="M84 102C84 98 80 98 79 101" stroke="{ICE1}" stroke-width="1.4" fill="none"/>'
    # thin, melting snow and the ember doing the melting
    body += snowcap(104, 40, 26, 4, 1.6)
    body += flame(85, 37, 1.05)
    body += f'<g fill="#ffd08a"><circle cx="78" cy="14" r="1.3"/><circle cx="94" cy="8" r="1"/><circle cx="88" cy="4" r=".8"/></g>'
    # steam
    body += f'<g fill="none" stroke="#e9f3ff" stroke-width="2" stroke-linecap="round" opacity=".55"><path d="M112 30C108 26 114 22 110 16"/><path d="M122 32C119 28 124 25 121 20"/></g>'
    body += sparkle(158, 24, 4) + sparkle(140, 50, 2.6, GLOWHI)
    defs += f'<linearGradient id="sg" x1="0" y1="0" x2="0" y2="1"><stop offset=".3" stop-color="{SNOW}"/><stop offset="1" stop-color="{SNOWSH}"/></linearGradient>'
    save('thaw.svg', svg(W, H, body, defs))


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


# ---------- 8. Frost lightning (flickers in the top corners) ----------
def make_bolt():
    W, H = 200, 120
    main = 'M0 8L26 14L38 6L62 22L80 16L102 34L124 30L146 48L170 46L196 62'
    br1 = 'M62 22L66 40L82 48L86 64'
    br2 = 'M124 30L132 14L150 10'
    br3 = 'M102 34L98 52L110 60'
    paths = [main, br1, br2, br3]
    body = ''.join(f'<path d="{p}" stroke="{GLOW}" stroke-width="7" opacity=".55" filter="url(#b)"/>' for p in paths)
    body += ''.join(f'<path d="{p}" stroke="{GLOW}" stroke-width="{2.6 if p == main else 1.8}"/>' for p in paths)
    body += ''.join(f'<path d="{p}" stroke="#fff" stroke-width="{1.1 if p == main else .8}"/>' for p in paths)
    body = f'<g fill="none" stroke-linejoin="round" stroke-linecap="round">{body}</g>'
    save('bolt.svg', svg(W, H, body, BLUR('b', 3)))


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
    ring = (f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}"/>'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx - 44}" ry="{ry - 13}"/>')
    body = f'<g fill="none" stroke="{GLOW}" stroke-width="12" opacity=".4" filter="url(#b)">{ring}</g>'
    body += f'<g fill="none" stroke="{GLOW}" stroke-width="3">{ring}</g>'
    body += f'<ellipse cx="{cx}" cy="{cy}" rx="{rx - 10}" ry="{ry - 3}" fill="none" stroke="{GLOWHI}" stroke-width="1" stroke-dasharray="2 10" opacity=".8"/>'
    body += f'<g fill="none" stroke="{GLOWHI}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" opacity=".95">{runes}</g>'
    body += f'<ellipse cx="{cx}" cy="{cy}" rx="{rx - 50}" ry="{ry - 16}" fill="{GLOW}" opacity=".07"/>'
    save('ring.svg', svg(W, H, body, BLUR('b', 6)))


# ---------- 10. Rot roots creeping up the side walls ----------
def make_roots():
    W, H = 26, 220
    main = 'M14 220C6 200 20 186 12 168C5 152 18 138 12 120C7 104 17 92 13 76C10 62 16 52 13 40'
    br = ['M12 168C18 162 22 164 24 156', 'M12 120C6 114 3 116 2 108', 'M13 76C18 72 21 74 22 66']
    body = f'<path d="{main}" fill="none" stroke="{INK}" stroke-width="6.4" stroke-linecap="round"/>'
    body += ''.join(f'<path d="{b}" fill="none" stroke="{INK}" stroke-width="4.4" stroke-linecap="round"/>' for b in br)
    body += f'<path d="{main}" fill="none" stroke="{ROT2}" stroke-width="3.4" stroke-linecap="round"/>'
    body += ''.join(f'<path d="{b}" fill="none" stroke="{ROT2}" stroke-width="2" stroke-linecap="round"/>' for b in br)
    body += f'<path d="{main}" fill="none" stroke="{ROT1}" stroke-width="1" stroke-linecap="round" stroke-dasharray="6 14" opacity=".8"/>'
    body += f'<g stroke="{INK}" stroke-width="1.2"><circle cx="24" cy="155" r="2.6" fill="{CAP}"/><circle cx="2" cy="107" r="2.2" fill="{CAP}"/><circle cx="22" cy="65" r="2" fill="{CAP2}"/></g>'
    body += f'<g fill="{SNOW}" stroke="{INK}" stroke-width="1"><path d="M8 170C9 166 15 166 16 169Z"/><path d="M9 122C10 118 15 118 16 121Z"/></g>'
    body += f'<g fill="#fff"><circle cx="13" cy="92" r="1"/><circle cx="11" cy="140" r=".9"/><circle cx="15" cy="196" r="1"/></g>'
    save('roots.svg', svg(W, H, body))


# ---------- 11. Snow cap for the Play button (repeats) ----------
def make_btncap():
    W, H = 60, 16
    d = 'M-2 16V9C4 2 10 3 14 7C18 1 28 1 31 7C35 3 44 1 48 7C52 4 58 4 62 9V16Z'
    body = f'<path d="{d}" fill="{SNOW}"/><path d="M-2 9C4 2 10 3 14 7C18 1 28 1 31 7C35 3 44 1 48 7C52 4 58 4 62 9" fill="none" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>'
    body += f'<path d="M-2 14C8 12 18 15 30 13C42 11 52 14 62 12V16H-2Z" fill="{SNOWSH}"/>'
    save('btncap.svg', svg(W, H, body))


# ---------- 12. Scene behind everything ----------
def make_bg():
    W, H = 800, 520
    body = '<rect width="800" height="520" fill="url(#sky)"/>'
    body += '<ellipse cx="400" cy="-20" rx="360" ry="200" fill="url(#top)"/>'
    # distant ice cliffs along the back wall
    cliff = 'M0 250L0 120L30 150L52 96L80 140L104 110L128 170L150 150L170 200L200 190L230 236L260 228L290 260V300H0Z'
    body += f'<path d="{cliff}" fill="{STONE1}" opacity=".9"/>'
    body += f'<path d="{cliff}" transform="translate(800 0) scale(-1 1)" fill="{STONE1}" opacity=".9"/>'
    body += f'<path d="M52 96L60 130L80 140M104 110L112 150M748 96L740 130L720 140" fill="none" stroke="#3a3c9a" stroke-width="3"/>'
    # light pouring down from the top
    body += '<rect x="356" y="-20" width="88" height="360" fill="url(#beam)" filter="url(#b8)"/>'
    body += '<rect x="390" y="-20" width="20" height="300" fill="url(#beam)" opacity=".8" filter="url(#b3)"/>'
    # paved floor in rings
    for i, (rx, ry, col) in enumerate(((720, 360, '#2a2a7a'), (560, 280, '#2f3088'), (420, 210, '#2b2c80'), (290, 150, '#31338e'))):
        body += f'<ellipse cx="400" cy="640" rx="{rx}" ry="{ry}" fill="{col}"/>'
    joints = ''
    for k in range(-9, 10):
        a = math.radians(90 + k * 9.5)
        joints += f'<line x1="400" y1="640" x2="{400 + 760 * math.cos(a):.0f}" y2="{640 - 380 * math.sin(a):.0f}"/>'
    body += f'<g stroke="#23226a" stroke-width="2.4" opacity=".75">{joints}</g>'
    for rx, ry in ((720, 360), (560, 280), (420, 210), (290, 150)):
        body += f'<ellipse cx="400" cy="640" rx="{rx}" ry="{ry}" fill="none" stroke="#1d1c58" stroke-width="3"/>'
    # snow scattered over the stones
    import random
    rnd = random.Random(7)
    flakes = ''.join(f'<ellipse cx="{rnd.uniform(0, 800):.0f}" cy="{rnd.uniform(300, 520):.0f}" rx="{rnd.uniform(3, 9):.1f}" ry="{rnd.uniform(1.4, 3):.1f}"/>' for _ in range(40))
    body += f'<g fill="{SNOW}" opacity=".22">{flakes}</g>'
    body += '<rect width="800" height="520" fill="url(#vig)"/>'
    defs = (f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#16133d"/><stop offset=".5" stop-color="#1f1c55"/><stop offset="1" stop-color="#2a2a74"/></linearGradient>'
            f'<radialGradient id="top"><stop offset="0" stop-color="{GLOW}" stop-opacity=".2"/><stop offset="1" stop-color="{GLOW}" stop-opacity="0"/></radialGradient>'
            f'<linearGradient id="beam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{GLOWHI}" stop-opacity=".45"/><stop offset=".55" stop-color="{GLOW}" stop-opacity=".14"/><stop offset="1" stop-color="{GLOW}" stop-opacity="0"/></linearGradient>'
            f'<radialGradient id="vig" cx=".5" cy=".45" r=".75"><stop offset=".55" stop-color="#0b0a24" stop-opacity="0"/><stop offset="1" stop-color="#0b0a24" stop-opacity=".7"/></radialGradient>'
            + BLUR('b8', 10) + BLUR('b3', 4))
    save('bg.svg', svg(W, H, body, defs))


if __name__ == '__main__':
    for f in (make_crystals, make_cornice, make_ground, make_rot, make_thaw, make_lantern, make_wisp, make_bolt, make_ring, make_roots, make_btncap, make_bg):
        f()
    print('sprites written to', HERE)
