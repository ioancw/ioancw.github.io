// Cloudflare Worker: a tiny relay between the trains app and National Rail's
// Darwin live departure boards (OpenLDBWS). Browsers can't call Darwin
// directly (SOAP, no CORS), and this keeps the token off the public page.
//
//   GET https://<worker>/?from=WNT&to=WAT  ->  {"station": ..., "services": [...]}
//
// Setup: Cloudflare dashboard -> Workers -> Create -> paste this file -> Deploy,
// then Settings -> Variables and Secrets -> add ONE of:
//   RDM_KEY       consumer key for "Live Departure Board" on the Rail Data
//                 Marketplace (raildata.org.uk), where new sign-ups now go.
//                 If that product lists a different endpoint, add it as RDM_BASE.
//   DARWIN_TOKEN  an older OpenLDBWS token from National Rail.

const DARWIN = "https://lite.realtime.nationalrail.co.uk/OpenLDBWS/ldb12.asmx";
const RDM_BASE = "https://api1.raildata.org.uk/1010-live-departure-board-dep1_2/LDBWS/api/20220120/GetDepartureBoard";
const ALLOWED_ORIGINS = ["https://ioancw.github.io"];
const CRS = /^[A-Z]{3}$/;

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") ?? "";
    const cors = {
      "Access-Control-Allow-Origin": ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0],
      "Vary": "Origin",
    };
    const url = new URL(request.url);
    const from = (url.searchParams.get("from") ?? "").toUpperCase();
    const to = (url.searchParams.get("to") ?? "").toUpperCase();
    if (!CRS.test(from) || (to && !CRS.test(to))) {
      return Response.json({ error: "from and to must be 3-letter station codes" }, { status: 400, headers: cors });
    }

    // Rail Data Marketplace: the same Darwin board as JSON.
    if (env.RDM_KEY) {
      const q = new URLSearchParams({ numRows: "10", ...(to ? { filterCrs: to, filterType: "to" } : {}) });
      const r = await fetch(`${env.RDM_BASE || RDM_BASE}/${from}?${q}`, { headers: { "x-apikey": env.RDM_KEY } });
      if (!r.ok) {
        return Response.json({ error: `Rail Data Marketplace returned ${r.status}`, detail: (await r.text()).slice(0, 300) }, { status: 502, headers: cors });
      }
      return Response.json(fromRest(await r.json()), { headers: { ...cors, "Cache-Control": "max-age=30" } });
    }
    if (!env.DARWIN_TOKEN) {
      return Response.json({ error: "relay has no RDM_KEY or DARWIN_TOKEN secret" }, { status: 500, headers: cors });
    }

    const body = `<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
  xmlns:typ="http://thalesgroup.com/RTTI/2013-11-28/Token/types" xmlns:ldb="http://thalesgroup.com/RTTI/2021-11-01/ldb/">
  <soap:Header><typ:AccessToken><typ:TokenValue>${env.DARWIN_TOKEN}</typ:TokenValue></typ:AccessToken></soap:Header>
  <soap:Body><ldb:GetDepartureBoardRequest>
    <ldb:numRows>10</ldb:numRows><ldb:crs>${from}</ldb:crs>
    ${to ? `<ldb:filterCrs>${to}</ldb:filterCrs><ldb:filterType>to</ldb:filterType>` : ""}
  </ldb:GetDepartureBoardRequest></soap:Body>
</soap:Envelope>`;

    const r = await fetch(DARWIN, {
      method: "POST",
      headers: { "Content-Type": "text/xml; charset=utf-8", "SOAPAction": "http://thalesgroup.com/RTTI/2012-01-13/ldb/GetDepartureBoard" },
      body,
    });
    const xml = await r.text();
    if (!r.ok) {
      return Response.json({ error: `Darwin returned ${r.status}`, detail: text(xml, "faultstring") }, { status: 502, headers: cors });
    }
    return Response.json(parseBoard(xml), { headers: { ...cors, "Cache-Control": "max-age=30" } });
  },
};

// Workers have no DOMParser, so read the few fields we need by element name,
// ignoring namespace prefixes (Darwin uses several).
const tag = (name) => new RegExp(`<(?:\\w+:)?${name}\\b[^>]*>([\\s\\S]*?)</(?:\\w+:)?${name}>`, "g");
const all = (xml, name) => [...xml.matchAll(tag(name))].map((m) => m[1]);
const decode = (s) => s.replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&apos;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&");
const text = (xml, name) => {
  const v = all(xml, name)[0];
  return v == null ? null : decode(v).trim();
};

export function parseBoard(xml) {
  const result = all(xml, "GetStationBoardResult")[0] ?? "";
  const services = all(result, "service").map((s) => ({
    std: text(s, "std"),
    etd: text(s, "etd"),
    platform: text(s, "platform"),
    operator: text(s, "operator"),
    destination: all(all(s, "destination")[0] ?? "", "locationName").map((n) => n.trim()).join(" & "),
    cancelled: text(s, "isCancelled") === "true",
    reason: text(s, "cancelReason") ?? text(s, "delayReason"),
  }));
  return {
    station: text(result, "locationName"),
    generated: text(result, "generatedAt"),
    messages: all(result, "message").map((m) => decode(m).replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim()),
    services,
  };
}

// Rail Data Marketplace JSON -> the same shape as parseBoard.
export function fromRest(d) {
  const strip = (m) => String(m?.Value ?? m?.value ?? m ?? "").replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
  return {
    station: d.locationName ?? null,
    generated: d.generatedAt ?? null,
    messages: (d.nrccMessages ?? []).map(strip).filter(Boolean),
    services: (d.trainServices ?? []).map((s) => ({
      std: s.std ?? null,
      etd: s.etd ?? null,
      platform: s.platform ?? null,
      operator: s.operator ?? null,
      destination: (s.destination ?? []).map((l) => l.locationName).join(" & "),
      cancelled: Boolean(s.isCancelled),
      reason: s.cancelReason ?? s.delayReason ?? null,
    })),
  };
}
