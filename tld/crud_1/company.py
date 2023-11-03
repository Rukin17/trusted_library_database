from sqlalchemy.orm import Session

from tld import models


def create_company(db: Session, name: str):
    db_company = models.Company(name=name)
    db.add(db_company)
    db.commit()
    return db_company

