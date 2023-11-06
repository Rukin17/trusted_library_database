from sqlalchemy.orm import Session

from tld import models


def create_approver(db: Session, fullname: str, email: str, company_id: int, user_id: int):
    db_approver = models.Approver(
        fullname=fullname,
        email=email,
        company_id=company_id,
        user_id=user_id
        )
    db.add(db_approver)
    db.commit()
    return db_approver