import enum
import uvicorn
import sqlalchemy
from datetime import timedelta

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from typing import Annotated
from sqlalchemy.orm import Session


from . import models, schemas
from tld.db import db_session, engine

from tld.crud import user, library, company, approver, approved_library
from tld.auth import Token, authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_current_active_user



models.Base.metadata.create_all(bind=engine)





def get_db():
    db = db_session()
    try:
        yield db
    finally:
        db.close()


class Roles(enum.Enum):
    USER = 1
    APPROVER = 2
    MANAGER = 3
    ADMIN = 4


app = FastAPI()


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

