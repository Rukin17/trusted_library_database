from sqlalchemy.orm import Session

from tld import models


def create_author(db: Session, name: str):
    db_author = models.Author(name=name)
    db.add(db_author)
    db.commit()
    return db_author
