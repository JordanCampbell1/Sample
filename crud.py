from sqlalchemy.orm import Session
from models import User
from security import get_password_hash, verify_password

def create_user(db: Session, email: str, password: str):
    hashed_pw = get_password_hash(password)
    user = User(email=email, hashed_password=hashed_pw)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user
