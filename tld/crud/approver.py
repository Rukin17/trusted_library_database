from sqlalchemy.orm import Session

from tld import models


def create_approver(db: Session, fullname: str, email: str, password: str, company_id: str):
    fake_hashed_password = password + 'notreallyhashed'
    db_approver = models.Approver(
        fullname=fullname,
        email=email,
        hashed_password=fake_hashed_password,
        company_id=company_id
        )
    db.add(db_approver)
    db.commit()
    return db_approver