"""Copies the Rot & Thaw card sprites into wordfall.html as data URIs.

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

CSS = f"""/* ROT-CARD: the play box in Rot & Thaw. A textured brown-red rot skin, a snow cap glazed
   with ice along the top, and clear ice layered round the edges over the rot.
   Textures (rotskin.svg, snowice.svg) live in art/rot-card and are copied in by art/rot-card/inline.py. */
.play-card{{position:relative}}
.rc,.rc-o{{display:none;position:absolute;inset:0;pointer-events:none}}
.rc{{border-radius:12px;overflow:hidden;z-index:0}}
.play-card.rotframe .rc{{display:block}}
.play-card>.pc-stack,.play-card>.pc-guide,.play-card>.ps-actions{{position:relative;z-index:2}}
.t-card.play-card.rotframe{{--mc:#bfeaff;border-color:#d6f3ff;background:#6a2620;padding:52px 26px 26px;box-shadow:0 0 0 2px #1c0806,0 0 26px -6px #9fdcffaa,0 26px 60px -22px #000}}
.rc i{{position:absolute;display:block}}
.rc-skin{{inset:0;background:radial-gradient(ellipse 120% 95% at 50% 45%,transparent 50%,#240906b0),{U['rotskin']} 0 0/260px 260px,#6a2620}}
.rc-rim{{inset:0;border-radius:inherit;padding:12px;background:linear-gradient(90deg,#ffffff38,transparent 30% 70%,#ffffff2e),linear-gradient(165deg,#f2fcffeb,#c8eeffa6 20%,#a8e2ff7a 48%,#c8eeff94 76%,#eefaffd9);-webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);-webkit-mask-composite:xor;mask-composite:exclude}}
.rc-frost{{inset:12px;border-radius:5px;box-shadow:0 0 0 1px #f4fdffd9,0 0 0 2.5px #7fcfff55,inset 0 0 18px #bfeaff3d}}
.rc-cap{{left:0;right:0;top:0;height:54px;background:{U['snowice']} repeat-x left top/auto 54px;filter:drop-shadow(0 2px 2px #1c080699)}}
.rotframe .t-play{{position:relative;border:2px solid #1c0806;background:linear-gradient(#f2fcff,#bfeaff 45%,#7fcff2);color:#3a110c;text-shadow:0 1px 0 #fff9;box-shadow:inset 0 -5px 0 #4a9fd0,inset 0 2px 0 #fff,0 0 0 2px #bfeaff55,0 0 26px -6px #9fdcff}}
.rotframe .t-switch{{border-color:#d6f3ff88;background:#2a0d0ae6;box-shadow:inset 0 0 20px -8px #bfeaff}}
.rotframe .pd-art{{background:radial-gradient(circle at 50% 25%,#bfeaff22,transparent 65%),#250b09e6;border-color:#d6f3ff77;box-shadow:none}}
.rotframe .pd-stats>div,.rotframe .seg{{background:#250b09d9}}
.rotframe .pc-mode{{border-top-color:#d6f3ff44}}
.rotframe .t-vdesc,.rotframe .pm-desc,.rotframe .tc-sub{{color:#f2dcd5}}
.rotframe .pc-guide{{background:#250b09cc}}
.rotframe .seg button[aria-pressed="true"]{{background:linear-gradient(#e9faff,#a8e2ff);color:#3a110c}}
@media (max-width:560px){{
  .t-card.play-card.rotframe{{padding:48px 16px 20px}}
  .rc-rim{{padding:9px}}.rc-frost{{inset:9px}}
}}
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

MARKUP = ('<div class="rc" aria-hidden="true"><i class="rc-skin"></i><i class="rc-rim"></i><i class="rc-frost"></i><i class="rc-cap"></i></div>'
          '<div class="rc-o" aria-hidden="true"></div>')

s = open(PAGE, encoding='utf-8').read()
# CSS: replace a previous ROT-CARD block, or the old frame block it grew out of.
if '/* ROT-CARD:' in s:
    a = s.index('/* ROT-CARD:'); b = s.index('/* /ROT-CARD */', a) + len('/* /ROT-CARD */\n')
else:
    a = s.index('/* Rot & Thaw frame around the play box'); b = s.index('/* Tutorials */', a)
s = s[:a] + CSS + ('' if '/* /ROT-CARD */' in s[a:b] else '\n') + s[b:]
# Markup inside #playCard.
s, n = re.subn(r'<div class="rc" aria-hidden="true">.*?<div class="rc-o" aria-hidden="true">.*?</div>', lambda m: MARKUP, s, count=1, flags=re.S)
assert n == 1, 'play card markup not found'
open(PAGE, 'w', encoding='utf-8', newline='\n').write(s)
used = [k for k in U if U[k] in CSS]
print('inlined', len(used), 'sprites:', ', '.join(used), '|', sum(len(U[k]) for k in used) // 1024, 'KB of data URIs')
