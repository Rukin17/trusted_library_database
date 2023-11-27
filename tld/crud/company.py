from sqlalchemy.orm import Session

from tld import models


def create_company(db: Session, name: str):
    db_company = models.Company(name=name)
    db.add(db_company)
    db.commit()
    return db_company


def get_company_by_id(db: Session, id: int):
    return db.query(models.Company).filter(models.Company.id == id).first()
