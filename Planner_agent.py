"""Planner Agent: a LangGraph workflow that books a trip by calling MCP tools, then confirms it.

    validate -> book_flight -> book_hotel -> book_cab -> confirm -> END
                    \\___________\\____________\\____ on error -> END

Modes (TRAVEL_TOOLS env var):
    mcp   (default) call tools on the MCP server over streamable HTTP
    local           call the tool functions directly (offline, used by tests)
"""
import json
import os
from datetime import date
from typing import Optional, TypedDict

import httpx
from langgraph.graph import END, StateGraph

MCP_URL = os.getenv("MCP_URL", "http://127.0.0.1:8000/mcp")
CONFIRM_URL = os.getenv("CONFIRM_URL", "http://127.0.0.1:6004/confirm")
TOOLS_MODE = os.getenv("TRAVEL_TOOLS", "mcp")
HTTP_TRANSPORT = None  # tests inject an httpx ASGI transport here


class TravelState(TypedDict, total=False):
    from_city: str
    to_city: str
    date: str
    checkout_date: str
    flight: dict
    hotel: dict
    cab: dict
    confirmation: dict
    error: Optional[str]


async def call_tool(name: str, arguments: dict) -> dict:
    """Call one booking tool, either through MCP or directly."""
    if TOOLS_MODE == "local":
        from mcp_tools import TOOLS
        return TOOLS[name](**arguments)

    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client

    async with streamablehttp_client(MCP_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(name, arguments)
    text = "".join(getattr(c, "text", "") for c in result.content)
    if result.isError:
        raise RuntimeError(text or f"{name} failed")
    if getattr(result, "structuredContent", None):
        data = result.structuredContent
        return data.get("result", data) if isinstance(data, dict) else data
    return json.loads(text)


# ---------- nodes ----------

async def validate(state: TravelState) -> TravelState:
    try:
        start, end = date.fromisoformat(state["date"]), date.fromisoformat(state["checkout_date"])
    except (KeyError, ValueError):
        return {"error": "Dates must be in YYYY-MM-DD format."}
    if not state.get("from_city") or not state.get("to_city"):
        return {"error": "Both cities are required."}
    if end <= start:
        return {"error": "Checkout date must be after the travel date."}
    return {"error": None}


def _booking_node(key: str, tool: str, args_from_state):
    async def node(state: TravelState) -> TravelState:
        try:
            return {key: await call_tool(tool, args_from_state(state))}
        except Exception as exc:
            return {"error": f"{tool} failed: {exc}"}
    node.__name__ = tool
    return node


book_flight = _booking_node("flight", "book_flight",
                            lambda s: {"from_city": s["from_city"], "to_city": s["to_city"], "date": s["date"]})
book_hotel = _booking_node("hotel", "book_hotel",
                           lambda s: {"city": s["to_city"], "check_in": s["date"], "check_out": s["checkout_date"]})
book_cab = _booking_node("cab", "book_cab",
                         lambda s: {"pickup": f"{s['to_city']} Airport", "drop": "Hotel", "date": s["date"]})


async def send_to_confirmation_agent(state: TravelState) -> TravelState:
    try:
        async with httpx.AsyncClient(transport=HTTP_TRANSPORT, timeout=10) as client:
            resp = await client.post(CONFIRM_URL, json={k: state[k] for k in ("flight", "hotel", "cab")})
            resp.raise_for_status()
            return {"confirmation": resp.json()}
    except Exception as exc:
        return {"error": f"Confirmation agent unavailable: {exc}"}


def _next(step: str):
    return lambda state: END if state.get("error") else step


# ---------- graph ----------

graph = StateGraph(TravelState)
graph.add_node("validate", validate)
graph.add_node("book_flight", book_flight)
graph.add_node("book_hotel", book_hotel)
graph.add_node("book_cab", book_cab)
graph.add_node("confirm", send_to_confirmation_agent)
graph.set_entry_point("validate")
graph.add_conditional_edges("validate", _next("book_flight"))
graph.add_conditional_edges("book_flight", _next("book_hotel"))
graph.add_conditional_edges("book_hotel", _next("book_cab"))
graph.add_conditional_edges("book_cab", _next("confirm"))
graph.add_edge("confirm", END)
app = graph.compile()


def new_trip(from_city: str, to_city: str, travel_date: str, checkout: str) -> TravelState:
    return {"from_city": from_city, "to_city": to_city, "date": travel_date, "checkout_date": checkout,
            "flight": {}, "hotel": {}, "cab": {}, "confirmation": {}, "error": None}


if __name__ == "__main__":
    import asyncio
    final = asyncio.run(app.ainvoke(new_trip("New York", "Los Angeles", "2026-12-01", "2026-12-05")))
    print(json.dumps(final, indent=2))
