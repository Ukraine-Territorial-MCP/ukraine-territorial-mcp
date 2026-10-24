from servers.territory_types import get_territory_type
import json
import sqlite3
from pathlib import Path

BASE = Path(__file__).resolve().parent
TREE_PATH = BASE / "data/official/ukraine-territory-tree.json"
DB_PATH = BASE / "data/official/territorial-knowledge.db"

with TREE_PATH.open(encoding="utf-8") as f:
    TREE_DATA = json.load(f)

NODES = TREE_DATA["nodes"]

SOURCE_METADATA = {
    "registry": TREE_DATA["source"],
    "edition_date": TREE_DATA["edition_date"],
}

NATIONAL_CODE = "UA"


def get_hierarchy(code):
    if code not in NODES:
        raise ValueError(f"Unknown territory: {code}")

    result = []
    visited = set()

    while code:
        if code in visited:
            raise ValueError("Cycle detected in territory hierarchy")

        visited.add(code)
        node = NODES[code]

        result.append({
            "code": code,
            "name": node["name"],
            "level": node["level"],
            "category": node["category"],
            **get_territory_type({
                "code": code,
                "category": node["category"],
            }),
            "source": SOURCE_METADATA.copy()
        })

        code = node["parent_code"]

    return list(reversed(result))


def search_knowledge(code, query="", limit=20):
    hierarchy = get_hierarchy(code)
    codes = [NATIONAL_CODE] + [x["code"] for x in hierarchy]

    limit = max(1, min(int(limit), 100))
    placeholders = ",".join("?" for _ in codes)

    sql = f"""
        SELECT id, territory_code, title, content,
               source_url, source_type, updated_at
        FROM knowledge
        WHERE territory_code IN ({placeholders})
    """

    params = list(codes)

    if query:
        sql += " AND (title LIKE ? OR content LIKE ?)"
        pattern = f"%{query}%"
        params.extend([pattern, pattern])

    sql += " ORDER BY updated_at DESC, id DESC LIMIT ?"
    params.append(limit)

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        return [dict(row) for row in conn.execute(sql, params)]


if __name__ == "__main__":
    code = "UA74100110090080359"
    print("ІЄРАРХІЯ КОЛИЧІВКИ:")
    for item in get_hierarchy(code):
        print(f"  {item['level']}: {item['name']}")
    print("Знайдено записів:", len(search_knowledge(code)))
    print("KNOWLEDGE MODULE OK")
