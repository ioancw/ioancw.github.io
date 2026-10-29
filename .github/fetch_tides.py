#!/usr/bin/env python3
"""Fetch ADMIRALTY (UKHO) high and low tides for Mumbles into tides/tides.json.

Runs daily from GitHub Actions with the ADMIRALTY_API_KEY secret (the free
"UK Tidal API - Discovery" subscription, which gives 7 days ahead). The tides
page uses these official times and falls back to Open-Meteo's model when the
file is missing or out of date.

    ADMIRALTY_API_KEY=... python3 .github/fetch_tides.py
    python3 .github/fetch_tides.py --events-file saved.json   # for testing
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone

API = "https://admiraltyapi.azure-api.net/uktidalapi/api/V1"
STATIONS = ["Mumbles", "Swansea"]   # the first one UKHO lists is used
OUT = "tides/tides.json"


def get(path, key):
    req = urllib.request.Request(API + path, headers={"Ocp-Apim-Subscription-Key": key})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def find_station(key):
    for name in STATIONS:
        found = get("/Stations?" + urllib.parse.urlencode({"name": name}), key)
        for f in found.get("features", []):
            p = f.get("properties", {})
            if p.get("Name", "").lower().startswith(name.lower()):
                return p["Id"], p["Name"]
    sys.exit(f"None of {STATIONS} is in the UKHO station list.")


def parse_events(raw):
    """UKHO TidalEvents (times in UTC) -> [{t: unix seconds, h: metres above chart datum, high}]."""
    out = []
    for e in raw:
        if e.get("Height") is None or e.get("IsDateTime") is False:
            continue
        t = datetime.fromisoformat(e["DateTime"].rstrip("Z")).replace(tzinfo=timezone.utc)
        out.append({"t": int(t.timestamp()), "h": round(float(e["Height"]), 2), "high": e["EventType"] == "HighWater"})
    return sorted(out, key=lambda x: x["t"])


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--events-file", help="saved TidalEvents JSON, for testing")
    a = p.parse_args()

    if a.events_file:
        station, raw = "Mumbles", json.load(open(a.events_file))
    else:
        key = os.environ.get("ADMIRALTY_API_KEY", "").strip()
        if not key:
            print("::warning::ADMIRALTY_API_KEY is not set, so the tides app keeps using Open-Meteo.")
            return
        sid, station = find_station(key)
        raw = get(f"/Stations/{sid}/TidalEvents?duration=7", key)

    events = parse_events(raw)
    if len(events) < 4:
        sys.exit(f"Only {len(events)} tidal events returned; leaving {OUT} as it was.")
    with open(OUT, "w") as f:
        json.dump({"station": station, "fetched": int(datetime.now(timezone.utc).timestamp()), "events": events}, f, indent=1)
    print(f"wrote {len(events)} events for {station} to {OUT}")


if __name__ == "__main__":
    main()
