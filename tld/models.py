import datetime
from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from tld.db import Base



class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    registered_at = Column(TIMESTAMP, default=datetime.date.today())

    
    correct_libraries = relationship('CorrectLibrary', back_populates='user')
    dangerous_libraries = relationship('DangerousLibrary', back_populates='user')



class CorrectLibrary(Base):
    __tablename__ = 'correct_libraries'

    id = Column(Integer, primary_key=True, index=True)
    library_name = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship('User', back_populates='correct_libraries')

    def __repr__(self):
        return f'Correct Library {self.id}, {self.library_name}'


class DangerousLibrary(Base):
    __tablename__ = 'dangerous_libraries'

    id = Column(Integer, primary_key=True, index=True)
    library_name = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship('User', back_populates='dangerous_libraries')


    def __repr__(self):
        return f'Dangerous Library {self.id}, {self.library_name}'