#!/usr/bin/env python3
"""Submit the site's sitemap URLs to IndexNow (Bing, Yandex, Naver, Seznam, Yep).

Reads the 32-hex key file at the repo root and every <loc> in sitemap.xml, then
POSTs them to the IndexNow endpoint. Google does not participate in IndexNow;
use Search Console + the sitemap for Google.
"""
import glob
import json
import os
import re
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOST = "coralc-lang.github.io"
BASE = f"https://{HOST}/coral-docs"

keys = [
    os.path.basename(p)[:-4]
    for p in glob.glob(os.path.join(ROOT, "*.txt"))
    if re.fullmatch(r"[0-9a-f]{32}", os.path.basename(p)[:-4])
]
if not keys:
    sys.exit("no IndexNow key file (32-hex .txt) found at repo root")
key = keys[0]

sitemap_path = os.path.join(ROOT, "sitemap.xml")
locs = re.findall(r"<loc>([^<]+)</loc>", open(sitemap_path, encoding="utf-8").read())
if not locs:
    sys.exit("no URLs found in sitemap.xml")

body = json.dumps(
    {
        "host": HOST,
        "key": key,
        "keyLocation": f"{BASE}/{key}.txt",
        "urlList": locs,
    }
).encode()
req = urllib.request.Request(
    "https://api.indexnow.org/indexnow",
    data=body,
    headers={"Content-Type": "application/json; charset=utf-8"},
)
try:
    resp = urllib.request.urlopen(req, timeout=30)
    print(f"IndexNow: {resp.status} {resp.reason} ({len(locs)} urls)")
except urllib.error.HTTPError as exc:
    print(f"IndexNow error {exc.code}: {exc.read()[:300]!r}")
    sys.exit(1)
