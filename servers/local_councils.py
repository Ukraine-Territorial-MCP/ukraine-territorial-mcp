import json
import unicodedata
from pathlib import Path

DATA = Path(
    str(Path(__file__).resolve().parents[1] / "data/official/edr") + "/"
    "verified-community-councils.json"
)

def load():
    return json.loads(
        DATA.read_text(encoding="utf-8")
    )["records"]

def norm(value):
    value = unicodedata.normalize("NFKC", str(value or ""))
    return (
        value.casefold()
        .replace("’", "'")
        .replace("ʼ", "'")
        .strip()
    )

def search_local_councils(query, limit=20):
    q = norm(query)
    results = []

    for row in load():
        searchable = " ".join([
            row.get("council_name") or "",
            row.get("edrpou") or "",
            row.get("katottg") or ""
        ])

        if q in norm(searchable):
            results.append(row)

    return {
        "total": len(results),
        "records": results[:max(1, min(limit, 100))]
    }

def get_local_council(identifier):
    code = norm(identifier)

    matches = [
        row for row in load()
        if code in (
            norm(row.get("katottg")),
            norm(row.get("edrpou"))
        )
    ]

    return (
        matches[0] if matches
        else {"error": "Місцеву раду не знайдено"}
    )

def list_local_councils(offset=0, limit=50):
    records = load()
    offset = max(0, offset)
    limit = max(1, min(limit, 200))

    return {
        "total": len(records),
        "offset": offset,
        "limit": limit,
        "records": records[offset:offset + limit]
    }
