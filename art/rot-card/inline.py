"""Copies the Rot & Thaw card styles and textures into wordfall.html (textures as data URIs).

Replaces everything between the ROT-CARD markers (CSS) and the .rc markup in #playCard,
so it can be re-run after editing make_sprites.py.
"""
import os, re
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.join(HERE, '..', '..', 'wordfall.html')
INK = '#15123a'


def uri(name):
    s = open(os.path.join(HERE, name), encoding='utf-8').read()
    s = re.sub(r'\s+', ' ', s).replace('"', "'")
    return 'url("data:image/svg+xml,' + quote(s, safe=" =:/,;.-'()") + '")'


U = {n[:-4]: uri(n) for n in os.listdir(HERE) if n.endswith('.svg')}

CSS = f"""/* ROT-CARD: the play box in Rot & Thaw. Night sky fading into rot at the bottom, a half-played
   stack of real board cells along the bottom (rubble, rotting blocks, netherrack power tiles, snow and ice on top),
   pixel snow falling behind the card, and a dark red glow round the rim. rotDeco() in the page script builds the
   stack; rotskin.svg lives in art/rot-card and is copied in by art/rot-card/inline.py. */
.play-card{{position:relative}}
.rc{{display:none;position:absolute;inset:0;pointer-events:none;border-radius:12px;overflow:hidden;z-index:0}}
.play-card.rotframe .rc{{display:block}}
.play-card>.pc-stack,.play-card>.pc-guide,.play-card>.ps-actions{{position:relative;z-index:2}}
.t-card.play-card.rotframe{{--mc:#9fdcff;--rt:22px;border-color:#7a2219;padding-bottom:100px;background:linear-gradient(#141b3d 0%,#16142f 50%,#2a1411cc 100%),{U['rotskin']} 0 0/260px 260px,#2a1411;box-shadow:0 0 0 1px #2a0806,0 0 32px -4px #a3241ab3,0 0 80px -18px #7a1410,0 24px 60px -24px #000}}
.rotframe .pd-art,.rotframe .t-switch{{background:#0d0b1fd9}}
.rc .c{{position:absolute!important;margin:0;width:var(--rt);height:var(--rt);--cell:var(--rt);--pc:#c4ae7f;animation:none!important}}
.rc .c.tile.ice::before{{font-size:.5em}}
.rc .c.nether{{background:linear-gradient(#a8504a,#83342f);box-shadow:inset 0 -4px 0 #5c2320}}
.rc .c.nether::after{{content:'';position:absolute;inset:0;border-radius:inherit;background:radial-gradient(circle at 25% 70%,#5e211e 0 12%,transparent 14%),radial-gradient(circle at 72% 30%,#6c2825 0 10%,transparent 12%)}}
.rc .flake{{position:absolute;top:-6px;width:3px;height:3px;background:#e9f6ff;box-shadow:0 0 4px #bfeaff;animation:rcfall linear infinite}}
.rc .flake.b{{width:4px;height:4px}}
@keyframes rcfall{{to{{transform:translate(18px,var(--fall,640px))}}}}
.calm .rc .flake{{display:none}}
@media (prefers-reduced-motion:reduce){{.rc .flake{{display:none}}}}
@media (max-width:560px){{.t-card.play-card.rotframe{{--rt:18px;padding-bottom:84px}}}}
/* Rot tiles: in Rot & Thaw the letters that give Ignite are burning red rot, crowned with flame. */
.c.orb.o-ignite{{background:radial-gradient(circle at 28% 24%,#ffd0cc 0 7%,transparent 9%),radial-gradient(ellipse 62% 48% at 34% 28%,#ff8c8c,transparent 72%),radial-gradient(ellipse 95% 70% at 82% 96%,#b8304a 0 52%,transparent 74%),#e8505e;color:#2a0710;text-shadow:0 1px 0 #ffc2bd99;border-radius:42% 42% 34% 34%/46% 46% 30% 30%;box-shadow:inset 0 -4px 0 #7a1830,0 0 0 2px #2a0f17,0 0 14px 2px #ff6a3c88;animation:rotpulse 1.2s ease-in-out infinite alternate;z-index:3}}
.c.orb.o-ignite::after{{content:'';top:auto;right:auto;bottom:66%;left:-6%;width:112%;height:56%;border-radius:0;background:{U['tileflame']} center bottom/100% 100% no-repeat;box-shadow:none;transform-origin:50% 100%;animation:rotflame .45s ease-in-out infinite alternate;pointer-events:none}}
.c.cur.orb.o-ignite{{box-shadow:inset 0 -4px 0 #7a1830,0 0 0 2px #2a0f17,0 0 0 4px #ff9a3c,0 0 18px 3px #ff6a3c}}
.mini i.orb.o-ignite{{background:linear-gradient(165deg,#ff8c8c,#e8505e 45%,#b8304a);color:#2a0710;border-radius:42% 42% 34% 34%;box-shadow:0 0 0 1.5px #2a0f17,0 0 8px #ff6a3c;animation:none}}
.rg-art i.orb{{background:radial-gradient(ellipse 62% 48% at 34% 28%,#ff8c8c,transparent 72%),radial-gradient(ellipse 95% 70% at 82% 96%,#b8304a 0 52%,transparent 74%),#e8505e;color:#2a0710;text-shadow:none;border-radius:42% 42% 34% 34%/46% 46% 30% 30%;box-shadow:inset 0 -3px 0 #7a1830,0 0 0 1.5px #2a0f17,0 0 10px #ff6a3c88}}
.rg-art i.orb::after{{content:'';top:-12px;right:auto;left:-2px;width:34px;height:15px;font-size:0;background:{U['tileflame']} center bottom/100% 100% no-repeat}}
.rotchip{{display:inline-block;width:1.05em;height:1.05em;vertical-align:-.15em;border-radius:42% 42% 34% 34%/46% 46% 30% 30%;background:linear-gradient(165deg,#ff8c8c,#e8505e 45%,#b8304a);box-shadow:0 0 0 1.5px #2a0f17,0 0 6px #ff6a3c;position:relative;margin:.3em .15em 0}}
.rotchip::after{{content:'';position:absolute;left:-12%;right:-12%;bottom:68%;height:70%;background:{U['tileflame']} center bottom/100% 100% no-repeat}}
@keyframes rotpulse{{to{{filter:brightness(1.12) saturate(1.1);transform:translateY(-1px)}}}}
@keyframes rotflame{{from{{transform:scale(.9,.84)}}to{{transform:scale(1.04,1.08)}}}}
.calm .c.orb.o-ignite,.calm .c.orb.o-ignite::after{{animation:none}}
@media (prefers-reduced-motion:reduce){{.c.orb.o-ignite,.c.orb.o-ignite::after{{animation:none}}}}
/* /ROT-CARD */
"""

MARKUP = '<div class="rc" aria-hidden="true"></div>'

s = open(PAGE, encoding='utf-8').read()
# CSS: replace a previous ROT-CARD block, or the old frame block it grew out of.
if '/* ROT-CARD:' in s:
    a = s.index('/* ROT-CARD:'); b = s.index('/* /ROT-CARD */', a) + len('/* /ROT-CARD */\n')
else:
    a = s.index('/* Rot & Thaw frame around the play box'); b = s.index('/* Tutorials */', a)
s = s[:a] + CSS + ('' if '/* /ROT-CARD */' in s[a:b] else '\n') + s[b:]
# Markup inside #playCard.
s, n = re.subn(r'<div class="rc" aria-hidden="true">.*?</div>(?:<div class="rc-o" aria-hidden="true"></div>)?', lambda m: MARKUP, s, count=1, flags=re.S)
assert n == 1, 'play card markup not found'
open(PAGE, 'w', encoding='utf-8', newline='\n').write(s)
used = [k for k in U if U[k] in CSS]
print('inlined', len(used), 'sprites:', ', '.join(used), '|', sum(len(U[k]) for k in used) // 1024, 'KB of data URIs')
