"""MCP tool server: exposes flight, hotel and cab booking as Model Context Protocol tools.

The tool functions are plain Python too, so the planner can call them directly in local mode
and the tests can exercise them without a running server.
"""
import os
import random
from datetime import date

from mcp.server.fastmcp import FastMCP

MCP_HOST = os.getenv("MCP_HOST", "127.0.0.1")
MCP_PORT = int(os.getenv("MCP_PORT", "8000"))

mcp = FastMCP("TravelBookingAgent", host=MCP_HOST, port=MCP_PORT)

AIRLINES = ["Delta", "United", "American", "JetBlue", "Alaska"]
HOTELS = ["Hilton", "Marriott", "Hyatt", "Taj", "Holiday Inn"]


class BookingError(ValueError):
    """Raised when a booking request is invalid."""


def _parse(day: str, field: str) -> date:
    try:
        return date.fromisoformat(day)
    except (TypeError, ValueError):
        raise BookingError(f"{field} must be a date in YYYY-MM-DD format, got {day!r}")


def _ref(prefix: str) -> str:
    return f"{prefix}{random.randint(1000, 9999)}"


@mcp.tool()
def book_flight(from_city: str, to_city: str, date: str) -> dict:
    """Book a one-way flight between two cities on a date (YYYY-MM-DD)."""
    if not from_city.strip() or not to_city.strip():
        raise BookingError("from_city and to_city are required")
    if from_city.strip().lower() == to_city.strip().lower():
        raise BookingError("from_city and to_city must be different")
    _parse(date, "date")
    airline = random.choice(AIRLINES)
    return {
        "pnr": _ref("FL"),
        "airline": airline,
        "price_usd": random.randint(129, 489),
        "details": f"Flight booked from {from_city} to {to_city} on {date} with {airline}",
    }


@mcp.tool()
def book_hotel(city: str, check_in: str, check_out: str) -> dict:
    """Book a hotel in a city between check-in and check-out dates (YYYY-MM-DD)."""
    start, end = _parse(check_in, "check_in"), _parse(check_out, "check_out")
    if end <= start:
        raise BookingError("check_out must be after check_in")
    nights = (end - start).days
    hotel = random.choice(HOTELS)
    nightly = random.randint(110, 320)
    return {
        "reservation_id": _ref("HT"),
        "hotel": f"{hotel} {city}",
        "nights": nights,
        "price_usd": nightly * nights,
        "details": f"Hotel booked in {city} from {check_in} to {check_out} ({nights} nights at {hotel})",
    }


@mcp.tool()
def book_cab(pickup: str, drop: str, date: str) -> dict:
    """Book a cab from a pickup point to a drop point on a date (YYYY-MM-DD)."""
    _parse(date, "date")
    return {
        "cab_id": _ref("CB"),
        "price_usd": random.randint(25, 70),
        "details": f"Cab from {pickup} to {drop} on {date}",
    }


TOOLS = {"book_flight": book_flight, "book_hotel": book_hotel, "book_cab": book_cab}
