from servers.community_engagement import get_welcome_data, submit_feedback_data
from mcp.server.mcpserver import MCPServer
from national_mcp import BY_CODE, records, EDITION_DATE, OBLAST_COUNCILS
from territorial_knowledge import get_hierarchy as build_hierarchy
from servers.katottg_search import search_by_name, search_detailed
from servers.territory_types import get_territory_type

BASE_URL = "https://community.ukrdigital.org/mcp"

CATEGORY_NAMES = {
    "O": "Область або Автономна Республіка Крим",
    "P": "Район",
    "H": "Об'єднана територіальна громада",
    "C": "Село",
    "X": "Селище",
    "M": "Місто",
    "B": "Район у місті",
    "K": "Місто зі спеціальним статусом",
}


server = MCPServer(name="ukraine-territorial-mcp")

@server.tool()
def get_catalog_info() -> dict:
    """Інформація про загальноукраїнський каталог територій."""
    categories = {}
    for r in records:
        cat = r["category"]
        categories[cat] = categories.get(cat, 0) + 1
    return {
        "name": "Ukraine Territorial MCP",
        "total": len(records),
        "source": "КАТОТТГ",
        "edition_date": EDITION_DATE,
        "categories": categories,
        "category_descriptions": CATEGORY_NAMES,
    }

@server.tool()
def search_territories(
    query: str,
    limit: int = 20,
    offset: int = 0,
    region_code: str = "",
    district_code: str = "",
    community_code: str = "",
) -> dict:
    """Пошук територій із повними адміністративними адресами,
    фільтрами та пагінацією. Повертає total, offset, limit, results.
    """
    return search_detailed(
        query=query,
        region_code=region_code,
        district_code=district_code,
        community_code=community_code,
        offset=offset,
        limit=limit,
    )

@server.tool()
def get_territory(code: str) -> dict:
    """Отримати територію за кодом КАТОТТГ."""
    territory = BY_CODE.get(code.strip().upper())
    if territory is None:
        return {"error": "Territory not found"}
    return {
        **territory,
        **get_territory_type(territory),
        "category_name": CATEGORY_NAMES.get(territory["category"], "Невідома категорія"),
        "source": {
            "registry": "КАТОТТГ",
            "edition_date": EDITION_DATE,
        },
    }

@server.tool()
def get_hierarchy(code: str) -> dict:
    """Отримати адміністративну ієрархію території."""
    code = code.strip().upper()
    if code not in BY_CODE:
        return {"error": "Territory not found"}
    return {"code": code, "hierarchy": build_hierarchy(code)}

@server.tool()
def list_territories(
    category: str = "",
    region_code: str = "",
    district_code: str = "",
    community_code: str = "",
    offset: int = 0,
    limit: int = 50,
    territory_type: str = "",
) -> dict:
    """Перелік територій із фільтрами та посторінковою видачею."""
    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    results = [
        r for r in records
        if (not territory_type or
            get_territory_type(r)["territory_type"] ==
            territory_type.strip().lower())
        and (not category or r["category"] == category.upper())
        and (not region_code or r.get("region_code") == region_code.upper())
        and (not district_code or r.get("district_code") == district_code.upper())
        and (not community_code or r.get("community_code") == community_code.upper())
    ]
    return {
        "total": len(results),
        "offset": offset,
        "limit": limit,
        "territories": [
            {
                **record,
                **get_territory_type(record),
                "source": {
                    "registry": "КАТОТТГ",
                    "edition_date": EDITION_DATE,
                },
            }
            for record in results[offset:offset + limit]
        ],
    }

@server.tool()
def get_mcp_endpoint(code: str) -> dict:
    """Отримати HTTPS-адресу територіального MCP."""
    code = code.strip().upper()
    if code not in BY_CODE:
        return {"error": "Territory not found"}
    return {
        "code": code,
        "name": BY_CODE[code]["name"],
        **get_territory_type(BY_CODE[code]),
        "url": f"{BASE_URL}/{code}/mcp",
    }



@server.tool()
def list_oblasts() -> dict:
    """Перелік 24 областей України з обласними радами та кодами ЄДРПОУ."""
    oblasts = []

    for katottg, council in OBLAST_COUNCILS.items():
        territory = BY_CODE.get(katottg)

        if territory is None:
            raise ValueError(f"Область відсутня у КАТОТТГ: {katottg}")

        oblasts.append({
            "name": territory["name"],
            "katottg": katottg,
            **get_territory_type(territory),
            "council_name": council["oms_name"],
            "edrpou": council["edrpou"],
            "source": {
                "territory": "КАТОТТГ",
                "council": "ЄДР"
            },
            "source_details": {
                "territory": {
                    "registry": "КАТОТТГ",
                    "edition_date": EDITION_DATE,
                },
                "council": {
                    "registry": "ЄДР",
                    "edition_date": None,
                },
            }
        })

    oblasts.sort(key=lambda r: r["name"])

    return {
        "total": len(oblasts),
        "oblasts": oblasts
    }



@server.tool()
def list_first_level_territories() -> dict:
    """Перелік 27 територій першого рівня: 24 області, АР Крим, Київ і Севастополь."""
    territories = []

    for record in records:
        if record["level"] != 1:
            continue

        code = record["code"]
        council = OBLAST_COUNCILS.get(code)

        territories.append({
            "name": record["name"],
            "katottg": code,
            "category": record["category"],
            "category_name": CATEGORY_NAMES.get(record["category"]),
            **get_territory_type(record),
            "level": record["level"],
            "source": {
                "registry": "КАТОТТГ",
                "edition_date": EDITION_DATE,
            },
            "regional_council": {
                "name": council["oms_name"],
                "edrpou": council["edrpou"],
                "source": "ЄДР"
            } if council else None
        })

    territories.sort(key=lambda x: x["katottg"])

    if len(territories) != 27:
        raise ValueError("Очікувалося 27 територій")

    if sum(x["regional_council"] is not None for x in territories) != 24:
        raise ValueError("Очікувалося 24 обласні ради")

    return {
        "total": len(territories),
        "oblasts": 24,
        "other_first_level_units": 3,
        "territories": territories
    }



@server.tool()
def search_territories_detailed(
    query: str,
    region_code: str = "",
    district_code: str = "",
    community_code: str = "",
    offset: int = 0,
    limit: int = 20,
) -> dict:
    """Пошук територій України з адміністративними назвами,
    фільтрами області, району, громади та посторінковою видачею.
    Використовуй для розрізнення однойменних населених пунктів.
    """
    return search_detailed(
        query=query,
        region_code=region_code,
        district_code=district_code,
        community_code=community_code,
        offset=offset,
        limit=limit,
    )


@server.tool()
def list_special_territories() -> dict:
    """Перелік трьох територій першого рівня з особливим статусом:
    Автономна Республіка Крим, Київ та Севастополь.
    """
    allowed = {"autonomous_republic", "special_status_city"}

    territories = []

    for record in records:
        details = get_territory_type(record)

        if details["territory_type"] not in allowed:
            continue

        territories.append({
            **record,
            **details,
            "source": {
                "registry": "КАТОТТГ",
                "edition_date": EDITION_DATE,
            },
        })

    territories.sort(key=lambda x: x["code"])

    if len(territories) != 3:
        raise ValueError("Очікувалося 3 спеціальні території")

    return {
        "total": len(territories),
        "offset": 0,
        "limit": len(territories),
        "results": territories,
    }


print(f"Ukraine Main MCP ready: {len(records)} territories")


@server.tool()
def get_welcome() -> dict:
    """Привітання, можливості, досягнення та плани MCP України."""
    return get_welcome_data()


def submit_feedback(
    feedback_type: str,
    message: str,
    territory_code: str = "",
    source_url: str = "",
) -> dict:
    """Надіслати зауваження, джерело або ідею для розвитку MCP."""
    return submit_feedback_data(
        feedback_type=feedback_type,
        message=message,
        territory_code=territory_code,
        source_url=source_url,
    )


@server.tool()
def list_datasets() -> dict:
    """Перелік активних і явно опублікованих наборів даних України."""
    from dataset_manager.mcp_tools import list_datasets as get_datasets
    return get_datasets()


@server.tool()
def describe_dataset(dataset_id: str) -> dict:
    """Опис та параметри публічно доступного набору даних."""
    from dataset_manager.mcp_tools import describe_dataset as describe
    return describe(dataset_id)


@server.tool()
def search_district_councils(query: str, region: str = "", limit: int = 20) -> dict:
    """Шукати районні ради України за назвою."""
    from servers.district_councils import search_district_councils as lookup
    return lookup(query=query, region=region, limit=limit)


@server.tool()
def get_district_council(identifier: str) -> dict:
    """Отримати районну раду за ЄДРПОУ або кодом КАТОТТГ району."""
    from servers.district_councils import get_district_council as lookup
    return lookup(identifier)


@server.tool()
def list_district_councils(region: str = "") -> dict:
    """Перелічити райони України та відповідні районні ради."""
    from servers.district_councils import list_district_councils as lookup
    return lookup(region=region)


@server.tool()
def search_local_councils(query: str, limit: int = 20) -> dict:
    """Пошук підтверджених місцевих рад України за назвою, ЄДРПОУ або КАТОТТГ населеного пункту."""
    from servers.local_councils import search_local_councils as lookup
    return lookup(query, limit)


@server.tool()
def get_local_council(identifier: str) -> dict:
    """Отримати місцеву раду за ЄДРПОУ або кодом КАТОТТГ населеного пункту."""
    from servers.local_councils import get_local_council as lookup
    return lookup(identifier)


@server.tool()
def list_local_councils(offset: int = 0, limit: int = 50) -> dict:
    """Список підтверджених місцевих рад України з пагінацією."""
    from servers.local_councils import list_local_councils as lookup
    return lookup(offset, limit)
