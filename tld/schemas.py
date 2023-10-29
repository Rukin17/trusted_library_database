from pydantic import BaseModel


class CorrectLibraryBase(BaseModel):
    library_name: str


class CorrectLibraryCreate(CorrectLibraryBase):
    pass


class CorrectLibrary(CorrectLibraryBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


class DangerousLibraryBase(BaseModel):
    library_name: str


class DangerousLibraryCreate(DangerousLibraryBase):
    pass


class DangerousLibrary(DangerousLibraryBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    correct_libraries: list[CorrectLibrary] = []
    dangerous_libraries: list[DangerousLibrary] = []

    class Config:
        from_attributes = True