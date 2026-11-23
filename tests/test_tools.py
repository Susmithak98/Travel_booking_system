import pytest

from mcp_tools import BookingError, book_cab, book_flight, book_hotel


def test_flight_booking_contract():
    r = book_flight("New York", "Los Angeles", "2026-12-01")
    assert r["pnr"].startswith("FL") and "New York" in r["details"]


def test_hotel_counts_nights_and_price():
    r = book_hotel("Los Angeles", "2026-12-01", "2026-12-05")
    assert r["reservation_id"].startswith("HT") and r["nights"] == 4 and r["price_usd"] > 0


def test_cab_booking():
    assert book_cab("LAX", "Hotel", "2026-12-01")["cab_id"].startswith("CB")


@pytest.mark.parametrize("call", [
    lambda: book_flight("Dallas", "dallas", "2026-12-01"),
    lambda: book_flight("Dallas", "Austin", "12/01/2026"),
    lambda: book_hotel("Austin", "2026-12-05", "2026-12-01"),
])
def test_invalid_requests_are_rejected(call):
    with pytest.raises(BookingError):
        call()
