"""Build the self-hosted copy of Wordfall.

Reads ../wordfall.html and deploy/config.json, then writes deploy/site/index.html:
  - adds the <!doctype>, charset and viewport tags that claude.ai adds for the artifact
  - fills in the Supabase project URL and public (anon) key so Online works off claude.ai

config.json looks like:
  { "url": "https://YOUR-PROJECT.supabase.co", "key": "YOUR-ANON-PUBLIC-KEY" }

Run:  python deploy/build.py
Then drag the deploy/site folder onto https://app.netlify.com/drop (or use the Netlify CLI).
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "wordfall.html")
CFG = os.path.join(HERE, "config.json")
OUT_DIR = os.path.join(HERE, "site")

src = open(SRC, encoding="utf8").read()
cfg = {"url": "", "key": ""}
if os.path.exists(CFG):
    cfg.update(json.load(open(CFG, encoding="utf8")))
else:
    print("No deploy/config.json: building without Online (bots and solo still work).")

url, key = cfg.get("url", "").strip().rstrip("/"), cfg.get("key", "").strip()
if url and not re.fullmatch(r"https://[a-z0-9-]+\.supabase\.co", url):
    sys.exit(f"config.json url should look like https://abcd1234.supabase.co, got {url!r}")
if url and not key:
    sys.exit("config.json has a url but no key")

PLACE = "const WF_SUPABASE = { url: '', key: '' };"
if src.count(PLACE) != 1:
    sys.exit("Couldn't find the WF_SUPABASE line in wordfall.html")
src = src.replace(PLACE, f"const WF_SUPABASE = {{ url: {json.dumps(url)}, key: {json.dumps(key)} }};")

head = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        '</head><body>\n')
os.makedirs(OUT_DIR, exist_ok=True)
with open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf8") as f:
    f.write(head + src + "\n</body></html>\n")
print("Wrote", os.path.join(OUT_DIR, "index.html"), "| Online:", "Supabase" if url else "off")
