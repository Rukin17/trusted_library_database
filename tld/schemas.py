from pydantic import BaseModel
from tld.models import Status

class User(BaseModel):
    id: int
    fullname: str
    email: str

    class Config:
        from_attributes = True


class Library(BaseModel):
    id: int
    name: str
    status: Status

    class Config:
        from_attributes = True


class Company(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class Approver(BaseModel):
    id: int
    fullname: str
    email: str
    company_id: int

    class Config:
        from_attributes = True