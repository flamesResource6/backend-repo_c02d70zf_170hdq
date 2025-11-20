import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import SCHEMA_MODELS, Vehicle, Booking, Lead

app = FastAPI(title="Black Label Luxury Rentals API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Black Label Luxury Rentals API running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = os.getenv("DATABASE_NAME") or "❌ Not Set"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
                response["connection_status"] = "Connected"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    return response


# ------------------------- Public Catalog -------------------------

@app.get("/api/vehicles", response_model=List[Vehicle])
def list_vehicles(make: Optional[str] = None, type: Optional[str] = None, drive_mode: Optional[str] = None):
    filters: Dict[str, Any] = {}
    if make:
        filters["make"] = {"$regex": f"^{make}$", "$options": "i"}
    if type:
        filters["type"] = type
    if drive_mode:
        filters["drive_mode"] = drive_mode

    items = get_documents("vehicle", filters)
    # Convert ObjectId to string if present
    for it in items:
        if it.get("_id"):
            it["_id"] = str(it["_id"])  # not in schema response
    # Pydantic will coerce fields
    return items  # type: ignore


@app.get("/api/vehicles/{slug}", response_model=Vehicle)
def get_vehicle(slug: str):
    res = get_documents("vehicle", {"slug": slug}, limit=1)
    if not res:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    it = res[0]
    if it.get("_id"):
        it["_id"] = str(it["_id"])  # remove bson id noise
    return it  # type: ignore


# ------------------------- Lead & Booking -------------------------

class QuotePayload(BaseModel):
    vehicle_slug: Optional[str] = None
    vehicle_id: Optional[str] = None
    drive_mode: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    delivery_location: Optional[str] = None
    occasion: Optional[str] = None
    addons: Optional[List[str]] = None
    utm: Optional[Dict[str, Any]] = None


class QuoteRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    preferred_contact: str = "whatsapp"
    payload: QuotePayload


@app.post("/api/lead", response_model=dict)
async def create_lead(lead: QuoteRequest):
    data = Lead(
        source="web",
        form_type="quote",
        payload={
            **lead.payload.model_dump(),
            "contact": {
                "first_name": lead.first_name,
                "last_name": lead.last_name,
                "email": lead.email,
                "phone": lead.phone,
                "preferred_contact": lead.preferred_contact,
            },
            "received_at": datetime.utcnow().isoformat(),
        },
    )
    _id = create_document("lead", data)
    return {"ok": True, "id": _id}


@app.post("/api/bookings", response_model=dict)
async def submit_booking(booking: Booking):
    # Minimal business rule: require age confirmation for self-drive
    if booking.drive_mode == "self-drive" and not booking.driver_age_confirmed:
        raise HTTPException(status_code=400, detail="Driver age must be confirmed for self-drive")
    _id = create_document("booking", booking)
    return {"ok": True, "id": _id}


# ------------------------- Uploads (mock, local) -------------------------

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    # For prototype: store in /tmp and return a fake URL
    contents = await file.read()
    filename = file.filename or "upload.bin"
    temp_path = f"/tmp/{filename}"
    with open(temp_path, "wb") as f:
        f.write(contents)
    return {"url": f"https://files.local/{filename}"}


# ------------------------- Schema Introspection -------------------------

@app.get("/schema")
def get_schema():
    return {name: model.model_json_schema() for name, model in SCHEMA_MODELS.items()}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
