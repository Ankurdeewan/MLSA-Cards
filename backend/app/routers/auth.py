from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from datetime import datetime

from ..auth import generate_nonce, pop_nonce, verify_signature, issue_jwt, verify_jwt
from ..config import get_settings
from ..database import get_db
from ..models import User

router = APIRouter(prefix="/auth", tags=["auth"])

from fastapi.responses import JSONResponse

def error_response(code: str, message: str, status_code: int = 400):
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message
            }
        }
    )

# OAuth configuration
settings = get_settings()

# Initialize OAuth with Starlette config
config = Config(environ={
    'GOOGLE_CLIENT_ID': settings.google_client_id,
    'GOOGLE_CLIENT_SECRET': settings.google_client_secret,
})

oauth = OAuth(config)

oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)


class NonceRequest(BaseModel):
    wallet: str


class VerifyRequest(BaseModel):
    wallet: str
    signature: str


@router.post("/nonce")
async def get_nonce(req: NonceRequest):
    nonce = generate_nonce(req.wallet)
    settings = get_settings()
    message = f"Sign in to {settings.app_name} with wallet {req.wallet.lower()} on chain {settings.chain_id}. Nonce: {nonce}"
    return {"nonce": nonce, "message": message}


@router.post("/verify")
async def verify(req: VerifyRequest, db: Session = Depends(get_db)):
    settings = get_settings()
    nonce = pop_nonce(req.wallet)
    if not nonce:
        raise HTTPException(status_code=400, detail="Nonce not found or expired")

    if not verify_signature(req.wallet, nonce, req.signature, settings.chain_id, settings.app_name):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Find or create user by wallet
    user = db.query(User).filter(User.wallet_address == req.wallet.lower()).first()
    if not user:
        user = User(
            email=f"{req.wallet.lower()}@wallet.local",  # Temporary email for wallet-only users
            wallet_address=req.wallet.lower(),
            name=f"User {req.wallet[:6]}",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.last_login = datetime.utcnow()
        db.commit()

    token = issue_jwt(str(user.id))
    return {"token": token, "user_id": user.id}


@router.get("/google/login")
async def google_login(request: Request):
    redirect_uri = 'http://localhost:8000/auth/google/callback'
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        
        if not user_info:
            raise HTTPException(status_code=400, detail="Failed to get user info")

        email = user_info.get('email')
        name = user_info.get('name')
        picture = user_info.get('picture')

        # Find or create user by email
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                email=email,
                name=name,
                picture=picture,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            user.last_login = datetime.utcnow()
            user.name = name
            user.picture = picture
            db.commit()

        jwt_token = issue_jwt(str(user.id))
        
        # Redirect to home with token in query param (will be stored in localStorage)
        return RedirectResponse(url=f"/home.html?token={jwt_token}")
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth error: {str(e)}")


@router.post("/link-wallet")
async def link_wallet(req: VerifyRequest, token: str, db: Session = Depends(get_db)):
    """Link wallet to existing Google account"""
    try:
        payload = verify_jwt(token)
        user_id = int(payload.get("sub"))
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Verify wallet signature
        settings = get_settings()
        nonce = pop_nonce(req.wallet)
        if not nonce:
            raise HTTPException(status_code=400, detail="Nonce not found or expired")

        if not verify_signature(req.wallet, nonce, req.signature, settings.chain_id, settings.app_name):
            raise HTTPException(status_code=401, detail="Invalid signature")

        # Link wallet to user
        user.wallet_address = req.wallet.lower()
        db.commit()

        return {"success": True, "wallet": user.wallet_address}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

