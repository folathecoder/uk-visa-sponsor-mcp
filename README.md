# UK Visa Sponsor MCP Server

An MCP server that lets AI assistants search the UK Register of Licensed Visa Sponsors (125,000+ companies). Built with [FastMCP](https://gofastmcp.com).

## Tools

| Tool | Description |
|------|-------------|
| `check_sponsor` | Check if a specific company sponsors UK visas |
| `search_sponsors` | Search sponsors by name, city, county, visa route, or rating |
| `get_sponsor_details` | Get full details for a specific sponsor |
| `get_stats` | Get register statistics (totals, breakdowns, top cities) |

## Setup

### Prerequisites

- Python 3.11+

### Install

```bash
git clone https://github.com/folathecoder/uk-visa-sponsor-mcp.git
cd uk-visa-sponsor-mcp
pip install -e .
```

### Run locally

```bash
fastmcp run server.py
```

### Test with FastMCP Inspector

```bash
fastmcp dev server.py
```

## Usage with AI Tools

### Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "uk-visa-sponsors": {
      "command": "fastmcp",
      "args": ["run", "/absolute/path/to/server.py"]
    }
  }
}
```

### Cursor

Add to `.cursor/mcp.json` in your project:

```json
{
  "mcpServers": {
    "uk-visa-sponsors": {
      "command": "fastmcp",
      "args": ["run", "/absolute/path/to/server.py"]
    }
  }
}
```

### Remote Server (SSE)

```bash
fastmcp run server.py --transport sse --host 0.0.0.0 --port 8000
```

Connect via SSE URL: `http://your-host:8000/sse`

## Deploy with Docker

```bash
docker build -t uk-visa-sponsor-mcp .
docker run -p 8000:8000 uk-visa-sponsor-mcp
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `API_BASE_URL` | `https://uksponsorsearch.co.uk` | Base URL of the UK Visa Sponsor Search API |

## Example Queries

Once connected, you can ask your AI assistant:

- "Does Deloitte sponsor UK visas?"
- "Find skilled worker visa sponsors in Manchester"
- "How many companies sponsor health and care worker visas?"
- "Show me A-rated visa sponsors in London"

## License

MIT
