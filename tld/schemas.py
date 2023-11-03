from pydantic import BaseModel


class User(BaseModel):
    id: int
    fullname: str
    email: str

    class Config:
        from_attributes = True


class Library(BaseModel):
    id: int
    name: str
    status: str

    class Config:
        from_attributes = True