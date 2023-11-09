import uvicorn
import sqlalchemy
from datetime import datetime, timedelta

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from dataclasses import dataclass
from jose import JWTError, jwt
from passlib.context import CryptContext

from pydantic import BaseModel
from sqlalchemy.orm import Session
from enum import Enum
from tld import crud, models, schemas
from tld.db import db_session, engine

from tld.crud import user, library, company, approver, approved_library

models.Base.metadata.create_all(bind=engine)


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "613a5daa21f5aafe87905481e0ad04d622b7e62269218f973d844b4cd9beae34"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30



def get_db():
    db = db_session()
    try:
        yield db
    finally:
        db.close()


class Roles(Enum):
    USER = 1
    APPROVER = 2
    MANAGER = 3
    ADMIN = 4


fake_users_db = {
    "johndoe": {
        'id': 1,
        "username": "johndoe",
        'roles': [Roles.APPROVER, Roles.USER, Roles.MANAGER, Roles.ADMIN],
        "fullname": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


app = FastAPI()

def fake_hash_password(password: str):
    return 'fakehashed' + password


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)

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
    # if username in users:
    #     user_dict = db[username]
    return UserInDB(db_user.id, db_user.username, db_user.fullname, db_user.email, db_user.hashed_password, db_user.disabled)


def authenticate_user(db, username: str, password: str):
    user = get_user(db, username=username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
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


@app.post("/token", response_model=Token)
def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[sqlalchemy.Engine, Depends(get_db)]):
    user = authenticate_user(db=db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=schemas.User)
def read_users_me(
    current_user: Annotated[schemas.User, Depends(get_current_active_user)]
):
    return current_user


@app.get("/users/me/items/")
def read_own_items(
    current_user: Annotated[schemas.User, Depends(get_current_active_user)]
):
    return [{"item_id": "Foo", "owner": current_user.username}]










def get_roles(db: Session = Depends(get_db)) -> list[Roles]:
    pass


@app.post('/users/', response_model=schemas.User)
def create_user(username: str, fullname: str, email: str, password: str, db: Session = Depends(get_db)):
    db_user = user.get_user_by_email(db, email=email)
    if db_user:
        raise HTTPException(status_code=400, detail='Email already registered')
    return user.create_user(db=db, username=username, fullname=fullname, email=email, password=password)



@app.post('/companies/', response_model=schemas.Company)
def create_company(name: str, db: Session = Depends(get_db), roles: list[Roles] = Depends(get_roles)):
    # if Roles.ADMIN in roles:
        return company.create_company(db, name=name)
    # else:
    #     raise HTTPException(status_code=403, detail='')


@app.post('/companies/{company_id}/approvers/', response_model=schemas.Approver)
def bind_approver_to_company(email: str, company_id: int, db: Session = Depends(get_db)):
    db_approver = approver.get_approver_by_email(db, email=email)
    if not db_approver:
        raise HTTPException(status_code=400, detail='Email not registered')
    db_approver.company_id = company_id
    db.commit()
    return db_approver


@app.post('/libraries/', response_model=schemas.Library)
def add_library(name: str, db: Session = Depends(get_db)):
    new_library = library.create_library(db, name=name)
    
    #TODO  authors

    return new_library


#TODO сделать авторизацию и взять approver_id 
@app.post('/libraries/{library_id}/approve', response_model=schemas.ApprovedLibrary)
def approve_library(library_id: int, approver_id: int, db: Session = Depends(get_db)):
    db_library = library.get_library_by_id(db=db, library_id=library_id)
    if not db_library:
        raise HTTPException(status_code=404, detail=("Library doesn't exists"))
    
    db_approver = approver.get_approver_by_id(db=db, id=approver_id)
    if db_approver.is_active:
        library.change_status(db=db, library=db_library, status=models.Status.approved)
        approve =  approved_library.create_approved_library(
            db=db,
            name=db_library.name,
            approver_id=approver_id,
            library_id=library_id
            )
        return approve


@app.post('/libraries/{library_id}/ban', response_model=schemas.Library)
def ban_library(library_id: int, approver_id: int, db: Session = Depends(get_db)):
    db_library = library.get_library_by_id(db=db, library_id=library_id)
    if not db_library:
        raise HTTPException(status_code=404, detail=("Library doesn't exists"))
    
    db_approver = approver.get_approver_by_id(db=db, id=approver_id)
    if db_approver.is_active:
        library.change_status(db=db, library=db_library, status=models.Status.malware)
    return db_library



@app.post('/approvers/', response_model=schemas.Approver)
def create_approver(email: str, db: Session = Depends(get_db)):
    db_user = user.get_user_by_email(db=db, email=email)
    new_approver = approver.create_approver(
        db=db,
        fullname=db_user.fullname,
        email=email,
        user_id=db_user.id
    )
    return new_approver


@app.post('/approvers/{approver_id}/ban/', response_model=schemas.Approver)
def ban_approver(id: int, db: Session = Depends(get_db)):
    db_approver = approver.get_approver_by_id(db=db, id=id)
    db_approver.is_active = False
    db.commit()
    return db_approver


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)

