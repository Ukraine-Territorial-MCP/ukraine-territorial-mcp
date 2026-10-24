from servers.community_engagement import get_welcome_data, submit_feedback_data
from servers.territory_types import get_territory_type
import json
from pathlib import Path
from mcp.server.mcpserver import MCPServer
from territorial_knowledge import get_hierarchy, search_knowledge

DATA = Path(__file__).resolve().parent / "data/official/ukraine-katottg.json"
catalog = json.loads(DATA.read_text(encoding="utf-8"))
records = catalog["records"]
EDITION_DATE = catalog.get("edition_date")

BY_CODE = {r["code"]: r for r in records}

OBLAST_COUNCILS_FILE = Path(
    str(Path(__file__).resolve().parent / "data/official/edr/katottg-oms-oblast.json")
)
OBLAST_COUNCILS = {
    r["katottg"]: r
    for r in json.loads(
        OBLAST_COUNCILS_FILE.read_text(encoding="utf-8")
    )
}



assert len(BY_CODE) == 31744, "Помилка кількості або дублікати КАТОТТГ"

def create_server(code):
    if code not in BY_CODE:
        raise ValueError(f"Невідомий КАТОТТГ: {code}")

    record = BY_CODE[code]

    server = MCPServer(
        name=f"territorial-{code.lower()}"
    )

    @server.tool()
    def get_identity() -> dict:
        """Офіційна назва, код та тип території."""
        return {
            **record,
            **get_territory_type(record),
            "source": {
                "registry": catalog["source"],
                "edition_date": EDITION_DATE,
            },
        }

    @server.tool()
    def get_basic_profile() -> dict:
        """Базовий адміністративний профіль території."""
        return {
            "name": record["name"],
            "katottg": record["code"],
            "category": record["category"],
            **get_territory_type(record),
            "level": record["level"],
            "region_code": record["region_code"],
            "district_code": record["district_code"],
            "community_code": record["community_code"],
            "settlement_code": record["settlement_code"],
            "source": {
                "registry": catalog["source"],
                "edition_date": EDITION_DATE,
            },
        }

    @server.tool()
    def get_sources() -> dict:
        """Джерело базових адміністративних даних."""
        return {
            "source": "КАТОТТГ",
            "edition_date": EDITION_DATE,
            "record_code": code,
        }


    @server.tool()
    def get_territory_hierarchy() -> dict:
        """Адміністративна ієрархія території від області до поточної одиниці."""
        return {
            "territory_code": code,
            "hierarchy": get_hierarchy(code)
        }

    @server.tool()
    def search_territory_knowledge(query: str = "", limit: int = 20) -> dict:
        """Пошук знань території та всіх її адміністративних предків."""
        return {
            "territory_code": code,
            "query": query,
            "results": search_knowledge(code, query, limit)
        }


    @server.tool()
    def get_regional_council() -> dict:
        """Отримати назву та ЄДРПОУ обласної ради."""
        council = OBLAST_COUNCILS.get(code)

        if council is None:
            return {
                "territory_code": code,
                "regional_council": None,
                "message": "Для цієї території обласну раду не визначено"
            }

        return {
            "region": record["name"],
            "katottg": code,
            "council_name": council["oms_name"],
            "edrpou": council["edrpou"],
            "source": council["source"]
        }


    @server.tool()
    def get_welcome() -> dict:
        """Привітання, можливості та плани MCP цієї території."""
        return get_welcome_data(record)


    def submit_feedback(
        feedback_type: str,
        message: str,
        source_url: str = "",
    ) -> dict:
        """Надіслати відгук, прив'язаний до цієї території."""
        return submit_feedback_data(
            feedback_type=feedback_type,
            message=message,
            territory_code=code,
            source_url=source_url,
        )

    return server

print(f"Національний MCP-рушій: {len(BY_CODE)} територій")
