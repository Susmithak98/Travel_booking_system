from fastapi import FastAPI, Request
import uuid

app = FastAPI()

@app.post("/confirm")
async def confirm_booking(request: Request):
    data = await request.json()

    print("✅ Final Booking Confirmed:")
    print(data)

    return {
        "task_id": str(uuid.uuid4()),
        "status": "ok",
        "result": {
            "message": "All bookings confirmed and sent to user interface.",
            "summary": data
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=6004)
