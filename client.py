"""Command-line client: collect trip details and run the Planner Agent.

    python client.py
    python client.py --from "New York" --to "Los Angeles" --date 2026-12-01 --checkout 2026-12-05
"""
import argparse
import asyncio
from datetime import date

import Planner_agent


def ask(prompt: str, validator=None) -> str:
    while True:
        value = input(prompt).strip()
        if not value:
            print("   Please enter a value.")
            continue
        if validator:
            try:
                validator(value)
            except ValueError as exc:
                print(f"   {exc}")
                continue
        return value


def iso_date(value: str) -> None:
    try:
        date.fromisoformat(value)
    except ValueError:
        raise ValueError("Use YYYY-MM-DD, for example 2026-12-01.")


def main():
    parser = argparse.ArgumentParser(description="Book a trip with the multi-agent planner")
    parser.add_argument("--from", dest="from_city")
    parser.add_argument("--to", dest="to_city")
    parser.add_argument("--date")
    parser.add_argument("--checkout")
    args = parser.parse_args()

    print("👤 Let's book your travel.")
    from_city = args.from_city or ask("📍 From city:\n> ")
    to_city = args.to_city or ask("🏙️  To city:\n> ")
    travel_date = args.date or ask("📅 Travel date (YYYY-MM-DD):\n> ", iso_date)
    checkout = args.checkout or ask("📅 Checkout date (YYYY-MM-DD):\n> ", iso_date)

    final = asyncio.run(Planner_agent.app.ainvoke(Planner_agent.new_trip(from_city, to_city, travel_date, checkout)))

    if final.get("error"):
        print(f"\n❌ {final['error']}")
        raise SystemExit(1)
    print("\n✈️  Flight:", final["flight"]["details"], f"(PNR {final['flight']['pnr']})")
    print("🏨 Hotel: ", final["hotel"]["details"], f"(ID {final['hotel']['reservation_id']})")
    print("🚖 Cab:   ", final["cab"]["details"], f"(ID {final['cab']['cab_id']})")
    conf = final["confirmation"]
    print(f"\n✅ All bookings confirmed. Total ${conf['result']['total_usd']} · task {conf['task_id']}")


if __name__ == "__main__":
    main()
