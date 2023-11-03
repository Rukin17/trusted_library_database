import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from tld import crud, models, schemas
from tld.db import db_session, engine

from tld.crud_1 import user, library

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
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = user.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail='User not found')
    return db_user


@app.post('/add_library/', response_model=schemas.Library)
def add_library(name: str, db: Session = Depends(get_db)):
    new_library = library.create_library(db, name=name)
    return new_library


# @app.get('/correct_libraries/', response_model=list[schemas.Library])
# def read_libraries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     libraries = crud.get_libraries(
#         library=crud.Library.correct_library,
#         db=db,
#         skip=skip,
#         limit=limit
#         )
#     return libraries


# @app.post('/users/{user_id}/dangerous_libraries/', response_model=schemas.Library)
# def add_library(user_id: int, library: schemas.DangerousLibraryCreate, db: Session = Depends(get_db)):
#     new_library = crud.create_library(
#         db=db, 
#         library=crud.Library.dangerous_library, 
#         library_schemas=crud.LibrarySchemas.dangerous_library, 
#         user_id=user_id
#         )
#     return new_library


# @app.get('/dangerous_libraries/', response_model=list[schemas.Library])
# def read_libraries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     libraries = crud.get_libraries(
#         library=crud.Library.dangerous_library,
#         db=db,
#         skip=skip,
#         limit=limit
#         )
#     return libraries



@app.get('/')
def read_root():
    return {'hello': 'world'}


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)

