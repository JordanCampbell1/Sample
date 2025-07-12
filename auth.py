from datetime import datetime, timedelta
import secrets
from fastapi import Depends, HTTPException, status
from jose import ExpiredSignatureError, jwt, JWTError
from config import SECRET_KEY, ALGORITHM
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_db
from models import RefreshToken, User


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


def create_refresh_token(user_id: int, expires_at: datetime, db: Session):
    token = secrets.token_urlsafe(64)  # ~384 bits of entropy

    refresh_token = RefreshToken(token=token, user_id=user_id, expires_at=expires_at)
    db.add(refresh_token)
    db.commit()
    db.refresh(refresh_token)
    return refresh_token


# OAuth2 scheme — looks for Authorization: Bearer <token>
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    # print(f"Received token: {token}")  # Debugging line
    # paylod = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    # print(f"Decoded payload: {paylod}")  # Debugging line
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # print("Checking token...")  # Debugging line
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # print(f"Decoded payload: {payload}")  # Debugging line
        user_id: int = int(payload.get("sub"))
        # print(f"Decoded user_id: {user_id}")  # Debugging line'
        # print(f"Decoded payload: {payload}")  # Debugging line
        if user_id is None:
            raise credentials_exception
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user
