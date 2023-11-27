
from fastapi import Depends, HTTPException

from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter

from tld import models, schemas
from tld.db import get_db, engine
from tld.crud import user, library, company, approver, approved_library
from tld.auth import get_current_active_user
from tld.models import Role


models.Base.metadata.create_all(bind=engine)



user_router = APIRouter()


def get_roles(db: Session = Depends(get_db)) -> list[Role]:
    pass


@user_router.post('/companies/', response_model=schemas.Company)
def create_company(name: str, db: Session = Depends(get_db), roles: list[Role] = Depends(get_roles)):
    # if Roles.ADMIN in roles:
        return company.create_company(db, name=name)
    # else:
    #     raise HTTPException(status_code=403, detail='')



@user_router.get("/me/", response_model=schemas.User)
def read_users_me(
    current_user: Annotated[schemas.User, Depends(get_current_active_user)]
):
    return current_user


@user_router.get("/me/items/")
def read_own_items(
    current_user: Annotated[schemas.User, Depends(get_current_active_user)]
):
    return [{"item_id": "Foo", "owner": current_user.username}]



@user_router.post('/', response_model=schemas.User)
def create_user(username: str, fullname: str, email: str, password: str, db: Session = Depends(get_db)):
    db_user = user.get_user_by_email(db, email=email)
    if db_user:
        raise HTTPException(status_code=400, detail='Email already registered')
    return user.create_user(db=db, username=username, fullname=fullname, email=email, password=password)



@user_router.post('/companies/', response_model=schemas.Company)
def create_company(name: str, db: Session = Depends(get_db), roles: list[Role] = Depends(get_roles)):
    # if Roles.ADMIN in roles:
        return company.create_company(db, name=name)
    # else:
    #     raise HTTPException(status_code=403, detail='')


@user_router.post('/companies/{company_id}/approvers/', response_model=schemas.Approver)
def bind_approver_to_company(email: str, company_id: int, db: Session = Depends(get_db)):
    db_approver = approver.get_approver_by_email(db, email=email)
    if not db_approver:
        raise HTTPException(status_code=400, detail='Email not registered')
    db_approver.company_id = company_id
    db.commit()
    return db_approver


@user_router.post('/libraries/', response_model=schemas.Library)
def add_library(name: str, db: Session = Depends(get_db)):
    new_library = library.create_library(db, name=name)
    
    #TODO  authors

    return new_library


#TODO сделать авторизацию и взять approver_id 
@user_router.post('/libraries/{library_id}/approve', response_model=schemas.ApprovedLibrary)
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


@user_router.post('/libraries/{library_id}/ban', response_model=schemas.Library)
def ban_library(library_id: int, approver_id: int, db: Session = Depends(get_db)):
    db_library = library.get_library_by_id(db=db, library_id=library_id)
    if not db_library:
        raise HTTPException(status_code=404, detail=("Library doesn't exists"))
    
    db_approver = approver.get_approver_by_id(db=db, id=approver_id)
    if db_approver.is_active:
        library.change_status(db=db, library=db_library, status=models.Status.malware)
    return db_library



@user_router.post('/approvers/', response_model=schemas.Approver)
def create_approver(email: str, db: Session = Depends(get_db)):
    db_user = user.get_user_by_email(db=db, email=email)
    new_approver = approver.create_approver(
        db=db,
        fullname=db_user.fullname,
        email=email,
        user_id=db_user.id
    )
    return new_approver


@user_router.post('/approvers/{approver_id}/ban/', response_model=schemas.Approver)
def ban_approver(id: int, db: Session = Depends(get_db)):
    db_approver = approver.get_approver_by_id(db=db, id=id)
    db_approver.is_active = False
    db.commit()
    return db_approver