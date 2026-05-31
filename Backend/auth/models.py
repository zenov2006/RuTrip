from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from database.models import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=True)
    avatar = Column(String, nullable=True)
    is_active = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    verification_code = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    vk_id = Column(String, unique=True, nullable=True)
    telegram_id = Column(String, unique=True, nullable=True)
    yandex_id = Column(String, unique=True, nullable=True)

    visited_subjects = Column(JSON, default=list)
    achievements = Column(JSON, default=list)

    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    expires_at = Column(DateTime, nullable=False)

    user = relationship(
        "User",
        back_populates="refresh_tokens",
    )
class FriendRequest(Base):
    __tablename__ = "friend_requests"

    id = Column(Integer, primary_key=True, index=True)

    from_user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    to_user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    status = Column(String, default="pending", nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    from_user = relationship(
        "User",
        foreign_keys=[from_user_id],
    )

    to_user = relationship(
        "User",
        foreign_keys=[to_user_id],
    )

    __table_args__ = (
        UniqueConstraint(
            "from_user_id",
            "to_user_id",
            name="uq_friend_request_from_to",
        ),
    )


class Friend(Base):
    __tablename__ = "friends"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    friend_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship(
        "User",
        foreign_keys=[user_id],
    )

    friend = relationship(
        "User",
        foreign_keys=[friend_id],
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "friend_id",
            name="uq_friend_user_friend",
        ),
    )