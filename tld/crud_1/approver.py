from sqlalchemy.orm import Session

from tld import models


def create_approver(db: Session, password: str, user_id: str, company_id: str):
    fake_hashed_password = password + 'notreallyhashed'
    db_approver = models.Approver(hashed_password=fake_hashed_password, user_id=user_id, company_id=company_id)
    db.add(db_approver)
    db.commit()
    return db_approver