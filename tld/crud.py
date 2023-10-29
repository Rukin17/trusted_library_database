import enum
from sqlalchemy.orm import Session

from tld import models, schemas


class Library(enum.Enum):
    correct_library = models.CorrectLibrary
    dangerous_library = models.DangerousLibrary


class LibrarySchemas(enum.Enum):
    correct_library = schemas.CorrectLibraryCreate
    dangerous_library = schemas.DangerousLibraryCreate


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + 'notreallyhashed'
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_library(library: Library, db: Session, library_id: int):
    return db.query(library).filter(library.id == library_id).first()


def get_libraries(library: Library, db: Session, skip: int = 0, limit: int = 100):
    return db.query(library).offset(skip).limit(limit).all()


def create_library(db: Session, library: Library, library_schemas: LibrarySchemas, user_id: int):
    db_library = library(**library_schemas.dict(), user_id=user_id)
    db.add(db_library)
    db.commit()
    db.refresh(db_library)
    return db_library
