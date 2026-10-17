"""Fetch a bounded snapshot from the official CGU API. Never publish unvalidated payloads.

Requires CGU_API_KEY. Designed for GitHub Actions; does not modify Flask/MySQL.
"""
import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

API="https://api.portaldatransparencia.gov.br/api-de-dados/despesas/por-orgao"
OUT=pathlib.Path("data/expenses.json")
def value(item, *keys):
    for key in keys:
        if item.get(key) is not None:
            try:
                return float(Decimal(str(item[key]).replace(",", ".")))
            except (InvalidOperation, ValueError, TypeError) as exc:
                raise ValueError(
                    f"Invalid numeric field {key}: type={type(item[key]).__name__}; "
                    f"available fields={sorted(str(k) for k in item.keys())}"
                ) from exc
    raise ValueError(f"Missing amount field, expected one of: {keys}")
def normalize(rows, year, code):
    if not isinstance(rows,list) or not rows:
        raise ValueError("Expected a nonempty list from the official API")
    output=[]
    for row in rows:
        if not isinstance(row,dict):
            raise ValueError("Expected object records")
        org=row.get("orgao") or row.get("nomeOrgao") or row.get("nomeOrgaoSuperior")
        if isinstance(org,dict):
            org=org.get("descricao") or org.get("nome")
        if not isinstance(org,str) or not org.strip():
            raise ValueError("Missing organization name; inspect API schema before publishing")
        output.append({"codigo":str(row.get("codigoOrgao") or row.get("codigoOrgaoSuperior") or code),
            "orgao":org.strip(),"ano":year,
            "empenhado":value(row,"valorEmpenhado","empenhado"),
            "liquidado":value(row,"valorLiquidado","liquidado"),
            "pago":value(row,"valorPago","pago")})
    return output
def main():
    key=os.getenv("CGU_API_KEY","").strip()
    year=int(os.getenv("CGU_YEAR","2025"))
    codes=[c.strip() for c in os.getenv("CGU_ORGAOS","26000").split(",") if c.strip()]
    pages=int(os.getenv("CGU_MAX_PAGES","1"))
    if not key:raise ValueError("CGU_API_KEY secret is required")
    if not 2013<=year<=datetime.now(timezone.utc).year:raise ValueError("Invalid CGU_YEAR")
    if not codes or len(codes)>5 or any(not re.fullmatch(r"\d{4,8}",c) for c in codes):raise ValueError("CGU_ORGAOS must contain 1-5 SIAFI numeric codes")
    if not 1<=pages<=3:raise ValueError("CGU_MAX_PAGES must be 1-3")
    records=[]
    for code in codes:
        for page in range(1,pages+1):
            query=urllib.parse.urlencode({"ano":year,"orgaoSuperior":code,"pagina":page})
            req=urllib.request.Request(API+"?"+query,headers={"chave-api-dados":key,"Accept":"application/json","User-Agent":"Breno3B-educational-open-data-dashboard/1.0"})
            try:
                with urllib.request.urlopen(req,timeout=35) as res:
                    payload=json.load(res)
            except urllib.error.HTTPError as exc:
                # Do not log request URLs or response bodies.
                raise RuntimeError(
                    f"CGU API returned HTTP {exc.code} for agency {code}, page {page}; "
                    "previous snapshot preserved"
                ) from exc
            except urllib.error.URLError as exc:
                raise RuntimeError(
                    f"CGU API connection failed ({type(exc.reason).__name__}); "
                    "previous snapshot preserved"
                ) from exc
            if payload==[]:break
            records.extend(normalize(payload,year,code))
    if not records:raise ValueError("No validated records; preserving previous snapshot")
    snapshot={"status":"official","source":API,"generated_at":datetime.now(timezone.utc).isoformat(timespec="seconds"),"scope":f"Selected orgaoSuperior codes {', '.join(codes)}; up to {pages} page(s) per code, not national totals","year":year,"records":records}
    OUT.parent.mkdir(exist_ok=True)
    temp=OUT.with_suffix(".tmp")
    temp.write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    temp.replace(OUT)
    print(f"Validated {len(records)} records; snapshot saved")
if __name__=="__main__":
    try: main()
    except Exception as exc:
        print(f"Snapshot not published: {exc}",file=sys.stderr)
        sys.exit(1)
