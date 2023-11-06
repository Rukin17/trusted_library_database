import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from tld import crud, models, schemas
from tld.db import db_session, engine

from tld.crud import user, library, company, approver, approved_library

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = db_session()
    try:
        yield db
    finally:
        db.close()


@app.post('/users/', response_model=schemas.User)
def create_user(fullname: str, email: str, password: str, db: Session = Depends(get_db)):
    db_user = user.get_user_by_email(db, email=email)
    if db_user:
        raise HTTPException(status_code=400, detail='Email already registered')
    return user.create_user(db=db, fullname=fullname, email=email, password=password)


@app.get('/users/{user_id}', response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = user.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail='User not found')
    return db_user


@app.post('/add_library/', response_model=schemas.Library)
def add_library(name: str, db: Session = Depends(get_db)):
    new_library = library.create_library(db, name=name)
    return new_library


@app.post('/libraries/{library_id}/update/', response_model=schemas.Library)
def update_library(library_id: int, db: Session = Depends(get_db)):
    update_library = library.get_library(db=db, library_id=library_id)
    if not update_library:
        raise HTTPException(status_code=404, detail=("Library doesn't exists"))
    return library.update_library(db=db, library=update_library)


@app.post('/companies/{approver_id}/create_approved_libraries/', response_model=schemas.ApprovedLibrary)
def create_approved_library(approver_id: int, library_id: int, db: Session = Depends(get_db)):
    db_library = library.get_library(db, library_id=library_id)

    if not db_library:
        raise HTTPException(status_code=404, detail=("Library doesn't exists"))
    
    # TODO написать проверку elif db_library.status != models.Status.approved: 

    approves =  approved_library.create_approved_library(
        db=db,
        name=db_library.name,
        approver_id=approver_id,
        library_id=library_id
        )
    return approves


@app.post('/companies/', response_model=schemas.Company)
def create_company(name: str, db: Session = Depends(get_db)):
    return company.create_company(db, name=name)


@app.get('/companies/{company_id}', response_model=schemas.Company)
def get_company_by_id(company_id: int, db: Session = Depends(get_db)):
    db_company = company.get_company_by_id(db, id=company_id)
    if not db_company:
        raise HTTPException(status_code=404, detail='Company not found')
    return db_company


@app.post('/companies/{company_id}/create_approver/', response_model=schemas.Approver)
def create_approver(fullname: str, password: str, email: str, company_id: int, db: Session = Depends(get_db)):
    db_user = user.get_user_by_email(db, email=email)
    if db_user:
        raise HTTPException(status_code=400, detail='Email already registered')
    new_user = user.create_user(db=db, fullname=fullname, email=email, password=password)

    new_approver = approver.create_approver(
        db=db,
        fullname=fullname,
        email=email,
        company_id=company_id,
        user_id=new_user.id
        )
    return new_approver

#TODO ручка delete approver 
#TODO ручка authors


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)

