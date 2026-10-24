import json
import sys
from pathlib import Path
from mcp.server.mcpserver import MCPServer

BASE = Path(__file__).resolve().parents[1] / "data/official"

identity_data = json.loads(
    (BASE / "ivanivska-mcp0.json").read_text(encoding="utf-8")
)

geodata = json.loads(
    (BASE / "ivanivska-geodata.json").read_text(encoding="utf-8")
)


def create_server(katottg: str) -> MCPServer:
    village = next(
        (v for v in identity_data["villages"] if v["katottg"] == katottg),
        None
    )

    if village is None:
        raise ValueError(f"Невідомий код КАТОТТГ: {katottg}")

    geo = next(
        (g for g in geodata["villages"] if g["katottg"] == katottg),
        None
    )

    server = MCPServer(
        name=f"village-{katottg.lower()}",
        title=f"Село {village['name']}",
        description=(
            f"MCP0 села {village['name']} Іванівської громади "
            "Чернігівської області. Адміністративні дані КАТОТТГ "
            "та довідкові координати OpenStreetMap."
        ),
        version="0.1.0",
    )

    @server.tool()
    def get_identity() -> dict:
        """Отримати назву, КАТОТТГ та адміністративну належність села."""
        return village

    @server.tool()
    def get_basic_profile() -> dict:
        """Отримати базовий профіль села з координатами OpenStreetMap."""
        return {
            **village,
            "geography": {
                "latitude": geo.get("latitude") if geo else None,
                "longitude": geo.get("longitude") if geo else None,
                "osm_type": geo.get("osm_type") if geo else None,
                "osm_id": geo.get("osm_id") if geo else None,
                "source": "OpenStreetMap / Nominatim",
                "retrieved_at": geodata.get("retrieved_at"),
            },
        }

    @server.tool()
    def get_sources() -> dict:
        """Отримати джерела адміністративних і географічних даних."""
        return {
            "administrative": identity_data["source"],
            "geographic": {
                "name": geodata["source"],
                "retrieved_at": geodata["retrieved_at"],
                "website": "https://www.openstreetmap.org",
            },
        }

    return server


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Використання: python village.py <КАТОТТГ>")

    create_server(sys.argv[1]).run(transport="stdio")
