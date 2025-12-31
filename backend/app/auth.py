import time
import secrets
from typing import Dict

import jwt
from eth_account.messages import encode_defunct
from eth_account import Account

from .config import get_settings

NONCE_STORE: Dict[str, str] = {}

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def require_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    # For now, just accept any token and return a dummy user
    return {"id": 1, "email": "test@example.com"}

def generate_nonce(wallet: str) -> str:
    nonce = secrets.token_hex(16)
    NONCE_STORE[wallet.lower()] = nonce
    return nonce


def pop_nonce(wallet: str) -> str:
    return NONCE_STORE.pop(wallet.lower(), "")


def verify_signature(wallet: str, nonce: str, signature: str, chain_id: int, app_name: str) -> bool:
    message = f"Sign in to {app_name} with wallet {wallet.lower()} on chain {chain_id}. Nonce: {nonce}"
    encoded = encode_defunct(text=message)
    recovered = Account.recover_message(encoded, signature=signature)
    return recovered.lower() == wallet.lower()


def issue_jwt(user_id: str) -> str:
    settings = get_settings()
    now = int(time.time())
    payload = {"sub": user_id, "iat": now, "exp": now + 86400}  # 24 hours
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def verify_jwt(token: str) -> dict:
    settings = get_settings()
    payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    return payload
