from sqlalchemy.orm import Session

from tld import models


def get_library_by_id(db: Session, library_id: int):
    return db.query(models.Library).filter(models.Library.id==library_id).first()


def get_libraries(db: Session, skip : int = 0, limit: int = 100):
    return db.query(models.Library).offset(skip).limit(limit).all()


def create_library(db: Session, name: str):
    db_lybrary = models.Library(name=name, status=models.LibraryStatus.untested)
    db.add(db_lybrary)
    db.commit()
    return db_lybrary


def change_status(db: Session, library: models.Library, status: models.LibraryStatus):
    library.status = status
    db.commit()
    return library