from contextlib import asynccontextmanager

from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from mcp.server.transport_security import TransportSecuritySettings

from national_mcp import BY_CODE, create_server
from ukraine_main_mcp import server as ukraine_server

SECURITY = TransportSecuritySettings(
    enable_dns_rebinding_protection=True,
    allowed_hosts=[
        "community.ukrdigital.org",
        "127.0.0.1:8903",
        "localhost:8903",
    ],
    allowed_origins=["https://community.ukrdigital.org"],
)

class TerritorialRouter:
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return

        parts = scope.get("path", "").strip("/").split("/")
        if len(parts) == 3 and parts[0] == "mcp":
            parts = parts[1:]

        if len(parts) != 2 or parts[1] != "mcp":
            await PlainTextResponse("Not Found", status_code=404)(
                scope, receive, send
            )
            return

        code = parts[0]

        if code == "ukraine":
            server = ukraine_server
        elif code in BY_CODE:
            server = create_server(code)
        else:
            await PlainTextResponse("Unknown KATOTTG", status_code=404)(
                scope, receive, send
            )
            return

        subapp = server.streamable_http_app(
            streamable_http_path="/mcp",
            stateless_http=True,
            json_response=True,
            transport_security=SECURITY,
        )

        child_scope = dict(scope)
        child_scope["path"] = "/mcp"
        child_scope["root_path"] = ""

        async with subapp.router.lifespan_context(subapp):
            await subapp(child_scope, receive, send)

        return

async def homepage(request):
    return PlainTextResponse(
        f"Ukraine Territorial MCP v3: {len(BY_CODE)} territories"
    )

app = Starlette(routes=[Route("/", homepage)])
app.mount("/mcp", TerritorialRouter())
