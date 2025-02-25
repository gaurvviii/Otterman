import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import Base

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
def test_shops_data(test_db):
    # Create a vendor
    vendor_data = {
        "username": "testvendor",
        "email": "test@example.com",
        "password": "testpassword",
        "full_name": "Test Vendor"
    }
    response = client.post("/register", json=vendor_data)
    token = client.post(
        "/token",
        data={
            "username": vendor_data["username"],
            "password": vendor_data["password"]
        }
    ).json()["access_token"]
    
    # Create test shops
    shops = [
        {
            "name": "Shop 1",
            "description": "Near Central Park",
            "latitude": 40.7829,
            "longitude": -73.9654
        },
        {
            "name": "Shop 2",
            "description": "Near Times Square",
            "latitude": 40.7580,
            "longitude": -73.9855
        },
        {
            "name": "Shop 3",
            "description": "Far Away Shop",
            "latitude": 41.8781,
            "longitude": -87.6298
        }
    ]
    
    for shop in shops:
        client.post(
            "/shops",
            json=shop,
            headers={"Authorization": f"Bearer {token}"}
        )

def test_search_nearby_shops(test_shops_data):
    # Search near Central Park
    response = client.get(
        "/search",
        params={
            "latitude": 40.7829,
            "longitude": -73.9654,
            "radius": 5.0
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2  # Should find at least 2 shops (Shop 1 and Shop 2)
    assert any(shop["name"] == "Shop 1" for shop in data)
    assert any(shop["name"] == "Shop 2" for shop in data)
    assert not any(shop["name"] == "Shop 3" for shop in data)  # Far away shop should not be found

def test_search_no_shops_found(test_shops_data):
    # Search in a location far from any shops
    response = client.get(
        "/search",
        params={
            "latitude": 51.5074,
            "longitude": -0.1278,  # London coordinates
            "radius": 1.0
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0  # Should find no shops

def test_search_invalid_coordinates(test_shops_data):
    # Test with invalid latitude
    response = client.get(
        "/search",
        params={
            "latitude": 91.0,  # Invalid latitude (>90)
            "longitude": -73.9654,
            "radius": 5.0
        }
    )
    assert response.status_code == 422  # Validation error

    # Test with invalid longitude
    response = client.get(
        "/search",
        params={
            "latitude": 40.7829,
            "longitude": -181.0,  # Invalid longitude (<-180)
            "radius": 5.0
        }
    )
    assert response.status_code == 422  # Validation error