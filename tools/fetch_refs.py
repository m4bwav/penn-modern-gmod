"""Download Commons reference photos at 1600px into refs/photos and log sources in refs/SOURCES.md.
Usage: python tools/fetch_refs.py "File:A.jpg" "File:B.jpg" ..."""
import datetime, json, os, re, sys, urllib.parse, urllib.request

UA = {"User-Agent": "penn-modern-gmod-refs/1.0 (m4bwav@gmail.com)"}
os.makedirs("refs/photos", exist_ok=True)

def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA)).read()

rows = []
for title in sys.argv[1:]:
    q = urllib.parse.urlencode({"action": "query", "format": "json", "titles": title, "prop": "imageinfo",
                                "iiprop": "url|extmetadata", "iiurlwidth": 1600})
    page = next(iter(json.loads(get("https://commons.wikimedia.org/w/api.php?" + q))["query"]["pages"].values()))
    ii = page["imageinfo"][0]
    m = ii["extmetadata"]
    name = re.sub(r"[^A-Za-z0-9]+", "_", title[5:].rsplit(".", 1)[0]).strip("_")[:60] + ".jpg"
    open("refs/photos/" + name, "wb").write(get(ii["thumburl"]))
    artist = re.sub("<[^>]+>", "", m.get("Artist", {}).get("value", "?")).strip()
    lic = m.get('LicenseShortName', {}).get('value', '?')
    if re.search(r"\bNC\b|\bND\b|non-?commercial|no deriv", lic, re.I) or lic == "?":
        sys.exit(f"refusing {title}: licence {lic} is not redistributable")
    rows.append(f"| {name} | {title[5:].rsplit('.', 1)[0]} | {artist} | {lic} | {ii['descriptionurl']} | {datetime.date.today()} |")
    print(name)

# refs/SOURCES.md columns: File | Subject | Author | Licence | URL | Fetched
with open("refs/SOURCES.md", "a", encoding="utf-8", newline="") as f:
    f.write("\n".join(rows) + "\n")
