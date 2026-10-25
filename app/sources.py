# TODO (YOU): This file only reads jobs from a CSV upload or a public
# RSS/Atom URL you paste in. There is no login-based or scraped job source
# here by design (see README's note on CAPTCHA/anti-bot/site restrictions).
# If you later add a new source, keep it to APIs/feeds you're actually
# permitted to use, and return dicts shaped like the ones below so the rest
# of the app (matcher, db) doesn't need to change.
import csv,io,requests,xml.etree.ElementTree as ET

def csv_jobs(f):
    rows=csv.DictReader(io.StringIO(f.getvalue().decode("utf-8-sig")))
    return [dict(r) for r in rows]

def rss_jobs(url,name="RSS"):
    r=requests.get(url,headers={"User-Agent":"JobMatchAssistant/1.0"},timeout=15)
    r.raise_for_status(); root=ET.fromstring(r.content); out=[]
    for x in root.findall(".//item"):
        out.append({"title":x.findtext("title") or "","company":"","location":"",
        "experience":"","salary":"","url":x.findtext("link") or "",
        "description":x.findtext("description") or "","source":name,
        "posted_at":x.findtext("pubDate") or ""})
    return out
