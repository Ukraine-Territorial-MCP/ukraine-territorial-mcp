# Ukraine Territorial MCP — Installation

## Requirements

- Python 3.12+
- Internet access to install Python packages

## Install

Clone the repository:

```bash
git clone https://github.com/Ukraine-Territorial-MCP/ukraine-territorial-mcp.git
cd ukraine-territorial-mcp
```

Create a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the MCP server

```bash
uvicorn national_http_v3:app --host 127.0.0.1 --port 8903
```

The MCP endpoint will be available at:

```text
http://127.0.0.1:8903/mcp
```

For public access, configure an HTTPS reverse proxy.

## Included data

- 31,744 territorial records from KATOTTG
- 24 oblast councils
- 136 district records
- 1,556 verified local councils

## MCP tools

The server exposes 19 MCP tools for territory search,
administrative hierarchy, council information and datasets.

## Notes

- This repository contains a portable version of the MCP server.
- Runtime feedback databases are not included.
- Data should be periodically refreshed from authoritative sources.
- Verify legal and attribution requirements for each data source.
