import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import User, OwnedCard
from app.database import SessionLocal
import app.auth as auth
from fastapi.security import HTTPBearer
import jwt

# --- Fake overrides ---
def fake_require_user():
    return User(
        id=1,
        email="test@example.com",
        wallet_address="0xabc",
        points=10
    )

def fake_httpbearer():
    class DummyCreds:
        credentials = "testtoken"
    return DummyCreds()

def fake_get_user_from_token(token: str, db):
    # Always return the same dummy user
    return User(
        id=1,
        email="test@example.com",
        wallet_address="0xabc",
        points=10
    )

# Apply overrides globally
app.dependency_overrides[auth.require_user] = fake_require_user
app.dependency_overrides[auth.security] = fake_httpbearer
app.dependency_overrides[HTTPBearer] = fake_httpbearer

# Patch get_user_from_token directly
auth.get_user_from_token = fake_get_user_from_token

# Patch jwt.decode so any token is accepted
jwt.decode = lambda token, secret, algorithms=None: {"sub": "test@example.com"}

# --- Fixtures ---
@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_header():
    return {"Authorization": "Bearer testtoken"}

@pytest.fixture(autouse=True)
def setup_owned_card():
    """Ensure a dummy OwnedCard exists for user id=1 before each test."""
    db = SessionLocal()
    card = OwnedCard(
        id=1,
        user_id=1,
        card_id=1,
        card_name="Test",
        card_description="Demo",
        card_image="http://example.com/image.png",
        card_rarity="Common",
        purchase_price=0,
        is_minted=False
    )
    db.merge(card)
    db.commit()
    db.close()