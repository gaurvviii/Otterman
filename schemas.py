from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

class VendorBase(BaseModel):
    username: str
    email: EmailStr

class VendorCreate(VendorBase):
    password: str

class Vendor(VendorBase):
    id: int

    class Config:
        from_attributes = True

class ShopBase(BaseModel):
    name: str
    type: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    description: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    opening_hours: Optional[str] = None
    business_category: Optional[str] = None
    address: Optional[str] = None

class ShopCreate(ShopBase):
    pass

class Shop(ShopBase):
    id: int
    vendor_id: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class ShopSearchRequest(BaseModel):
    latitude: float
    longitude: float
    radius: float = 5.0  # Default 5 km