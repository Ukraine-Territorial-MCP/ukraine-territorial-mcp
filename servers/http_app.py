import json
from contextlib import asynccontextmanager, AsyncExitStack
from pathlib import Path

from starlette.applications import Starlette
from starlette.routing import Mount
from mcp.server.transport_security import TransportSecuritySettings

from servers.community import server as community_server
from servers.village import create_server

BASE = Path(__file__).resolve().parents[1] / "data/official"
data = json.loads(
    (BASE / "ivanivska-mcp0.json").read_text(encoding="utf-8")
)

servers = [("community", community_server)]

for village in data["villages"]:
    servers.append((
        village["katottg"],
        create_server(village["katottg"])
    ))

routes = []
apps = []

for slug, server in servers:
    subapp = server.streamable_http_app(
        streamable_http_path="/mcp",
        stateless_http=True,
        json_response=True,
        transport_security=TransportSecuritySettings(
            enable_dns_rebinding_protection=True,
            allowed_hosts=[
                "community.ukrdigital.org",
                "127.0.0.1:8900",
                "localhost:8900",
            ],
            allowed_origins=[
                "https://community.ukrdigital.org",
            ],
        ),
    )
    routes.append(Mount(f"/mcp/{slug}", app=subapp))
    apps.append(subapp)


@asynccontextmanager
async def lifespan(app):
    async with AsyncExitStack() as stack:
        for subapp in apps:
            await stack.enter_async_context(subapp.router.lifespan_context(subapp))
        yield


app = Starlette(routes=routes, lifespan=lifespan)

print(f"HTTP MCP0: підготовлено {len(servers)} серверів")
