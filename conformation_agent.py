"""Confirmation Agent: receives the planner's bookings and confirms the whole itinerary."""
import os
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Travel Confirmation Agent")


class Bookings(BaseModel):
    flight: dict
    hotel: dict
    cab: dict


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/confirm")
def confirm_booking(bookings: Bookings):
    missing = [name for name, item in bookings.model_dump().items() if not item]
    if missing:
        raise HTTPException(status_code=422, detail=f"Missing bookings: {', '.join(missing)}")
    total = sum(item.get("price_usd", 0) for item in bookings.model_dump().values())
    print("✅ Final booking confirmed")
    return {
        "task_id": str(uuid.uuid4()),
        "status": "ok",
        "confirmed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "result": {
            "message": "All bookings confirmed and sent to user interface.",
            "total_usd": total,
            "summary": bookings.model_dump(),
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=os.getenv("CONFIRM_HOST", "127.0.0.1"), port=int(os.getenv("CONFIRM_PORT", "6004")))
