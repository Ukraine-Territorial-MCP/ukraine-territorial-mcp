import json
from pathlib import Path
from mcp.server.mcpserver import MCPServer

BASE = Path(__file__).resolve().parents[1] / "data/official"

identity_data = json.loads(
    (BASE / "ivanivska-mcp0.json").read_text(encoding="utf-8")
)

geodata = json.loads(
    (BASE / "ivanivska-geodata.json").read_text(encoding="utf-8")
)

server = MCPServer(
    name="ivanivska-community",
    title="Іванівська територіальна громада",
    description=(
        "Офіційні адміністративні та довідкові географічні "
        "дані Іванівської громади Чернігівської області."
    ),
    version="0.1.0",
)

@server.tool()
def get_identity() -> dict:
    """Повернути офіційну назву, код КАТОТТГ, область і район громади."""
    return identity_data["community"]

@server.tool()
def list_villages() -> list[dict]:
    """Перелічити всі 17 сіл громади з кодами КАТОТТГ і координатами OSM."""
    geo_by_code = {
        item["katottg"]: item
        for item in geodata["villages"]
    }

    result = []
    for village in identity_data["villages"]:
        geo = geo_by_code.get(village["katottg"], {})
        result.append({
            "name": village["name"],
            "katottg": village["katottg"],
            "latitude": geo.get("latitude"),
            "longitude": geo.get("longitude"),
            "coordinate_source": geo.get("source"),
        })
    return result

@server.tool()
def get_sources() -> dict:
    """Повернути джерела та дати актуальності адміністративних і географічних даних."""
    return {
        "administrative": identity_data["source"],
        "geographic": {
            "name": geodata["source"],
            "retrieved_at": geodata["retrieved_at"],
            "website": "https://www.openstreetmap.org",
        },
    }


@server.tool()
def search_katottg(query: str, limit: int = 20) -> list[dict]:
    """Пошук адміністративних одиниць України за українською назвою."""
    from servers.katottg_search import search_by_name
    return search_by_name(query, limit)


@server.tool()
def get_katottg_record(code: str) -> dict:
    """Отримати адміністративну одиницю за кодом КАТОТТГ."""
    from servers.katottg_search import find_by_code
    return find_by_code(code) or {"error": "Код не знайдено"}


@server.tool()
def get_katottg_children(code: str) -> list[dict]:
    """Отримати безпосередні дочірні адміністративні одиниці."""
    from servers.katottg_search import get_children
    return get_children(code)



@server.tool()
def search_katottg_by_location(
    query: str,
    region: str = "",
    district: str = "",
    limit: int = 20,
) -> list[dict]:
    """Пошук громад і населених пунктів України за назвою, областю та районом.

    Підтримує українські й англійські назви, зокрема
    Ivanivska Community, Іванівська ОТГ, Kolychivka.
    """
    from servers.katottg_search import search_by_location
    return search_by_location(
        query,
        region=region,
        district=district,
        limit=limit,
    )



@server.tool()
def find_community_settlements(
    query: str,
    region: str = "",
    district: str = "",
) -> dict:
    """Знайти територіальну громаду України та всі її населені пункти.

    Підтримує українські й англійські назви:
    Іванівська ОТГ, Ivanivska Community.

    Для однойменних громад можна уточнити область і район.
    Якщо уточнень недостатньо, повертає список громад
    замість випадкового вибору.
    """
    from servers.katottg_search import (
        find_community_settlements as lookup
    )
    return lookup(
        query,
        region=region,
        district=district,
    )



@server.tool()
def search_community_natural(query: str) -> dict:
    """Знайти громаду України та її населені пункти за звичайним реченням.

    Приклади:
    - Покажи всі села Іванівської громади Чернігівського району
    - Іванівська громада Чернігівський район
    - Ivanivska Community Chernihivskyi District

    Якщо назва неоднозначна, повертає варіанти для уточнення.
    """
    from servers.natural_search import search_community_in_text
    return search_community_in_text(query)


@server.tool()
def find_settlement_parent(
    name: str,
    region: str = "",
    district: str = "",
) -> dict:
    """Визначити громаду, район і область населеного пункту України.

    Підтримує українські та англійські назви.
    Приклади: Количівка, Kolychivka, Ягідне, Ivanivka.

    Якщо існують однойменні населені пункти, повертає всі
    відповідні варіанти з кодами КАТОТТГ для уточнення.

    Параметри region і district дозволяють уточнити пошук.
    """
    from servers.settlement_parent import (
        find_settlement_parent as lookup
    )
    return lookup(
        name,
        region=region,
        district=district,
    )



@server.tool()
def count_settlements(
    level: str = "ukraine",
    name: str = "",
    code: str = "",
    region: str = "",
    district: str = "",
) -> dict:
    """Порахувати міста, селища та села України за даними КАТОТТГ.

    Рівні: ukraine, region, district, community.

    Приклади:
    - Скільки сіл в Україні?
    - Скільки міст у Чернігівській області?
    - Скільки селищ у Чернігівському районі?
    - Скільки сіл в Іванівській громаді?

    Повертає кількість міст, селищ, сіл та загальну кількість.
    Для уточнення однойменних територій використовуйте
    region, district або офіційний код КАТОТТГ.
    """
    from servers.settlement_counts import count_settlements as lookup
    return lookup(
        level=level,
        name=name,
        code=code,
        region=region,
        district=district,
    )


@server.tool()
def list_communities(
    region: str = "",
    district: str = "",
    region_code: str = "",
    district_code: str = "",
) -> dict:
    """Отримати перелік територіальних громад України з кодами КАТОТТГ.

    Дозволяє знайти всі громади певної області або району.

    Приклади запитів:
    - Покажи всі громади Чернігівської області.
    - Які громади входять до Чернігівського району?
    - Назви всі громади району та їхні коди КАТОТТГ.

    Параметри:
    - region: назва області, наприклад Чернігівська.
    - district: назва району, наприклад Чернігівський.
    - region_code: код КАТОТТГ області.
    - district_code: код КАТОТТГ району.

    Для однойменних районів уточнюйте область.
    Повертає кількість громад та повний перелік із кодами.
    """
    from servers.community_listing import list_communities as lookup

    return lookup(
        region=region,
        district=district,
        region_code=region_code,
        district_code=district_code,
    )


@server.tool()
def search_district_councils(
    query: str,
    region: str = "",
    limit: int = 20,
) -> dict:
    """Знайти районні ради України за назвою, областю або ЄДРПОУ."""
    from servers.district_councils import search_district_councils as lookup
    return lookup(query, region=region, limit=limit)


@server.tool()
def get_district_council(identifier: str) -> dict:
    """Отримати районну раду за ЄДРПОУ або кодом КАТОТТГ району."""
    from servers.district_councils import get_district_council as lookup
    return lookup(identifier)


@server.tool()
def list_district_councils(region: str = "") -> dict:
    """Перелічити райони України та відповідні районні ради.

    Повертає також райони, для яких рада ще не ідентифікована.
    """
    from servers.district_councils import list_district_councils as lookup
    return lookup(region=region)


if __name__ == "__main__":
    server.run(transport="stdio")
