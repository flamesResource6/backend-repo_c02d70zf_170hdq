"""
Database Schemas for Black Label Luxury Rentals

Each Pydantic model corresponds to a MongoDB collection. The collection name
is the lowercase of the class name (e.g., Vehicle -> "vehicle").
"""
from __future__ import annotations

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Literal


# ------------------------- Core Collections -------------------------

class Vehicle(BaseModel):
    slug: str = Field(..., description="Unique slug: brand-model-year-trim")
    year: int = Field(..., ge=1900, le=2100)
    make: str
    model: str
    trim: Optional[str] = None
    type: Literal["supercar", "suv", "luxury", "sedan", "convertible"]
    drive_mode: Literal["self-drive", "chauffeur", "both"] = "both"
    price_per_day: float = Field(..., ge=0)
    price_per_week: Optional[float] = Field(None, ge=0)
    mileage_limit_per_day: int = Field(..., ge=0)
    overage_fee_per_mile: float = Field(..., ge=0)
    security_deposit: int = Field(..., ge=0, le=10000)
    transmission: Optional[str] = None
    drivetrain: Optional[str] = None
    seats: Optional[int] = Field(None, ge=1, le=9)
    color: Optional[str] = None
    horsepower: Optional[int] = Field(None, ge=0)
    torque: Optional[int] = Field(None, ge=0)
    zero_to_60: Optional[float] = Field(None, ge=0)
    features: List[str] = []
    images: List[HttpUrl] = []
    video_url: Optional[HttpUrl] = None
    tags: List[str] = []  # e.g., nightlife, wedding
    available: bool = True
    availability_notes: Optional[str] = None


class Booking(BaseModel):
    vehicle_id: str = Field(..., description="Reference to vehicle _id as string")
    first_name: str
    last_name: str
    email: str
    phone: str
    preferred_contact: Literal["whatsapp", "phone", "email"] = "whatsapp"
    start_date: str  # ISO date
    end_date: str    # ISO date
    delivery_location: Optional[str] = None
    occasion: Optional[Literal["nightlife", "wedding", "corporate", "weekend", "other"]] = None
    driver_age_confirmed: bool = False
    license_upload_url: Optional[HttpUrl] = None
    insurance_upload_url: Optional[HttpUrl] = None
    selfie_upload_url: Optional[HttpUrl] = None
    drive_mode: Optional[Literal["self-drive", "chauffeur"]] = None
    addons: List[str] = []
    notes: Optional[str] = None
    status: Literal["new", "reviewing", "approved", "declined", "canceled"] = "new"


class Testimonial(BaseModel):
    author_name: str
    location: Optional[str] = None
    quote: str
    rating: Optional[int] = Field(None, ge=1, le=5)
    image_url: Optional[HttpUrl] = None


class Blogpost(BaseModel):
    slug: str
    title: str
    excerpt: Optional[str] = None
    cover_image_url: Optional[HttpUrl] = None
    body: str
    category: Literal["nightlife", "corporate", "weekenders", "spotlight"]
    author: Optional[str] = None
    published_at: Optional[str] = None  # ISO datetime


class Faq(BaseModel):
    question: str
    answer: str
    category: Optional[Literal["policy", "booking", "vehicles", "services"]] = None
    order: Optional[int] = None


class Service(BaseModel):
    slug: str
    title: str
    summary: Optional[str] = None
    body: Optional[str] = None
    hero_image_url: Optional[HttpUrl] = None
    highlights: List[str] = []


class Lead(BaseModel):
    source: Literal["web", "whatsapp", "phone"] = "web"
    form_type: Literal["quote", "contact", "newsletter"] = "quote"
    payload: dict = Field(default_factory=dict)
    status: Literal["new", "contacted", "qualified", "closed"] = "new"


# ------------------------- Helper: schema map -------------------------

SCHEMA_MODELS = {
    "vehicle": Vehicle,
    "booking": Booking,
    "testimonial": Testimonial,
    "blogpost": Blogpost,
    "faq": Faq,
    "service": Service,
    "lead": Lead,
}
