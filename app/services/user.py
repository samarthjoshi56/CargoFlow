from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate


def list_users(
    db: Session,
    name: str | None = None,
    skip: int = 0,
    limit: int = 20,
) -> list[User]:
    statement = select(User).order_by(User.id)

    if name:
        search = name.strip()
        if search:
            statement = statement.where(User.name.ilike(f"%{search}%"))

    statement = statement.offset(skip).limit(limit)
    return list(db.scalars(statement).all())


def get_user(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def create_user(db: Session, payload: UserCreate) -> User:
    existing_user = db.scalar(select(User).where(User.email == str(payload.email)))
    if existing_user is not None:
        raise ValueError("A user with this email already exists")

    user = User(
        name=payload.name,
        email=str(payload.email),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
