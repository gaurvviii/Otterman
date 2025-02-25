from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

import crud
import models
import schemas
import security
from database import engine, get_db
from config import logger, get_settings

# Get settings
settings = get_settings()

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Vendor Shop Management System",
    description="API for managing vendor shops with geolocation search"
)

# Authentication Routes
@app.post("/register", response_model=schemas.Vendor)
def register_vendor(vendor: schemas.VendorCreate, db: Session = Depends(get_db)):
    try:
        # Check if username or email already exists
        existing_vendor = db.query(models.Vendor).filter(
            (models.Vendor.username == vendor.username) | 
            (models.Vendor.email == vendor.email)
        ).first()
        
        if existing_vendor:
            logger.warning(f"Registration attempt with existing username/email: {vendor.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered"
            )
        
        new_vendor = crud.create_vendor(db=db, vendor=vendor)
        logger.info(f"New vendor registered successfully: {vendor.username}")
        return new_vendor
    except Exception as e:
        logger.error(f"Error during vendor registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    vendor = security.authenticate_vendor(
        db, 
        form_data.username, 
        form_data.password
    )
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = security.create_access_token(
        data={"sub": vendor.username}
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Shop Management Routes
@app.post("/shops", response_model=schemas.Shop)
def create_shop(
    shop: schemas.ShopCreate, 
    db: Session = Depends(get_db), 
    current_vendor = Depends(security.get_current_vendor)
):
    return crud.create_shop(db=db, shop=shop, vendor_id=current_vendor.id)

@app.get("/shops", response_model=List[schemas.Shop])
def read_shops(
    db: Session = Depends(get_db), 
    current_vendor = Depends(security.get_current_vendor)
):
    return crud.get_vendor_shops(db=db, vendor_id=current_vendor.id)

@app.put("/shops/{shop_id}", response_model=schemas.Shop)
def update_shop(
    shop_id: int, 
    shop: schemas.ShopCreate, 
    db: Session = Depends(get_db), 
    current_vendor = Depends(security.get_current_vendor)
):
    updated_shop = crud.update_shop(
        db=db, 
        shop_id=shop_id, 
        shop_data=shop, 
        vendor_id=current_vendor.id
    )
    if not updated_shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    return updated_shop

@app.delete("/shops/{shop_id}")
def delete_shop(
    shop_id: int, 
    db: Session = Depends(get_db), 
    current_vendor = Depends(security.get_current_vendor)
):
    success = crud.delete_shop(
        db=db, 
        shop_id=shop_id, 
        vendor_id=current_vendor.id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Shop not found")
    return {"detail": "Shop deleted successfully"}

# Public Search Route
@app.get("/search", response_model=List[schemas.Shop])
def search_shops(
    latitude: float, 
    longitude: float, 
    radius: float = 5.0, 
    db: Session = Depends(get_db)
):
    return crud.search_nearby_shops(
        db=db, 
        latitude=latitude, 
        longitude=longitude, 
        radius=radius
    )

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)