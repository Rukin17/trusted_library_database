from sqlalchemy.orm import Session

from tld import models


def get_approver_by_email(db: Session, email: str):
    return db.query(models.Approver).filter(models.Approver.email == email).first()


def get_approver_by_id(db: Session, id: int):
    return db.query(models.Approver).filter(models.Approver.id == id).first()


def get_approvers(db: Session, skip : int = 0, limit: int = 100):
    return db.query(models.Approver).offset(skip).limit(limit).all()


def create_approver(db: Session, fullname: str, email: str, user_id: int):
    db_approver = models.Approver(
        fullname=fullname,
        email=email,
        user_id=user_id
        )
    db.add(db_approver)
    db.commit()
    return db_approver
