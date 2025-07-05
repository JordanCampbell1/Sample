from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from crud import create_user, authenticate_user
from schemas import UserCreate
from auth import create_access_token
from config import ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
from database import get_db

router = APIRouter()

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    if create_user(db, user.email, user.password):
        return {"msg": "User created"}

@router.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(
        data={"sub": db_user.email},
        expires_delta=timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    )
    return {"access_token": access_token, "token_type": "bearer"}
