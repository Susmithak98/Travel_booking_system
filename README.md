# Travel Booking System · Multi-Agent (LangGraph + MCP)

A **LangGraph Planner Agent** books a complete trip by calling **Model Context Protocol (MCP)** tools for a flight, hotel and cab, then hands the itinerary to a **FastAPI Confirmation Agent**.

**▶ Live demo:** https://susmithak98.github.io/Travel_booking_system/

## Architecture

```
client.py ──► Planner_agent.py  (LangGraph StateGraph[TravelState])

   validate ─► book_flight ─► book_hotel ─► book_cab ─► confirm ─► END
       │            │             │            │           │
       └─ error ────┴─────────────┴────────────┴──► END    │
                    │             │            │           ▼
                    └── MCP over streamable HTTP ──┘   conformation_agent.py
                        mcp_tools.py (:8000/mcp)       FastAPI (:6004/confirm)
```

| File | Role |
|---|---|
| `Planner_agent.py` | Typed `TravelState`, async LangGraph with validation and error routing; calls tools through an MCP `ClientSession` |
| `mcp_tools.py` | FastMCP server with `book_flight`, `book_hotel` and `book_cab` (input validation, booking references, prices) |
| `mcp_server_demo.py` | Starts the MCP server over streamable HTTP |
| `conformation_agent.py` | FastAPI agent with `/confirm` (Pydantic-validated, returns `task_id` and total) and `/health` |
| `client.py` | CLI, either interactive or with `--from/--to/--date/--checkout` |
| `tests/` | 9 pytest tests covering tool contracts, the full graph, bad dates and tool failures |
| `docker-compose.yml` | Runs all three agents as services |
| `index.html` | Interactive browser demo (GitHub Pages) |

## Run locally

```bash
pip install -r requirements.txt

python mcp_server_demo.py        # terminal 1: MCP tools on :8000
python conformation_agent.py     # terminal 2: confirmation agent on :6004
python client.py                 # terminal 3: book a trip
```

Example:

```
✈️  Flight: Flight booked from New York to Los Angeles on 2026-12-01 with Delta (PNR FL2874)
🏨 Hotel:  Hotel booked in Los Angeles from 2026-12-01 to 2026-12-05 (4 nights at Marriott) (ID HT1257)
🚖 Cab:    Cab from Los Angeles Airport to Hotel on 2026-12-01 (ID CB3238)
✅ All bookings confirmed. Total $780 · task f8833bdb-…
```

### With Docker

```bash
docker compose up -d mcp-tools confirmation-agent
docker compose run --rm planner
```

### Offline mode (no servers)

```bash
TRAVEL_TOOLS=local python client.py      # Windows: set TRAVEL_TOOLS=local
```

## Test

```bash
pip install -r requirements-dev.txt
pytest -q
```

## Configuration

| Variable | Default |
|---|---|
| `MCP_URL` | `http://127.0.0.1:8000/mcp` |
| `CONFIRM_URL` | `http://127.0.0.1:6004/confirm` |
| `TRAVEL_TOOLS` | `mcp` (or `local`) |

**Tech:** Python · LangGraph · Model Context Protocol (FastMCP) · FastAPI · Pydantic · httpx · asyncio · Docker Compose

*Contributors: Susmitha Kotharu, NotYeshwanthReddy*
