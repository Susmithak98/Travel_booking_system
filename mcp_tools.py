from mcp.server.fastmcp import FastMCP
import uvicorn

# Create MCP server
mcp = FastMCP("TravelBookingAgent")

@mcp.tool()
def book_flight(from_city: str, to_city: str, date: str) -> dict:
    return {
        "pnr": "FL123",
        "details": f"Flight booked from {from_city} to {to_city} on {date}"
    }

@mcp.tool()
def book_hotel(city: str, check_in: str, check_out: str) -> dict:
    return {
        "reservation_id": "HT456",
        "details": f"Hotel booked in {city} from {check_in} to {check_out}"
    }

@mcp.tool()
def book_cab(pickup: str, drop: str, date: str) -> dict:
    return {
        "cab_id": "CB789",
        "details": f"Cab from {pickup} to {drop} on {date}"
    }

if __name__ == "__main__":
    # ✅ Important: run mcp.asgi_app directly
    uvicorn.run(mcp.asgi_app, host="0.0.0.0", port=8000)
