from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from crud import create_user, authenticate_user
from models import RefreshToken
from schemas import LoginRequest, RefreshRequest, UserCreate
from auth import create_access_token, create_refresh_token
from config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from datetime import timedelta
from database import get_db
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


router = APIRouter()

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        if create_user(db, user.email, user.password):
            return {"msg": "User created"}
    except IntegrityError:
        db.rollback()  # always rollback on failed commit
        raise HTTPException(status_code=400, detail="Email already exists")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/login")
def login(user: LoginRequest, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(
        data={"sub": str(db_user.id)},
        expires_delta=timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    )

    expires_at = datetime.utcnow() + timedelta(days=int(REFRESH_TOKEN_EXPIRE_DAYS))

    refresh_token = create_refresh_token(db_user.id, expires_at, db)

    return {"access_token": access_token, "refresh_token": refresh_token.token}

@router.post("/refresh")
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    token = db.query(RefreshToken).filter(RefreshToken.token == data.refresh_token).first()
    if not token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if token.expires_at < datetime.utcnow():
        db.delete(token)
        db.commit()
        raise HTTPException(status_code=401, detail="Refresh token expired")

    access_token = create_access_token({"sub": str(token.user_id)})
    return {"access_token": access_token}

@router.post("/logout")
def logout(data: RefreshRequest, db: Session = Depends(get_db)):
    token = db.query(RefreshToken).filter(RefreshToken.token == data.refresh_token).first()
    if token:
        db.delete(token)
        db.commit()
    return {"detail": "Logged out successfully"}