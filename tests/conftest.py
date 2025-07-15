import uuid
import pytest
from fastapi.testclient import TestClient
from database import SessionLocal, engine, Base
from main import app
from auth import get_current_user
from models import User

from redis_utils import redis_client


# Create a clean test DB schema before tests
@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


# Provide a test DB session
@pytest.fixture()
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Clear Redis before each test
@pytest.fixture(autouse=True)
def clear_redis_cache():
    redis_client.flushdb()


# Simulate logged-in user
@pytest.fixture
def test_user(db_session):
    random_email = f"test+{uuid.uuid4().hex}@example.com"

    user = User(email=random_email, hashed_password="hashed_password")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


# Override get_current_user to always return test_user
@pytest.fixture
def client(test_user):
    def override_get_current_user():
        return test_user

    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
