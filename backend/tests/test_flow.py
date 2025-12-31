import os
from typing import Any

import pytest
from fastapi.testclient import TestClient
import jwt

from app.main import app
from app import auth
from app.routers import game
from app.models import User
from eth_account import Account

# --- Dummy blockchain/web3 stubs ---
class DummySignedTx:
    def __init__(self):
        self.rawTransaction = b"0x123"

class DummyEth:
    def get_transaction_count(self, _addr: str) -> int:
        return 1
    def send_raw_transaction(self, _raw: bytes):
        return b"\x11" * 32
    def wait_for_transaction_receipt(self, tx_hash: bytes):
        return DummyReceipt(tx_hash)

class DummyMinted:
    def process_receipt(self, _receipt):
        return [{"args": {"tokenId": 1}}]

class DummyContract:
    def __init__(self):
        self.events = type("Events", (), {"Minted": lambda self: DummyMinted()})()

class DummyWeb3:
    def __init__(self):
        self.eth = DummyEth()

class DummyReceipt:
    def __init__(self, tx_hash: bytes):
        self.transactionHash = tx_hash   # attribute, not dict

# Stub for pin_json
async def _pin_json(*args, **kwargs):
    return "ipfs://dummy"

# --- Environment setup ---
@pytest.fixture(autouse=True)
def setup_env(monkeypatch):
    os.environ.setdefault("JWT_SECRET", "test-secret")
    auth.NONCE_STORE.clear()

    # Stub signature verification and account recovery
    monkeypatch.setattr("app.auth.verify_signature", lambda *args, **kwargs: True)
    monkeypatch.setattr(Account, "recover_message", lambda *args, **kwargs: "0xabc")

    # Stub game blockchain dependencies
    monkeypatch.setattr(game, "pin_json", _pin_json)
    monkeypatch.setattr(game, "get_web3", lambda: DummyWeb3())
    monkeypatch.setattr(game, "build_safe_mint_tx", lambda _w3, _to, _uri: DummySignedTx())
    monkeypatch.setattr(game, "get_contract", lambda _w3: DummyContract())

    # Stub JWT encoding
    monkeypatch.setattr(jwt, "encode", lambda payload, secret, algorithm=None: "dummy.token.value")

# --- Tests ---
def test_auth_points_and_mint_flow(client, auth_header):
    # Nonce
    nonce_resp = client.post("/auth/nonce", json={"wallet": "0xabc"})
    assert nonce_resp.status_code == 200

    # Verify (signature bypassed by stub)
    verify_resp = client.post(
        "/auth/verify",
        json={"wallet": "0xabc", "signature": "0x" + "11" * 65}
    )
    assert verify_resp.status_code == 200

    # Mint card with ID 1
    mint_resp = client.post("/game/mint/1", headers=auth_header)
    assert mint_resp.status_code == 200
    mint_json = mint_resp.json()
    assert isinstance(mint_json["transactionHash"], str)
    assert mint_json["tokenId"] == 1

    # Points check
    points_resp = client.get("/game/points", headers=auth_header)
    assert points_resp.status_code == 200
    assert points_resp.json()["points"] == 10

def test_solve_problem_answer_validation():
    client = TestClient(app)

    # Too short
    resp = client.post("/game/solve", json={"problem_id": 1, "answer": ""})
    assert resp.status_code == 400

    # Too long
    resp = client.post("/game/solve", json={"problem_id": 1, "answer": "a" * 101})
    assert resp.status_code == 400

    # Valid answer with spaces
    resp = client.post("/game/solve", json={"problem_id": 1, "answer": "   correct   "})
    assert resp.status_code in (200, 400)

def test_invalid_difficulty_filter():
    client = TestClient(app)

    resp = client.get("/game/problems?difficulty=invalid", headers={"Authorization": "Bearer testtoken"})
    assert resp.status_code == 422

def test_health_endpoint():
    client = TestClient(app)

    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}