from typing import Optional
import random
from datetime import datetime

from fastapi import APIRouter, Header, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..auth import verify_jwt
from ..pinata import pin_json
from ..chain import get_web3
from ..contract import build_safe_mint_tx, get_contract
from ..database import get_db
from ..models import User, OwnedCard, SolvedProblem

router = APIRouter(prefix="/game", tags=["game"])

# Problem bank
PROBLEMS = [
    {"id": 1, "question": "What is 15 + 27?", "answer": "42", "points": 5, "category": "Math"},
    {"id": 2, "question": "What is the capital of France?", "answer": "paris", "points": 3, "category": "Geography"},
    {"id": 3, "question": "What is 8 * 7?", "answer": "56", "points": 5, "category": "Math"},
    {"id": 4, "question": "How many sides does a hexagon have?", "answer": "6", "points": 4, "category": "Math"},
    {"id": 5, "question": "What is the largest planet in our solar system?", "answer": "jupiter", "points": 4, "category": "Science"},
    {"id": 6, "question": "What is 100 - 37?", "answer": "63", "points": 5, "category": "Math"},
    {"id": 7, "question": "What programming language is this backend written in?", "answer": "python", "points": 2, "category": "Tech"},
    {"id": 8, "question": "What is 12 * 12?", "answer": "144", "points": 5, "category": "Math"},
    {"id": 9, "question": "What is the chemical symbol for water?", "answer": "h2o", "points": 3, "category": "Science"},
    {"id": 10, "question": "What is the square root of 64?", "answer": "8", "points": 4, "category": "Math"},
    {"id": 11, "question": "Who wrote Romeo and Juliet?", "answer": "shakespeare", "points": 3, "category": "Literature"},
    {"id": 12, "question": "What is the capital of Japan?", "answer": "tokyo", "points": 3, "category": "Geography"},
    {"id": 13, "question": "What is 25 * 4?", "answer": "100", "points": 4, "category": "Math"},
    {"id": 14, "question": "How many continents are there?", "answer": "7", "points": 3, "category": "Geography"},
    {"id": 15, "question": "What is the chemical symbol for gold?", "answer": "au", "points": 3, "category": "Science"},
    {"id": 16, "question": "What year did World War II end?", "answer": "1945", "points": 4, "category": "History"},
    {"id": 17, "question": "What is 99 / 9?", "answer": "11", "points": 4, "category": "Math"},
    {"id": 18, "question": "What is the smallest prime number?", "answer": "2", "points": 3, "category": "Math"},
    {"id": 19, "question": "What is the speed of light in vacuum (m/s)?", "answer": "300000000", "points": 5, "category": "Physics"},
    {"id": 20, "question": "How many bones are in the human body?", "answer": "206", "points": 4, "category": "Biology"},
    {"id": 21, "question": "What is the capital of Germany?", "answer": "berlin", "points": 3, "category": "Geography"},
    {"id": 22, "question": "What is 17 + 18?", "answer": "35", "points": 3, "category": "Math"},
    {"id": 23, "question": "What element has atomic number 1?", "answer": "hydrogen", "points": 4, "category": "Chemistry"},
    {"id": 24, "question": "How many sides does a pentagon have?", "answer": "5", "points": 2, "category": "Math"},
    {"id": 25, "question": "What is the largest ocean on Earth?", "answer": "pacific", "points": 3, "category": "Geography"},
    {"id": 26, "question": "What is 144 / 12?", "answer": "12", "points": 4, "category": "Math"},
    {"id": 27, "question": "Who invented the telephone?", "answer": "alexander graham bell", "points": 4, "category": "History"},
    {"id": 28, "question": "What is the boiling point of water in Celsius?", "answer": "100", "points": 3, "category": "Physics"},
    {"id": 29, "question": "How many strings does a guitar have?", "answer": "6", "points": 2, "category": "Music"},
    {"id": 30, "question": "What is the capital of Italy?", "answer": "rome", "points": 3, "category": "Geography"},
    {"id": 31, "question": "What does CPU stand for?", "answer": "central processing unit", "points": 4, "category": "Tech"},
    {"id": 32, "question": "What is 2^5?", "answer": "32", "points": 3, "category": "Math"},
    {"id": 33, "question": "Who painted the Mona Lisa?", "answer": "leonardo da vinci", "points": 3, "category": "Art"},
    {"id": 34, "question": "What planet is known as the Red Planet?", "answer": "mars", "points": 3, "category": "Science"},
    {"id": 35, "question": "What language runs in a web browser?", "answer": "javascript", "points": 4, "category": "Tech"},
    {"id": 36, "question": "What is 7! (factorial)?", "answer": "5040", "points": 5, "category": "Math"},
    {"id": 37, "question": "What gas do plants absorb?", "answer": "carbon dioxide", "points": 3, "category": "Biology"},
    {"id": 38, "question": "What is the hardest natural substance?", "answer": "diamond", "points": 3, "category": "Science"},
    {"id": 39, "question": "Who discovered penicillin?", "answer": "alexander fleming", "points": 4, "category": "History"},
    {"id": 40, "question": "What is 3/4 as a decimal?", "answer": "0.75", "points": 3, "category": "Math"},
    {"id": 41, "question": "What protocol secures HTTP?", "answer": "tls", "points": 4, "category": "Tech"},
    {"id": 42, "question": "What is the capital of Canada?", "answer": "ottawa", "points": 3, "category": "Geography"},
    {"id": 43, "question": "What is the tallest mountain on Earth?", "answer": "mount everest", "points": 3, "category": "Geography"},
    {"id": 44, "question": "How many bits are in a byte?", "answer": "8", "points": 2, "category": "Tech"},
    {"id": 45, "question": "What is the freezing point of water in Celsius?", "answer": "0", "points": 2, "category": "Physics"},
    {"id": 46, "question": "What organ pumps blood through the body?", "answer": "heart", "points": 2, "category": "Biology"},
    {"id": 47, "question": "Solve for x: 2x + 6 = 14", "answer": "4", "points": 3, "category": "Math"},
    {"id": 48, "question": "What is the binary representation of 5?", "answer": "101", "points": 3, "category": "Tech"},
    {"id": 49, "question": "Who is known as the father of computers?", "answer": "charles babbage", "points": 4, "category": "History"},
    {"id": 50, "question": "What does DNA stand for?", "answer": "deoxyribonucleic acid", "points": 5, "category": "Biology"},
]

# Store catalog (MLSA-inspired collectibles)
STORE_ITEMS = [
    {
        "id": "aiml",
        "name": "AI/ML Master Card",
        "description": "Master artificial intelligence and machine learning",
        "price": 15,
        "rarity": "Rare",
        "color": "#ffd54f",
        "image": "/images/cards/aiml.png",
    },
    {
        "id": "cloud",
        "name": "Cloud Expert Card",
        "description": "Become a cloud computing expert",
        "price": 12,
        "rarity": "Uncommon",
        "color": "#a5d6a7",
        "image": "/images/cards/cloud.png",
    },
    {
        "id": "web",
        "name": "Web Developer Card",
        "description": "Build modern web applications",
        "price": 10,
        "rarity": "Common",
        "color": "#4fc3f7",
        "image": "/images/cards/web.png",
    },
    {
        "id": "gd",
        "name": "Game Development Card",
        "description": "Create immersive gaming experiences",
        "price": 18,
        "rarity": "Epic",
        "color": "#ffb74d",
        "image": "/images/cards/gd.png",
    },
    {
        "id": "crpr",
        "name": "Competitive Programming Card",
        "description": "Master algorithms and problem solving",
        "price": 20,
        "rarity": "Legendary",
        "color": "#ce93d8",
        "image": "/images/cards/crpr.png",
    },
    {
        "id": "broadcast",
        "name": "Broadcasting & Media Card",
        "description": "Create and share content with the world",
        "price": 14,
        "rarity": "Rare",
        "color": "#ffd54f",
        "image": "/images/cards/broadcast.png",
    },
    {
        "id": "cyber",
        "name": "Cybersecurity Card",
        "description": "Protect systems and secure digital assets",
        "price": 16,
        "rarity": "Epic",
        "color": "#ff6b6b",
        "image": "/images/cards/cyber.png",
    },
    {
        "id": "arvr",
        "name": "AR/VR Developer Card",
        "description": "Build immersive augmented and virtual reality experiences",
        "price": 22,
        "rarity": "Legendary",
        "color": "#ce93d8",
        "image": "/images/cards/arvr.png",
    },
    {
        "id": "app",
        "name": "App Development Card",
        "description": "Develop mobile and desktop applications",
        "price": 13,
        "rarity": "Uncommon",
        "color": "#a5d6a7",
        "image": "/images/cards/app.png",
    },
    {
        "id": "video",
        "name": "Video Production Card",
        "description": "Create professional video content",
        "price": 17,
        "rarity": "Epic",
        "color": "#ffb74d",
        "image": "/images/cards/video.png",
    },
]


class SolveRequest(BaseModel):
    problem_id: int
    answer: str


class PurchaseRequest(BaseModel):
    item_id: str


class MintCardRequest(BaseModel):
    card_id: int  # OwnedCard.id from database


def require_user(authorization: str = Header(None), db: Session = Depends(get_db)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = authorization.split(" ", 1)[1]
    try:
        payload = verify_jwt(token)
        user_id = int(payload.get("sub"))
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc


@router.get("/points")
async def get_points(user: User = Depends(require_user)):
    return {"user_id": user.id, "email": user.email, "points": user.points}

from fastapi import Query

@router.get("/store/items")
async def list_store_items(
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
    limit: int | None = Query(None, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    owned = db.query(OwnedCard).filter(OwnedCard.user_id == user.id).all()
    owned_card_ids = {card.card_id for card in owned}

    items = STORE_ITEMS

    # Apply pagination ONLY if limit is provided
    if limit is not None:
        items = items[offset : offset + limit]

    items_with_ownership = []
    for item in items:
        item_copy = item.copy()
        item_copy["owned"] = item["id"] in owned_card_ids
        items_with_ownership.append(item_copy)

    return {
        "total": len(STORE_ITEMS),
        "limit": limit,
        "offset": offset,
        "items": items_with_ownership,
        "points": user.points,
    }



@router.post("/store/purchase")
async def purchase_item(req: PurchaseRequest, user: User = Depends(require_user), db: Session = Depends(get_db)):
    item = next((i for i in STORE_ITEMS if i["id"] == req.item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if user.points < item["price"]:
        raise HTTPException(status_code=400, detail="Not enough points to purchase")

    user.points -= item["price"]

    # Create owned card
    owned_card = OwnedCard(
        user_id=user.id,
        card_id=item["id"],
        card_name=item["name"],
        card_rarity=item["rarity"],
        card_description=item["description"],
        card_image=item["image"],
        purchase_price=item["price"],
    )
    db.add(owned_card)
    db.commit()
    db.refresh(owned_card)

    return {
        "success": True,
        "item": item,
        "card_id": owned_card.id,
        "remaining_points": user.points,
        "message": f"Purchased {item['name']} for {item['price']} points",
    }


@router.get("/cards")
async def get_owned_cards(user: User = Depends(require_user), db: Session = Depends(get_db)):
    """Get all cards owned by the user"""
    owned_cards = db.query(OwnedCard).filter(OwnedCard.user_id == user.id).all()
    
    return {
        "cards": [
            {
                "id": card.id,
                "card_id": card.card_id,
                "name": card.card_name,
                "rarity": card.card_rarity,
                "description": card.card_description,
                "image": card.card_image,
                "purchased_at": card.purchased_at.isoformat(),
                "is_minted": card.is_minted,
                "token_id": card.token_id,
                "tx_hash": card.tx_hash,
            }
            for card in owned_cards
        ]
    }


@router.get("/problems")
async def get_problems(user: User = Depends(require_user), db: Session = Depends(get_db)):
    """Get a random unsolved problem for the user"""
    solved = db.query(SolvedProblem).filter(SolvedProblem.user_id == user.id).all()
    solved_ids = {sp.problem_id for sp in solved}
    
    # Get unsolved problems
    unsolved = [p for p in PROBLEMS if p["id"] not in solved_ids]
    
    if not unsolved:
        return {
            "problem": None,
            "message": "You've solved all problems! Great job!",
            "total_solved": len(solved_ids),
            "total_problems": len(PROBLEMS)
        }
    
    # Return a random unsolved problem (without the answer)
    problem = random.choice(unsolved)
    return {
        "id": problem["id"],
        "question": problem["question"],
        "points": problem["points"],
        "category": problem["category"],
        "total_solved": len(solved_ids),
        "total_problems": len(PROBLEMS)
    }


@router.post("/solve")
async def solve_problem(req: SolveRequest, user: User = Depends(require_user), db: Session = Depends(get_db)):
    """Submit an answer to a problem"""
    
    # Check if already solved
    already_solved = db.query(SolvedProblem).filter(
        SolvedProblem.user_id == user.id,
        SolvedProblem.problem_id == req.problem_id
    ).first()
    
    if already_solved:
        raise HTTPException(status_code=400, detail="Problem already solved")
    # Find the problem
    problem = next((p for p in PROBLEMS if p["id"] == req.problem_id), None)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    # Check answer (case-insensitive)
    is_correct = req.answer.strip().lower() == problem["answer"].lower()
    
    if is_correct:
        # Award points and mark as solved
        user.points += problem["points"]
        
        solved_problem = SolvedProblem(
            user_id=user.id,
            problem_id=req.problem_id,
            points_earned=problem["points"]
        )
        db.add(solved_problem)
        db.commit()
        
        return {
            "correct": True,
            "points_earned": problem["points"],
            "total_points": user.points,
            "message": f"Correct! You earned {problem['points']} points!"
        }
    else:
        return {
            "correct": False,
            "points_earned": 0,
            "total_points": user.points,
            "message": "Incorrect answer. Try again or get a new problem!"
        }


@router.post("/mint/{card_id}")
async def mint_card(card_id: int, user: User = Depends(require_user), db: Session = Depends(get_db)):
    """Mint an owned card as NFT on blockchain"""
    
    # Check if user has wallet linked
    if not user.wallet_address:
        raise HTTPException(status_code=400, detail="Please link your wallet first to mint NFTs")
    
    # Get the owned card
    owned_card = db.query(OwnedCard).filter(
        OwnedCard.id == card_id,
        OwnedCard.user_id == user.id
    ).first()
    
    if not owned_card:
        raise HTTPException(status_code=404, detail="Card not found or not owned")
    
    if owned_card.is_minted:
        raise HTTPException(status_code=400, detail="Card already minted as NFT")

    metadata = {
        "name": owned_card.card_name,
        "description": owned_card.card_description,
        "image": owned_card.card_image,
        "attributes": [
            {"trait_type": "Rarity", "value": owned_card.card_rarity},
            {"trait_type": "Purchase Price", "value": owned_card.purchase_price},
            {"trait_type": "Collection", "value": "MLSA Cards"}
        ],
    }
    token_uri = await pin_json(metadata)

    w3 = get_web3()
    signed_tx = build_safe_mint_tx(w3, user.wallet_address, token_uri)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    contract = get_contract(w3)
    events = contract.events.Minted().process_receipt(receipt)
    token_id = events[0]["args"]["tokenId"] if events else None

    # Mark card as minted
    owned_card.is_minted = True
    owned_card.token_id = token_id
    owned_card.tx_hash = receipt.transactionHash.hex()
    owned_card.minted_at = datetime.utcnow()
    db.commit()

    return {
        "success": True,
        "transactionHash": receipt.transactionHash.hex(),
        "tokenId": token_id,
        "tokenURI": token_uri,
    }
