#!/usr/bin/env python3
"""Phone notification (via ntfy.sh) when aurora is possible at the site.

Runs every 3 hours from GitHub Actions. Each run looks at the next NOAA Kp
block (starting within about 3 hours), so every block is checked once, and alerts when Kp
reaches the camera threshold for the site's latitude, the Sun is more than 12°
down and forecast cloud is at most 50%.

    python3 .github/aurora_alert.py --mode dry-run   # print, don't send
    python3 .github/aurora_alert.py --mode test      # send a test notification
"""
import argparse
import json
import math
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

SITE = {"name": "Pennard", "lat": 51.576, "lon": -4.088}
PAGE = "https://ioancw.github.io/skychart/"
KP_URL = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index-forecast.json"
MAX_CLOUD = 50
BLOCK = timedelta(hours=3)
TZ = ZoneInfo("Europe/London")


def get_json(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)


def parse_kp(raw):
    """NOAA has published this as rows with a header and as objects; accept both."""
    rows = [dict(zip(raw[0], r)) for r in raw[1:]] if isinstance(raw[0], list) else raw
    out = []
    for o in rows:
        try:
            t = datetime.fromisoformat(str(o["time_tag"]).replace(" ", "T").replace("Z", ""))
            out.append((t.replace(tzinfo=timezone.utc), float(o["kp"])))
        except (KeyError, TypeError, ValueError):
            continue
    return out


def kp_needed(lat):
    """Rough Kp for a camera to catch aurora low in the north (eye needs one more)."""
    return (5 if lat >= 58 else 6 if lat >= 55 else 7) - 1


def sun_alt(dt, lat, lon):
    """Low-precision solar altitude in degrees (good to about a degree)."""
    d = (dt - datetime(2000, 1, 1, 12, tzinfo=timezone.utc)).total_seconds() / 86400
    g = math.radians(357.528 + 0.9856003 * d)
    lam = math.radians(280.460 + 0.9856474 * d + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g))
    eps = math.radians(23.439 - 4e-7 * d)
    ra = math.atan2(math.cos(eps) * math.sin(lam), math.cos(lam))
    dec = math.asin(math.sin(eps) * math.sin(lam))
    ha = math.radians((280.46061837 + 360.98564736629 * d + lon) % 360) - ra
    phi = math.radians(lat)
    return math.degrees(math.asin(math.sin(phi) * math.sin(dec) + math.cos(phi) * math.cos(dec) * math.cos(ha)))


def cloud_by_hour(lat, lon):
    q = urllib.parse.urlencode({"latitude": lat, "longitude": lon, "hourly": "cloud_cover",
                                "models": "ukmo_seamless", "forecast_hours": 24, "timeformat": "unixtime"})
    h = get_json(f"https://api.open-meteo.com/v1/forecast?{q}")["hourly"]
    return {datetime.fromtimestamp(t, timezone.utc): c for t, c in zip(h["time"], h["cloud_cover"]) if c is not None}


def check(now, kp, cloud, site):
    """Return (title, message) if the next Kp block deserves an alert, else None, plus a log line."""
    slot = now.replace(minute=0, second=0, microsecond=0) - timedelta(hours=now.hour % 3)
    start = slot + BLOCK
    block = next((v for t, v in kp if t == start), None)
    need = kp_needed(site["lat"])
    hours = [start + timedelta(hours=i) for i in range(3)]
    dark = [h for h in hours if sun_alt(h + timedelta(minutes=30), site["lat"], site["lon"]) < -12]
    covers = [cloud[h] for h in dark if h in cloud]
    mean = sum(covers) / len(covers) if covers else None
    when = f"{start.astimezone(TZ):%a %H:%M}-{(start + BLOCK).astimezone(TZ):%H:%M}"
    log = f"block {when}: Kp {block}, need {need}, dark hours {len(dark)}, cloud {mean}"
    if block is None or block < need or not dark or mean is None or mean > MAX_CLOUD:
        return None, log
    eye = "may be visible by eye" if block >= need + 1 else "a camera will show more than your eyes"
    title = f"Aurora possible at {site['name']} {when}"
    msg = f"Kp {block:.1f} forecast ({eye}). Cloud about {mean:.0f}%. Look low to the north."
    return (title, msg), log


def send(topic, title, msg):
    req = urllib.request.Request(f"https://ntfy.sh/{topic}", data=msg.encode(), method="POST",
                                 headers={"Title": title, "Tags": "milky_way", "Click": PAGE, "Priority": "high"})
    urllib.request.urlopen(req, timeout=30).close()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["normal", "test", "dry-run"], default="normal")
    p.add_argument("--kp-file", help="saved NOAA JSON, for testing")
    p.add_argument("--cloud-file", help="saved Open-Meteo JSON, for testing")
    p.add_argument("--now", help="ISO time to pretend it is, for testing")
    a = p.parse_args()

    topic = os.environ.get("NTFY_TOPIC", "").strip()
    if not topic and a.mode == "test":
        sys.exit("NTFY_TOPIC is not set: add it as a repository secret.")
    if not topic and a.mode == "normal":
        # Not set up yet: still check the feeds, but don't fail every scheduled run.
        print("::warning::NTFY_TOPIC is not set, so no notification will be sent.")
        a.mode = "dry-run"
    if a.mode == "test":
        send(topic, "Sky Chart test", "Aurora alerts are set up. You'll get one when aurora is likely and skies are clear.")
        print("sent test notification")
        return

    now = datetime.fromisoformat(a.now) if a.now else datetime.now(timezone.utc)
    kp = parse_kp(json.load(open(a.kp_file)) if a.kp_file else get_json(KP_URL))
    if a.cloud_file:
        h = json.load(open(a.cloud_file))["hourly"]
        cloud = {datetime.fromtimestamp(t, timezone.utc): c for t, c in zip(h["time"], h["cloud_cover"])}
    else:
        cloud = cloud_by_hour(SITE["lat"], SITE["lon"])

    alert, log = check(now, kp, cloud, SITE)
    print(log)
    if alert:
        print("ALERT:", *alert)
        if a.mode == "normal":
            send(topic, *alert)


if __name__ == "__main__":
    main()
