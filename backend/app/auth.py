import time
import secrets
from typing import Dict, Tuple

import jwt
from eth_account.messages import encode_defunct
from eth_account import Account

from .config import get_settings

##  AUTH config ##


# nonce lifetime in seconds (5 minutes)
NONCE_TTL = 300

# JWT expiry in seconds (24 hours)
JWT_EXPIRY_SECONDS = 86400

# wallet -> (nonce, created_at)
NONCE_STORE: Dict[str, Tuple[str, int]] = {}

# Message versioning for signature verification
AUTH_MESSAGE_VERSION = "MLSA_AUTH_V1"

## NONCE functions ##


def generate_nonce(wallet: str) -> str:
    wallet = wallet.lower()
    nonce = secrets.token_hex(16)
    NONCE_STORE[wallet] = (nonce, int(time.time()))
    return nonce


def verify_signature(
    wallet: str,
    nonce: str,
    signature: str,
    chain_id: int,
    app_name: str
) -> bool:
    wallet = wallet.lower()

    stored = NONCE_STORE.pop(wallet, None)
    if not stored:
        return False

    stored_nonce, created_at = stored

    # nonce mismatch
    if stored_nonce != nonce:
        return False

    # nonce expired
    if created_at + NONCE_TTL < time.time():
        return False

    message = (
    f"{AUTH_MESSAGE_VERSION}\n"
    f"Sign in to {app_name} with wallet {wallet} "
    f"on chain {chain_id}. Nonce: {nonce}"
    )

    encoded = encode_defunct(text=message)
    try:
        recovered = Account.recover_message(encoded, signature=signature)
    except Exception:
# Any error in signature recovery → authentication fails

        return False
    return recovered.lower() == wallet


def issue_jwt(user_id: str) -> str:
    settings = get_settings()
    now = int(time.time())
    payload = {"sub": user_id, "iat": now, "exp": now + JWT_EXPIRY_SECONDS, "iss": "mlsa-cards-backend", "aud": "mlsa-cards-frontend"}  # 24 hours
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def verify_jwt(token: str) -> dict:
    settings = get_settings()
    payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"], audience="mlsa-cards-frontend", issuer="mlsa-cards-backend")
    return payload
