import Planner_agent

def get_user_input() -> dict:
    print("👤 Let's book your travel. Please answer the following:")

    from_city = input("📍 From city:\n> ").strip()
    to_city = input("🏙️  To city:\n> ").strip()
    date = input("📅 Travel date (YYYY-MM-DD):\n> ").strip()
    checkout = input("📅 Checkout date (YYYY-MM-DD):\n> ").strip()

    return {
        "from_city": from_city,
        "to_city": to_city,
        "date": date,
        "checkout_date": checkout,
        "flight": {},
        "hotel": {},
        "cab": {}
    }

if __name__ == "__main__":
    try:
        user_state = get_user_input()
        final_state = Planner_agent.app.invoke(user_state)

        print("\n✈️  Flight:", final_state["flight"]["details"])
        print("🏨 Hotel:", final_state["hotel"]["details"])
        print("🚖 Cab:", final_state["cab"]["details"])
        print("\n✅ All bookings completed and confirmed.")

    except Exception as e:
        print(f"❌ Error: {e}")
