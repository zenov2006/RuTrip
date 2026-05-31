from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from auth.models import User, FriendRequest, Friend
from database.database import get_db
from utils.helpers import build_user_response


router = APIRouter(tags=["users"])


@router.get("/users/search")
async def search_users(
    q: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = q.strip()

    if len(query) < 2:
        return []

    users = (
        db.query(User)
        .filter(
            User.id != current_user.id,
            or_(
                User.name.ilike(f"%{query}%"),
                User.email.ilike(f"%{query}%"),
            ),
        )
        .limit(20)
        .all()
    )

    return [build_user_response(user) for user in users]


@router.post("/users/{user_id}/friend-request")
async def send_friend_request(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя отправить заявку самому себе",
        )

    target_user = db.query(User).filter(User.id == user_id).first()

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    existing_friend = (
        db.query(Friend)
        .filter(
            Friend.user_id == current_user.id,
            Friend.friend_id == user_id,
        )
        .first()
    )

    if existing_friend:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь уже в друзьях",
        )

    existing_request = (
        db.query(FriendRequest)
        .filter(
            or_(
                and_(
                    FriendRequest.from_user_id == current_user.id,
                    FriendRequest.to_user_id == user_id,
                ),
                and_(
                    FriendRequest.from_user_id == user_id,
                    FriendRequest.to_user_id == current_user.id,
                ),
            ),
            FriendRequest.status == "pending",
        )
        .first()
    )

    if existing_request:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Заявка уже существует",
        )

    friend_request = FriendRequest(
        from_user_id=current_user.id,
        to_user_id=user_id,
        status="pending",
    )

    db.add(friend_request)
    db.commit()
    db.refresh(friend_request)

    return {
        "message": "Заявка в друзья отправлена",
        "request_id": friend_request.id,
    }


@router.get("/users/me/friend-requests")
async def get_my_friend_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    incoming_requests = (
        db.query(FriendRequest)
        .filter(
            FriendRequest.to_user_id == current_user.id,
            FriendRequest.status == "pending",
        )
        .all()
    )

    outgoing_requests = (
        db.query(FriendRequest)
        .filter(
            FriendRequest.from_user_id == current_user.id,
            FriendRequest.status == "pending",
        )
        .all()
    )

    return {
        "incoming": [
            {
                "id": request.id,
                "status": request.status,
                "created_at": request.created_at,
                "fromUser": build_user_response(request.from_user),
            }
            for request in incoming_requests
        ],
        "outgoing": [
            {
                "id": request.id,
                "status": request.status,
                "created_at": request.created_at,
                "toUser": build_user_response(request.to_user),
            }
            for request in outgoing_requests
        ],
    }

@router.post("/friend-requests/{request_id}/accept")
async def accept_friend_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    friend_request = (
        db.query(FriendRequest)
        .filter(
            FriendRequest.id == request_id,
            FriendRequest.to_user_id == current_user.id,
            FriendRequest.status == "pending",
        )
        .first()
    )

    if not friend_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена",
        )

    first_friend = Friend(
        user_id=friend_request.from_user_id,
        friend_id=friend_request.to_user_id,
    )

    second_friend = Friend(
        user_id=friend_request.to_user_id,
        friend_id=friend_request.from_user_id,
    )

    friend_request.status = "accepted"

    db.add(first_friend)
    db.add(second_friend)
    db.commit()

    return {
        "message": "Заявка принята",
    }


@router.delete("/friend-requests/{request_id}")
async def delete_friend_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    friend_request = (
        db.query(FriendRequest)
        .filter(
            FriendRequest.id == request_id,
            or_(
                FriendRequest.from_user_id == current_user.id,
                FriendRequest.to_user_id == current_user.id,
            ),
        )
        .first()
    )

    if not friend_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена",
        )

    db.delete(friend_request)
    db.commit()

    return {
        "message": "Заявка удалена",
    }


@router.get("/users/{user_id}/friends")
async def get_user_friends(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    friends = (
        db.query(Friend)
        .filter(Friend.user_id == user_id)
        .all()
    )

    return [
        build_user_response(friend.friend)
        for friend in friends
    ]