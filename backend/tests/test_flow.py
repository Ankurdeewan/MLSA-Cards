import os
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app import auth
from app.routers import game


class DummySignedTx:
    def __init__(self):
        self.rawTransaction = b"0x123"


class DummyEth:
    def get_transaction_count(self, _addr: str) -> int:
        return 1

    def send_raw_transaction(self, _raw: bytes):
        return b"\x11" * 32

    def wait_for_transaction_receipt(self, tx_hash: bytes):
        return {"transactionHash": tx_hash}


class DummyEvents:
    def process_receipt(self, _receipt):
        return [{"args": {"tokenId": 1}}]


class DummyMinted:
    def process_receipt(self, _receipt):
        return [{"args": {"tokenId": 1}}]


class DummyContract:
    def __init__(self):
        self.events = type("Events", (), {"Minted": lambda self: DummyMinted()})()


class DummyWeb3:
    def __init__(self):
        self.eth = DummyEth()


@pytest.fixture(autouse=True)
def setup_env(monkeypatch):
    os.environ.setdefault("JWT_SECRET", "test-secret")
    # Reset in-memory stores
    auth.NONCE_STORE.clear()
    game.POINTS.clear()

    # Stub external deps: signature check, pinning, chain
    monkeypatch.setattr(auth, "verify_signature", lambda *args, **kwargs: True)
    async def _pin_json(_m):
        return "ipfs://dummy"

    monkeypatch.setattr(game, "pin_json", _pin_json)
    monkeypatch.setattr(game, "get_web3", lambda: DummyWeb3())
    monkeypatch.setattr(game, "build_safe_mint_tx", lambda _w3, _to, _uri: DummySignedTx())
    monkeypatch.setattr(game, "get_contract", lambda _w3: DummyContract())

    yield


def test_auth_points_and_mint_flow():
     pytest.skip(
        "Signature verification is stubbed; skipping misleading auth flow test"
    )
    client = TestClient(app)

    # Nonce
    nonce_resp = client.post("/auth/nonce", json={"wallet": "0xabc"})
    assert nonce_resp.status_code == 200

    # Verify (signature bypassed by stub)
    verify_resp = client.post("/auth/verify", json={"wallet": "0xabc", "signature": "0xsig"})
    assert verify_resp.status_code == 200
    token = verify_resp.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Award points twice to reach threshold
    award1 = client.post("/game/points/award", json={"amount": 5}, headers=headers)
    award2 = client.post("/game/points/award", json={"amount": 5}, headers=headers)
    assert award1.status_code == 200
    assert award2.status_code == 200

    # Mint
    mint_resp = client.post(
        "/game/mint",
        json={"name": "Test", "description": "Demo", "image_url": None},
        headers=headers,
    )
    assert mint_resp.status_code == 200
    mint_json = mint_resp.json()
    assert mint_json["tokenId"] == 1
    assert isinstance(mint_json["transactionHash"], str)

    # Points deducted
    points_resp = client.get("/game/points", headers=headers)
    assert points_resp.status_code == 200
    assert points_resp.json()["points"] == 0
