from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    # Relationship with shops
    shops = relationship("Shop", back_populates="owner")

class Shop(Base):
    __tablename__ = "shops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    description = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    website = Column(String, nullable=True)
    opening_hours = Column(String, nullable=True)
    business_category = Column(String, nullable=True)
    address = Column(String, nullable=True)
    
    # Relationship with vendor
    owner = relationship("Vendor", back_populates="shops")