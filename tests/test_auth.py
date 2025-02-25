import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import Base
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

def test_register_vendor():
    response = client.post(
        "/register",
        json={
            "username": "testvendor",
            "email": "test@example.com",
            "password": "testpassword",
            "full_name": "Test Vendor"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testvendor"
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_register_duplicate_vendor():
    # Register first vendor
    client.post(
        "/register",
        json={
            "username": "testvendor",
            "email": "test@example.com",
            "password": "testpassword",
            "full_name": "Test Vendor"
        }
    )
    
    # Try to register duplicate vendor
    response = client.post(
        "/register",
        json={
            "username": "testvendor",
            "email": "test@example.com",
            "password": "testpassword",
            "full_name": "Test Vendor"
        }
    )
    assert response.status_code == 400

def test_login_success():
    # Register vendor first
    client.post(
        "/register",
        json={
            "username": "testvendor",
            "email": "test@example.com",
            "password": "testpassword",
            "full_name": "Test Vendor"
        }
    )
    
    # Test login
    response = client.post(
        "/token",
        data={
            "username": "testvendor",
            "password": "testpassword"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials():
    response = client.post(
        "/token",
        data={
            "username": "nonexistent",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401