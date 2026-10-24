import json
import unicodedata
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data/official/district-councils.json"

def load():
    return json.loads(DATA.read_text(encoding="utf-8"))["records"]

def norm(value):
    value = unicodedata.normalize("NFKC", str(value or ""))
    return value.casefold().replace("’", "'").replace("ʼ", "'").strip()

def search_district_councils(query, region="", limit=20):
    q = norm(query)
    reg = norm(region)
    results = []

    for row in load():
        if reg and reg not in norm(row["region"]):
            continue

        council = row["council"]
        searchable = " ".join([
            row["district"],
            council.get("official_name") or "",
            council.get("edrpou") or "",
            row["katottg"]
        ])

        if q in norm(searchable):
            results.append(row)

    return {
        "total": len(results),
        "records": results[:max(1, min(limit, 136))]
    }

def get_district_council(identifier):
    code = norm(identifier)
    matches = [
        row for row in load()
        if code in [
            norm(row["katottg"]),
            norm(row["council"].get("edrpou"))
        ]
    ]
    return matches[0] if matches else {"error": "Районну раду не знайдено"}

def list_district_councils(region=""):
    reg = norm(region)
    records = [
        row for row in load()
        if not reg or reg in norm(row["region"])
    ]
    return {
        "total": len(records),
        "records": records
    }
