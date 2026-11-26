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

CSS = f"""/* ROT-CARD: the play box dressed as a frozen courtyard with rot breaking through.
   Sprites are drawn by art/rot-card/make_sprites.py and copied in by art/rot-card/inline.py. */
.play-card{{position:relative}}
.rc,.rc-o{{display:none;position:absolute;inset:0;pointer-events:none}}
.rc{{border-radius:12px;overflow:hidden;z-index:0}}
.rc-o{{z-index:3}}
.play-card.rotframe .rc,.play-card.rotframe .rc-o{{display:block}}
.play-card>.pc-stack,.play-card>.pc-guide,.play-card>.ps-actions{{position:relative;z-index:2}}
.t-card.play-card.rotframe{{--mc:#7fe3ff;border-color:#8feaff;background:#1b1848;padding:48px 28px 94px;box-shadow:0 0 0 2px {INK},0 0 36px -4px #62f0ffaa,0 26px 60px -22px #000}}
.rc i,.rc-o i{{position:absolute;display:block}}
.rc-bg{{inset:0;background:{U['bg']} center bottom/cover no-repeat}}
.rc-beam{{left:50%;top:0;width:150px;height:70%;transform:translateX(-50%);background:radial-gradient(ellipse 50% 100% at 50% 0,#d4feff40,transparent 75%);animation:rcbeam 6s ease-in-out infinite}}
.rc-bolt{{top:4px;width:190px;height:114px;background:{U['bolt']} center/contain no-repeat;opacity:0;animation:rcbolt 8s linear infinite}}
.rc-bolt.l{{left:30px}}.rc-bolt.r{{right:30px;transform:scaleX(-1);animation-delay:-4.3s}}
.rc-roots{{bottom:70px;width:22px;height:186px;background:{U['roots']} center bottom/contain no-repeat;opacity:.95}}
.rc-roots.l{{left:3px}}.rc-roots.r{{right:3px;transform:scaleX(-1)}}
.rc-wisp{{width:24px;height:31px;background:{U['wisp']} center/contain no-repeat;animation:rcwisp 5s ease-in-out infinite}}
.rc-wisp.a{{left:5px;top:34%}}.rc-wisp.b{{right:7px;top:22%;width:18px;height:23px;animation-delay:-2.2s}}
.rc-ring{{left:50%;bottom:38px;width:min(660px,118%);aspect-ratio:640/140;transform:translateX(-50%);background:{U['ring']} center/contain no-repeat;animation:rcring 4s ease-in-out infinite}}
.rc-top{{left:0;right:0;top:0;height:40px;background:{U['cornice']} repeat-x left top/auto 40px}}
.rc-ground{{left:0;right:0;bottom:0;height:70px;background:{U['ground']} repeat-x center bottom/auto 70px}}
.rc-lamp{{bottom:14px;width:30px;height:72px;background:{U['lantern']} center bottom/contain no-repeat}}
.rc-lamp.l{{left:27%}}.rc-lamp.r{{right:27%}}
.rc-rot{{left:-6px;bottom:-4px;width:150px;height:106px;background:{U['rot']} left bottom/contain no-repeat}}
.rc-thaw{{right:-6px;bottom:-4px;width:140px;height:99px;background:{U['thaw']} right bottom/contain no-repeat}}
.rc-glow{{right:40px;bottom:40px;width:50px;height:50px;border-radius:50%;background:radial-gradient(#ff9a3c99,transparent 68%);animation:rcember .7s ease-in-out infinite alternate}}
.rc-snow{{inset:0;opacity:.8;background-image:radial-gradient(2px 2px at 20px 30px,#fff,transparent),radial-gradient(2.5px 2.5px at 110px 140px,#eaf6ff,transparent),radial-gradient(1.6px 1.6px at 70px 90px,#ffffffcc,transparent),radial-gradient(1.6px 1.6px at 150px 20px,#ffffffaa,transparent);background-size:170px 210px,170px 210px,120px 160px,120px 160px;animation:rcsnow 11s linear infinite}}
.rc-ice{{top:-18px;width:128px;height:120px;background:{U['crystals']} left top/contain no-repeat}}
.rc-ice.l{{left:-24px}}.rc-ice.r{{right:-24px;transform:scaleX(-1)}}
.rc-plq{{position:absolute;top:-12px;left:50%;transform:translateX(-50%);padding:6px 16px 5px;border-radius:8px;background:linear-gradient(#3c3fa6,#25236a);border:2px solid {INK};box-shadow:0 3px 0 {INK},0 0 18px -4px #62f0ff,inset 0 -3px 0 #0005;color:#e6fbff;font:400 12px/1 var(--f-display);letter-spacing:.12em;white-space:nowrap;text-shadow:0 0 8px #62f0ff,0 1px 0 {INK}}}
.rc-plq::before{{content:'';position:absolute;left:-5px;right:-5px;top:-8px;height:12px;background:{U['btncap']} repeat-x left top/auto 12px}}
.rc-plq::after{{content:'';position:absolute;left:10%;right:10%;bottom:-13px;height:12px;background:{U['cornice']} repeat-x center bottom/auto 30px;clip-path:inset(42% 0 0 0)}}
.rotframe .t-play{{position:relative;border:2px solid {INK};background:linear-gradient(#effdff,#a9eaff 45%,#58c6f2);color:#0b2450;text-shadow:0 1px 0 #fff9;box-shadow:inset 0 -5px 0 #2c86cf,inset 0 2px 0 #fff,0 0 0 2px #62f0ff55,0 0 34px -6px #62f0ff}}
.rotframe .t-play::before{{content:'';position:absolute;left:5px;right:5px;top:-10px;height:16px;background:{U['btncap']} repeat-x left top/auto 16px;pointer-events:none}}
.rotframe .t-switch{{border-color:#7fe3ffaa;background:#1d1b54e6;box-shadow:inset 0 0 22px -8px #62f0ff}}
.rotframe .pd-art{{background:radial-gradient(circle at 50% 25%,#62f0ff3a,transparent 65%),#100e30e6;border-color:#7fe3ff88;box-shadow:inset 0 0 30px -12px #a9eaff}}
.rotframe .pd-stats>div,.rotframe .seg{{background:#100e30d9}}
.rotframe .pc-mode{{border-top-color:#7fe3ff44}}
.rotframe .t-vdesc,.rotframe .pm-desc,.rotframe .tc-sub{{color:#c9d0f6}}
.rotframe .pc-guide{{background:#100e30cc}}
@keyframes rcbeam{{50%{{opacity:.55}}}}
@keyframes rcring{{50%{{opacity:.7}}}}
@keyframes rcbolt{{0%,100%{{opacity:0}}3%{{opacity:.9}}4%{{opacity:.15}}5.5%{{opacity:1}}9%{{opacity:0}}}}
@keyframes rcwisp{{50%{{transform:translateY(-9px);opacity:.75}}}}
@keyframes rcember{{to{{transform:scale(1.25);opacity:.7}}}}
@keyframes rcsnow{{to{{background-position:40px 210px,40px 210px,-24px 160px,-24px 160px}}}}
.rc-wisp.b{{animation-name:rcwisp}}
.calm .rc *,.calm .rc-o *{{animation:none!important}}
@media (prefers-reduced-motion:reduce){{.rc *,.rc-o *{{animation:none!important}}}}
@media (max-width:560px){{
  .t-card.play-card.rotframe{{padding:44px 18px 82px}}
  .rc-rot{{width:118px;height:83px}}.rc-thaw{{width:112px;height:79px}}
  .rc-glow{{right:32px;bottom:30px;width:40px;height:40px}}
  .rc-ice{{width:96px;height:90px;top:-13px}}.rc-ice.l{{left:-14px}}.rc-ice.r{{right:-14px}}
  .rc-roots{{bottom:60px;height:140px;width:17px}}
  .rc-ring{{bottom:30px;width:150%}}
}}
/* /ROT-CARD */
"""

MARKUP = ('<div class="rc" aria-hidden="true"><i class="rc-bg"></i><i class="rc-beam"></i><i class="rc-bolt l"></i><i class="rc-bolt r"></i>'
          '<i class="rc-roots l"></i><i class="rc-roots r"></i><i class="rc-wisp a"></i><i class="rc-wisp b"></i><i class="rc-ring"></i>'
          '<i class="rc-top"></i><i class="rc-ground"></i><i class="rc-lamp l"></i><i class="rc-lamp r"></i><i class="rc-rot"></i>'
          '<i class="rc-thaw"></i><i class="rc-glow"></i><i class="rc-snow"></i></div>'
          '<div class="rc-o" aria-hidden="true"><i class="rc-ice l"></i><i class="rc-ice r"></i><span class="rc-plq">Rot &amp; Thaw</span></div>')

s = open(PAGE, encoding='utf-8').read()
# CSS: replace a previous ROT-CARD block, or the old frame block it grew out of.
if '/* ROT-CARD:' in s:
    a = s.index('/* ROT-CARD:'); b = s.index('/* /ROT-CARD */', a) + len('/* /ROT-CARD */\n')
else:
    a = s.index('/* Rot & Thaw frame around the play box'); b = s.index('/* Tutorials */', a)
s = s[:a] + CSS + ('' if '/* /ROT-CARD */' in s[a:b] else '\n') + s[b:]
# Markup inside #playCard.
s, n = re.subn(r'<div class="rf" aria-hidden="true">.*?</span></div>|<div class="rc" aria-hidden="true">.*?<span class="rc-plq">Rot &amp; Thaw</span></div>', lambda m: MARKUP, s, count=1, flags=re.S)
assert n == 1, 'play card markup not found'
open(PAGE, 'w', encoding='utf-8', newline='\n').write(s)
print('inlined', len(U), 'sprites;', sum(len(v) for v in U.values()) // 1024, 'KB of data URIs')
