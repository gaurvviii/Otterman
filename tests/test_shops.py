import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import Base
from models import Vendor
from security import get_password_hash

# Create test database
SQLITE_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLITE_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test database tables
Base.metadata.create_all(bind=engine)

# Test client
client = TestClient(app)

@pytest.fixture
def test_db():
    Base.metadata.create_all(bind=engine)
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_vendor(test_db):
    # Create a test vendor
    vendor_data = {
        "username": "testvendor",
        "email": "test@example.com",
        "password": "testpassword",
        "full_name": "Test Vendor"
    }
    response = client.post("/register", json=vendor_data)
    assert response.status_code == 200
    
    # Get token
    response = client.post(
        "/token",
        data={
            "username": vendor_data["username"],
            "password": vendor_data["password"]
        }
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"token": token}

def test_create_shop(test_vendor):
    shop_data = {
        "name": "Test Shop",
        "description": "Test Description",
        "latitude": 40.7128,
        "longitude": -74.0060
    }
    response = client.post(
        "/shops",
        json=shop_data,
        headers={"Authorization": f"Bearer {test_vendor['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == shop_data["name"]
    assert data["description"] == shop_data["description"]
    assert "id" in data

def test_get_shops(test_vendor):
    # Create a shop first
    shop_data = {
        "name": "Test Shop",
        "description": "Test Description",
        "latitude": 40.7128,
        "longitude": -74.0060
    }
    client.post(
        "/shops",
        json=shop_data,
        headers={"Authorization": f"Bearer {test_vendor['token']}"}
    )
    
    # Get shops
    response = client.get(
        "/shops",
        headers={"Authorization": f"Bearer {test_vendor['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == shop_data["name"]

def test_update_shop(test_vendor):
    # Create a shop first
    shop_data = {
        "name": "Test Shop",
        "description": "Test Description",
        "latitude": 40.7128,
        "longitude": -74.0060
    }
    response = client.post(
        "/shops",
        json=shop_data,
        headers={"Authorization": f"Bearer {test_vendor['token']}"}
    )
    shop_id = response.json()["id"]
    
    # Update shop
    updated_data = {
        "name": "Updated Shop",
        "description": "Updated Description",
        "latitude": 40.7128,
        "longitude": -74.0060
    }
    response = client.put(
        f"/shops/{shop_id}",
        json=updated_data,
        headers={"Authorization": f"Bearer {test_vendor['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == updated_data["name"]
    assert data["description"] == updated_data["description"]

def test_delete_shop(test_vendor):
    # Create a shop first
    shop_data = {
        "name": "Test Shop",
        "description": "Test Description",
        "latitude": 40.7128,
        "longitude": -74.0060
    }
    response = client.post(
        "/shops",
        json=shop_data,
        headers={"Authorization": f"Bearer {test_vendor['token']}"}
    )
    shop_id = response.json()["id"]
    
    # Delete shop
    response = client.delete(
        f"/shops/{shop_id}",
        headers={"Authorization": f"Bearer {test_vendor['token']}"}
    )
    assert response.status_code == 200
    
    # Verify shop is deleted
    response = client.get(
        "/shops",
        headers={"Authorization": f"Bearer {test_vendor['token']}"}
    )
    data = response.json()
    assert len([shop for shop in data if shop["id"] == shop_id]) == 0