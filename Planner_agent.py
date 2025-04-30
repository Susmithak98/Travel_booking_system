import asyncio
import uuid
from typing import TypedDict
from langgraph.graph import StateGraph, END
from mcp import ClientSession

# Step 1: Define state schema
class TravelState(TypedDict):
    from_city: str
    to_city: str
    date: str
    checkout_date: str
    flight: dict
    hotel: dict
    cab: dict

# Step 2: Define async tool-calling functions using ClientSession

async def book_flight(state: TravelState) -> TravelState:
    async with ClientSession(endpoint="http://localhost:8000/mcp/tool") as session:
        result = await session.call(
            tool="book_flight",
            arguments={
                "from_city": state["from_city"],
                "to_city": state["to_city"],
                "date": state["date"]
            }
        )
        state["flight"] = result
        return state

async def book_hotel(state: TravelState) -> TravelState:
    async with ClientSession(endpoint="http://localhost:8000/mcp/tool") as session:
        result = await session.call(
            tool="book_hotel",
            arguments={
                "city": state["to_city"],
                "check_in": state["date"],
                "check_out": state["checkout_date"]
            }
        )
        state["hotel"] = result
        return state

async def book_cab(state: TravelState) -> TravelState:
    async with ClientSession(endpoint="http://localhost:8000/mcp/tool") as session:
        result = await session.call(
            tool="book_cab",
            arguments={
                "pickup": "Airport",
                "drop": "Hotel",
                "date": state["date"]
            }
        )
        state["cab"] = result
        return state

async def send_to_confirmation_agent(state: TravelState) -> TravelState:
    import httpx
    async with httpx.AsyncClient() as client:
        await client.post("http://localhost:6004/confirm", json={
            "flight": state["flight"],
            "hotel": state["hotel"],
            "cab": state["cab"]
        })
    return state

# Step 3: Build LangGraph with async support
graph = StateGraph(TravelState)

graph.add_node("book_flight", book_flight)
graph.add_node("book_hotel", book_hotel)
graph.add_node("book_cab", book_cab)
graph.add_node("confirm", send_to_confirmation_agent)

graph.set_entry_point("book_flight")
graph.add_edge("book_flight", "book_hotel")
graph.add_edge("book_hotel", "book_cab")
graph.add_edge("book_cab", "confirm")
graph.add_edge("confirm", END)

app = graph.compile()

# Step 4: Run the planner
if __name__ == "__main__":
    user_input: TravelState = {
        "from_city": "New York",
        "to_city": "Los Angeles",
        "date": "2025-05-01",
        "checkout_date": "2025-05-05",
        "flight": {},
        "hotel": {},
        "cab": {}
    }

    final_state = asyncio.run(app.invoke(user_input))

    print("\n✅ Booking complete!")
    print("✈️ ", final_state["flight"]["details"])
    print("🏨", final_state["hotel"]["details"])
    print("🚖", final_state["cab"]["details"])
