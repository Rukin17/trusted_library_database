from sqlalchemy.orm import Session

from tld import models


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, fullname: str, email: str, password: str):
    fake_hashed_password = password + 'notreallyhashed'
    db_user = models.User(fullname=fullname, email=email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
