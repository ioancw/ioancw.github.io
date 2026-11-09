#!/usr/bin/env python3
"""Fetch a few market numbers into markets/data.json for the markets app.

Runs hourly on weekdays from GitHub Actions; no API keys. Each section is
fetched on its own, and a section that fails keeps its previous values.

  gilts   Bank of England nominal spot curve (daily, published next morning)
  fx      GBP/USD and GBP/EUR, ECB reference rates via Frankfurter (daily)
  ftse    FTSE 100 daily closes: Yahoo Finance, falling back to Stooq
  us10y   US 10-year Treasury yield: FRED, falling back to Yahoo (^TNX)

    python3 .github/fetch_markets.py            # needs: pip install openpyxl
"""
import csv
import io
import json
import sys
import time
import urllib.parse
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
    return {"date": rates[-1][0],
            "pairs": {c: [[day, r[c]] for day, r in rates if c in r] for c in ("USD", "EUR")}}


def yahoo(symbol):
    q = urllib.parse.urlencode({"range": "6mo", "interval": "1d"})
    d = json.loads(get(f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(symbol)}?{q}"))
    r = d["chart"]["result"][0]
    closes = r["indicators"]["quote"][0]["close"]
    series = [[datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d"), round(c, 3)]
              for t, c in zip(r["timestamp"], closes) if c is not None]
    return series[-DAYS:]


def stooq(symbol):
    rows = list(csv.DictReader(io.StringIO(get(f"https://stooq.com/q/d/l/?s={urllib.parse.quote(symbol)}&i=d").decode())))
    series = [[r["Date"], round(float(r["Close"]), 3)] for r in rows if r.get("Close") not in (None, "", "N/D")]
    if not series:
        raise ValueError("Stooq returned no rows")
    return series[-DAYS:]


def fred(series_id):
    start = (date.today() - timedelta(days=DAYS * 2)).isoformat()
    rows = list(csv.reader(io.StringIO(get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}&cosd={start}").decode())))[1:]
    series = [[d, float(v)] for d, v in rows if v not in ("", ".")]
    if not series:
        raise ValueError("FRED returned no rows")
    return series[-DAYS:]


def first_of(*sources):
    """Try each (label, fn) in turn; return the first series that works."""
    errors = []
    for label, fn in sources:
        try:
            series = fn()
            return {"source": label, "date": series[-1][0], "series": series}
        except Exception as e:  # noqa: BLE001 - any failure moves on to the next source
            errors.append(f"{label}: {e}")
    raise RuntimeError("; ".join(errors))


SECTIONS = {
    "gilts": gilts,
    "fx": fx,
    "ftse": lambda: first_of(("Yahoo Finance", lambda: yahoo("^FTSE")), ("Stooq", lambda: stooq("^ukx"))),
    "us10y": lambda: first_of(("FRED", lambda: fred("DGS10")), ("Yahoo Finance", lambda: yahoo("^TNX"))),
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
