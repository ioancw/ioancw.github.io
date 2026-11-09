#!/usr/bin/env python3
"""Fetch a few market numbers into markets/data.json for the markets app.

Runs hourly on weekdays from GitHub Actions; no API keys. Each section is
fetched on its own, and a section that fails keeps its previous values.

  gilts   Bank of England nominal spot curve (daily, published next morning)
  fx      GBP/USD, GBP/EUR and EUR/USD, ECB reference rates via Frankfurter (daily)
  us10y   US 10-year Treasury par yield, from the US Treasury's daily curve

    python3 .github/fetch_markets.py            # needs: pip install openpyxl
"""
import csv
import io
import json
import sys
import time
import urllib.request
import zipfile
from datetime import date, datetime, timedelta, timezone

OUT = "markets/data.json"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
DAYS = 120          # history kept for sparklines
BOE_ZIP = "https://www.bankofengland.co.uk/-/media/boe/files/statistics/yield-curves/latest-yield-curve-data.zip"


def get(url, timeout=40):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def gilts():
    """Spot curve for the latest day, the day before, and the first day of the month."""
    import openpyxl
    z = zipfile.ZipFile(io.BytesIO(get(BOE_ZIP)))
    name = next(n for n in z.namelist() if "nominal" in n.lower())
    wb = openpyxl.load_workbook(io.BytesIO(z.read(name)), read_only=True, data_only=True)
    ws = wb[next(s for s in wb.sheetnames if "spot curve" in s.lower())]
    maturities, days = None, []
    for row in ws.iter_rows(values_only=True):
        if isinstance(row[0], str) and row[0].strip().lower().startswith("years"):
            maturities = [float(m) for m in row[1:] if isinstance(m, (int, float))]
        elif isinstance(row[0], (datetime, date)) and maturities:
            vals = [v if isinstance(v, (int, float)) else None for v in row[1:1 + len(maturities)]]
            if sum(v is not None for v in vals) > len(vals) // 2:
                days.append((row[0].strftime("%Y-%m-%d"), [None if v is None else round(v, 3) for v in vals]))
    if not maturities or not days:
        raise ValueError("no spot curve rows found in the BoE workbook")
    out = {"maturities": maturities, "date": days[-1][0], "latest": days[-1][1],
           "month_start_date": days[0][0], "month_start": days[0][1],
           "history": [[d, v[maturities.index(10.0)]] for d, v in days]}
    if len(days) > 1:
        out["prev_date"], out["prev"] = days[-2]
    return out


def fx():
    start = (date.today() - timedelta(days=DAYS)).isoformat()
    d = json.loads(get(f"https://api.frankfurter.dev/v1/{start}..?base=GBP&symbols=USD,EUR"))
    rates = sorted(d["rates"].items())
    pairs = {c: [[day, r[c]] for day, r in rates if c in r] for c in ("USD", "EUR")}
    pairs["EURUSD"] = [[day, round(r["USD"] / r["EUR"], 4)] for day, r in rates if "USD" in r and "EUR" in r]
    return {"date": rates[-1][0], "pairs": pairs}


def us10y():
    """US 10-year par yield from the US Treasury's daily yield curve CSV (newest first)."""
    series = []
    for year in (date.today().year, date.today().year - 1):
        url = ("https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/"
               f"{year}/all?type=daily_treasury_yield_curve&field_tdr_date_value={year}&page&_format=csv")
        for row in csv.DictReader(io.StringIO(get(url).decode("utf-8-sig"))):
            try:
                d = datetime.strptime(row["Date"], "%m/%d/%Y").strftime("%Y-%m-%d")
                series.append([d, float(row["10 Yr"])])
            except (KeyError, ValueError):
                continue
        if len(series) >= DAYS:
            break
    if not series:
        raise ValueError("US Treasury returned no rows")
    series.sort()
    return {"source": "US Treasury", "date": series[-1][0], "series": series[-DAYS:]}


SECTIONS = {
    "gilts": gilts,
    "fx": fx,
    "us10y": us10y,
}


def main():
    try:
        data = json.load(open(OUT))
    except (OSError, ValueError):
        data = {}
    ok = 0
    for name, fn in SECTIONS.items():
        try:
            data[name] = fn()
            data[name]["fetched"] = int(time.time())
            ok += 1
            print(f"{name}: ok, latest {data[name].get('date')}")
        except Exception as e:  # noqa: BLE001 - keep the previous values for this section
            print(f"::warning::{name} failed, keeping previous values: {e}")
    if not ok:
        sys.exit("every source failed; leaving the file as it was")
    data["updated"] = int(time.time())
    with open(OUT, "w") as f:
        json.dump(data, f, separators=(",", ":"))
    print(f"wrote {OUT} ({ok} of {len(SECTIONS)} sections refreshed)")


if __name__ == "__main__":
    main()
