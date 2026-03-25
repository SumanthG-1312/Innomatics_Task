from fastapi import FastAPI, HTTPException,Query
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

# Q2: Rooms Data
rooms = [
    {"id": 1, "room_number": "101", "type": "Single", "price_per_night": 1000, "floor": 1, "is_available": True},
    {"id": 2, "room_number": "102", "type": "Double", "price_per_night": 1800, "floor": 1, "is_available": False},
    {"id": 3, "room_number": "201", "type": "Suite", "price_per_night": 3000, "floor": 2, "is_available": True},
    {"id": 4, "room_number": "202", "type": "Deluxe", "price_per_night": 2500, "floor": 2, "is_available": True},
    {"id": 5, "room_number": "301", "type": "Single", "price_per_night": 1200, "floor": 3, "is_available": False},
    {"id": 6, "room_number": "302", "type": "Double", "price_per_night": 2000, "floor": 3, "is_available": True},
]

bookings = []
booking_counter = 1


# Q1: Root Endpoint
@app.get("/")
def home():
    return {"message": "Welcome to Grand Stay Hotel"}


# Q2: Get all rooms
@app.get("/rooms")
def get_rooms():
    total = len(rooms)
    available_count = sum(1 for room in rooms if room["is_available"])

    return {
        "rooms": rooms,
        "total": total,
        "available_count": available_count
    }
# Q5: Rooms Summary (IMPORTANT: above /rooms/{room_id})
@app.get("/rooms/summary")
def rooms_summary():
    total = len(rooms)
    available = sum(1 for r in rooms if r["is_available"])
    occupied = total - available

    prices = [r["price_per_night"] for r in rooms]

    # Breakdown by type
    type_breakdown = {}
    for r in rooms:
        room_type = r["type"]
        type_breakdown[room_type] = type_breakdown.get(room_type, 0) + 1

    return {
        "total_rooms": total,
        "available_rooms": available,
        "occupied_rooms": occupied,
        "cheapest_price": min(prices),
        "most_expensive_price": max(prices),
        "room_type_breakdown": type_breakdown
    }

@app.get("/rooms/filter")
def filter_rooms(
    type: Optional[str] = None,
    max_price: Optional[int] = None,
    floor: Optional[int] = None,
    is_available: Optional[bool] = None
):
    result = filter_rooms_logic(type, max_price, floor, is_available)

    return {
        "filtered_rooms": result,
        "count": len(result)
    }

#Q16 :
@app.get("/rooms/search")
def search_rooms(keyword: str):
    keyword_lower = keyword.lower()

    results = [
        r for r in rooms
        if keyword_lower in r["room_number"].lower()
        or keyword_lower in r["type"].lower()
    ]

    if not results:
        return {
            "message": "No rooms found matching your search",
            "total_found": 0,
            "results": []
        }

    return {
        "total_found": len(results),
        "results": results
    }

@app.get("/bookings/active")  # ✅ MUST be ABOVE /bookings/{id} if exists
def active_bookings():
    active = [
        b for b in bookings
        if b["status"] in ["confirmed", "checked_in"]
    ]

    return {
        "active_bookings": active,
        "count": len(active)
    }

#Q17 :
@app.get("/rooms/sort")
def sort_rooms(sort_by: str = "price_per_night", order: str = "asc"):
    valid_fields = ["price_per_night", "floor", "type"]
    valid_orders = ["asc", "desc"]

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"Invalid sort_by. Choose from {valid_fields}")

    if order not in valid_orders:
        raise HTTPException(status_code=400, detail=f"Invalid order. Choose from {valid_orders}")

    reverse = True if order == "desc" else False

    sorted_rooms = sorted(rooms, key=lambda x: x[sort_by], reverse=reverse)

    return {
        "sorted_by": sort_by,
        "order": order,
        "results": sorted_rooms
    }

import math
#Q18 :
@app.get("/rooms/page")
def paginate_rooms(page: int = 1, limit: int = 2):
    total = len(rooms)

    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="Page and limit must be > 0")

    start = (page - 1) * limit
    end = start + limit

    paginated = rooms[start:end]

    total_pages = math.ceil(total / limit)

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "rooms": paginated
    }

@app.get("/rooms/browse")
def browse_rooms(
    keyword: str = None,
    sort_by: str = "price_per_night",
    order: str = "asc",
    page: int = 1,
    limit: int = 3
):
    data = rooms

    # 🔍 Search
    if keyword:
        keyword_lower = keyword.lower()
        data = [
            r for r in data
            if keyword_lower in r["room_number"].lower()
            or keyword_lower in r["type"].lower()
        ]

    # 🔃 Sort
    valid_fields = ["price_per_night", "floor", "type"]
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"Invalid sort_by. Choose from {valid_fields}")

    reverse = True if order == "desc" else False
    data = sorted(data, key=lambda x: x[sort_by], reverse=reverse)

    # 📄 Pagination
    total = len(data)

    start = (page - 1) * limit
    end = start + limit
    paginated = data[start:end]

    total_pages = math.ceil(total / limit)

    return {
        "filters": {
            "keyword": keyword,
            "sort_by": sort_by,
            "order": order,
            "page": page,
            "limit": limit
        },
        "total_results": total,
        "total_pages": total_pages,
        "results": paginated
    }

# Q3: Get room by ID
@app.get("/rooms/{room_id}")
def get_room(room_id: int):
    for room in rooms:
        if room["id"] == room_id:
            return room

    raise HTTPException(status_code=404, detail="Room not found")

# Q4: Get all bookings
@app.get("/bookings")
def get_bookings():
    return {
        "bookings": bookings,
        "total": len(bookings)
    }

@app.get("/bookings/search")
def search_bookings(guest_name: str):
    results = [
        b for b in bookings
        if guest_name.lower() in b["guest_name"].lower()
    ]

    return {
        "total_found": len(results),
        "results": results
    }

@app.get("/bookings/sort")
def sort_bookings(sort_by: str = "total_cost", order: str = "asc"):
    valid_fields = ["total_cost", "nights"]
    valid_orders = ["asc", "desc"]

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"Invalid sort_by. Choose from {valid_fields}")

    if order not in valid_orders:
        raise HTTPException(status_code=400, detail=f"Invalid order. Choose from {valid_orders}")

    reverse = True if order == "desc" else False

    sorted_data = sorted(bookings, key=lambda x: x[sort_by], reverse=reverse)

    return {
        "sorted_by": sort_by,
        "order": order,
        "results": sorted_data
    }

#Q6:
class BookingRequest(BaseModel):
    guest_name: str = Field(..., min_length=2)
    room_id: int = Field(..., gt=0)
    nights: int = Field(..., gt=0, le=30)
    phone: str = Field(..., min_length=10)
    meal_plan: str = "none"
    early_checkout: bool = False

def find_room(room_id: int):
    for room in rooms:
        if room["id"] == room_id:
            return room
    return None

#Q7 :
def calculate_stay_cost(price_per_night: int, nights: int, meal_plan: str, early_checkout: bool):
    base_cost = price_per_night * nights

    # Meal cost
    if meal_plan == "breakfast":
        meal_cost = 500 * nights
    elif meal_plan == "all-inclusive":
        meal_cost = 1200 * nights
    else:
        meal_cost = 0

    total = base_cost + meal_cost

    discount = 0
    if early_checkout:
        discount = 0.10 * total
        total -= discount

    return total, discount

#Q8&Q9:

@app.post("/bookings")
def create_booking(request: BookingRequest):
    global booking_counter

    room = find_room(request.room_id)

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if not room["is_available"]:
        raise HTTPException(status_code=400, detail="Room already occupied")

    # Mark room unavailable
    room["is_available"] = False

    total_cost, discount = calculate_stay_cost(
        room["price_per_night"],
        request.nights,
        request.meal_plan,
        request.early_checkout
    )

    booking = {
        "booking_id": booking_counter,
        "guest_name": request.guest_name,
        "room": room,
        "nights": request.nights,
        "meal_plan": request.meal_plan,
        "early_checkout": request.early_checkout,
        "total_cost": total_cost,
        "discount": discount,
        "status": "confirmed"
    }

    bookings.append(booking)
    booking_counter += 1

    return booking

#Q10:
def filter_rooms_logic(type=None, max_price=None, floor=None, is_available=None):
    filtered = rooms

    if type is not None:
        filtered = [r for r in filtered if r["type"].lower() == type.lower()]

    if max_price is not None:
        filtered = [r for r in filtered if r["price_per_night"] <= max_price]

    if floor is not None:
        filtered = [r for r in filtered if r["floor"] == floor]

    if is_available is not None:
        filtered = [r for r in filtered if r["is_available"] == is_available]

    return filtered

class NewRoom(BaseModel):
    room_number: str = Field(..., min_length=1)
    type: str = Field(..., min_length=2)
    price_per_night: int = Field(..., gt=0)
    floor: int = Field(..., gt=0)
    is_available: bool = True

#Q11:
@app.post("/rooms", status_code=201)
def create_room(room: NewRoom):
    # Check duplicate room number
    for r in rooms:
        if r["room_number"] == room.room_number:
            raise HTTPException(status_code=400, detail="Room number already exists")

    new_room = {
        "id": len(rooms) + 1,
        "room_number": room.room_number,
        "type": room.type,
        "price_per_night": room.price_per_night,
        "floor": room.floor,
        "is_available": room.is_available
    }

    rooms.append(new_room)
    return new_room


#q12 :
@app.put("/rooms/{room_id}")
def update_room(
    room_id: int,
    price_per_night: int = Query(None),
    is_available: bool = Query(None)
):
    room = find_room(room_id)

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if price_per_night is not None:
        room["price_per_night"] = price_per_night

    if is_available is not None:
        room["is_available"] = is_available

    return room

#Q13 :
@app.delete("/rooms/{room_id}")
def delete_room(room_id: int):
    for i, room in enumerate(rooms):
        if room["id"] == room_id:

            if not room["is_available"]:
                raise HTTPException(status_code=400, detail="Cannot delete occupied room")

            deleted_room = rooms.pop(i)

            return {
                "message": "Room deleted successfully",
                "room": deleted_room
            }

    raise HTTPException(status_code=404, detail="Room not found")

#Q14 :
@app.post("/checkin/{booking_id}")
def checkin(booking_id: int):
    for booking in bookings:
        if booking["booking_id"] == booking_id:
            booking["status"] = "checked_in"
            return booking

    raise HTTPException(status_code=404, detail="Booking not found")

#Q15 :
@app.post("/checkout/{booking_id}")
def checkout(booking_id: int):
    for booking in bookings:
        if booking["booking_id"] == booking_id:
            booking["status"] = "checked_out"

            # Free the room
            room = booking["room"]
            room["is_available"] = True

            return booking

    raise HTTPException(status_code=404, detail="Booking not found")

