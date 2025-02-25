from sqlalchemy.orm import Session
from sqlalchemy import func
from geopy.distance import geodesic

import models
import schemas
import security
from config import logger

def create_vendor(db: Session, vendor: schemas.VendorCreate):
    hashed_password = security.get_password_hash(vendor.password)
    db_vendor = models.Vendor(
        username=vendor.username, 
        email=vendor.email, 
        hashed_password=hashed_password
    )
    db.add(db_vendor)
    db.commit()
    db.refresh(db_vendor)
    return db_vendor

def create_shop(db: Session, shop: schemas.ShopCreate, vendor_id: int):
    try:
        # Validate vendor exists
        vendor = db.query(models.Vendor).filter(models.Vendor.id == vendor_id).first()
        if not vendor:
            logger.error(f"Attempt to create shop for non-existent vendor ID: {vendor_id}")
            raise ValueError("Invalid vendor ID")

        # Create shop with validated data
        shop_data = shop.dict()
        db_shop = models.Shop(**shop_data, vendor_id=vendor_id)
        db.add(db_shop)
        db.commit()
        db.refresh(db_shop)
        logger.info(f"Shop created successfully for vendor {vendor_id}: {shop.name}")
        return db_shop
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating shop: {str(e)}")
        raise

def get_vendor_shops(db: Session, vendor_id: int):
    return db.query(models.Shop).filter(models.Shop.vendor_id == vendor_id).all()

def update_shop(db: Session, shop_id: int, shop_data: schemas.ShopCreate, vendor_id: int):
    db_shop = db.query(models.Shop).filter(
        models.Shop.id == shop_id, 
        models.Shop.vendor_id == vendor_id
    ).first()
    
    if not db_shop:
        return None
    
    for key, value in shop_data.dict().items():
        setattr(db_shop, key, value)
    
    db.commit()
    db.refresh(db_shop)
    return db_shop

def delete_shop(db: Session, shop_id: int, vendor_id: int):
    db_shop = db.query(models.Shop).filter(
        models.Shop.id == shop_id, 
        models.Shop.vendor_id == vendor_id
    ).first()
    
    if not db_shop:
        return False
    
    db.delete(db_shop)
    db.commit()
    return True

def search_nearby_shops(db: Session, latitude: float, longitude: float, radius: float = 5.0):
    shops = db.query(models.Shop).all()
    
    nearby_shops = []
    for shop in shops:
        distance = geodesic(
            (latitude, longitude), 
            (shop.latitude, shop.longitude)
        ).kilometers
        
        if distance <= radius:
            nearby_shops.append(shop)
    
    return nearby_shops