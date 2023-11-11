from pydantic import BaseModel
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status

from typing import Annotated
from dataclasses import dataclass
from jose import JWTError, jwt
from tld.hashing import Hasher
from sqlalchemy.orm import Session
from tld.db import get_db
from . import schemas


from tld.crud import user
from fastapi.security import OAuth2PasswordBearer

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "613a5daa21f5aafe87905481e0ad04d622b7e62269218f973d844b4cd9beae34"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None



@dataclass
class UserInDB:
    id: int
    username: str
    fullname: str
    email: str
    hashed_password: str
    disabled: bool


def get_user(db: Session, username: str):
    db_user = user.get_user_by_username(db, username=username)
    
    return UserInDB(db_user.id, db_user.username, db_user.fullname, db_user.email, db_user.hashed_password, db_user.disabled)


def authenticate_user(db, username: str, password: str):
    user = get_user(db, username=username)
    if not user:
        return False
    if not Hasher.verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(
    current_user: Annotated[schemas.User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user



