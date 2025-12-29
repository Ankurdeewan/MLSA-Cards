from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
from sqlalchemy import func

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    picture = Column(String, nullable=True)
    wallet_address = Column(String, unique=True, nullable=True, index=True)
    points = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    owned_cards = relationship("OwnedCard", back_populates="user", cascade="all, delete-orphan")
    solved_problems = relationship("SolvedProblem", back_populates="user", cascade="all, delete-orphan")


class OwnedCard(Base):
    __tablename__ = "owned_cards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    card_id = Column(String, nullable=False)  # e.g., "mlsa_starter"
    card_name = Column(String, nullable=False)
    card_rarity = Column(String, nullable=False)
    card_description = Column(String, nullable=False)
    card_image = Column(String, nullable=False)
    purchase_price = Column(Integer, nullable=False)
    purchased_at = Column(DateTime(timezone=True), server_default=func.now())
    is_minted = Column(Boolean, default=False)
    token_id = Column(Integer, nullable=True)
    tx_hash = Column(String, nullable=True)
    minted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="owned_cards")


class SolvedProblem(Base):
    __tablename__ = "solved_problems"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    problem_id = Column(Integer, nullable=False)
    solved_at = Column(DateTime(timezone=True), server_default=func.now())
    points_earned = Column(Integer, nullable=False)

    # Relationships
    user = relationship("User", back_populates="solved_problems")

