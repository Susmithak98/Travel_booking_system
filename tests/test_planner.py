import httpx
import pytest

import Planner_agent
from conformation_agent import app as confirm_app


@pytest.fixture(autouse=True)
def local_mode(monkeypatch):
    monkeypatch.setattr(Planner_agent, "TOOLS_MODE", "local")
    monkeypatch.setattr(Planner_agent, "HTTP_TRANSPORT", httpx.ASGITransport(app=confirm_app))
    monkeypatch.setattr(Planner_agent, "CONFIRM_URL", "http://confirm/confirm")


async def test_full_trip_is_booked_and_confirmed():
    final = await Planner_agent.app.ainvoke(Planner_agent.new_trip("New York", "Los Angeles", "2026-12-01", "2026-12-05"))
    assert final["error"] is None
    assert final["flight"]["pnr"].startswith("FL")
    assert final["hotel"]["nights"] == 4
    assert final["cab"]["cab_id"].startswith("CB")
    conf = final["confirmation"]
    assert conf["status"] == "ok"
    assert conf["result"]["total_usd"] == sum(final[k]["price_usd"] for k in ("flight", "hotel", "cab"))


async def test_bad_dates_stop_before_any_booking():
    final = await Planner_agent.app.ainvoke(Planner_agent.new_trip("New York", "Boston", "2026-12-05", "2026-12-01"))
    assert "Checkout date" in final["error"]
    assert final["flight"] == {}


async def test_tool_failure_stops_the_graph():
    final = await Planner_agent.app.ainvoke(Planner_agent.new_trip("Austin", "austin", "2026-12-01", "2026-12-03"))
    assert final["error"].startswith("book_flight failed")
    assert final["hotel"] == {} and final["confirmation"] == {}
