import datetime
import enum

from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship
from tld.db import Base


class Status(enum.Enum):
    approved = 'approved'
    malware = 'malware'
    untested = 'untested'


association_table = Table(
    'association_table',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('library_id', ForeignKey('libraries.id'), primary_key=True),
    Column('author_id', ForeignKey('authors.id'), primary_key=True),
)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    registered_at = Column(TIMESTAMP, default=datetime.date.today())

    
    # approvers = relationship('Approver', back_populates='user')

    def __repr__(self):
        return f'Company {self.id}, {self.fullname}'


class Company(Base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    approvers = relationship('Approver', back_populates='company')

    def __repr__(self):
        return f'Company {self.id}, {self.name}'


class Approver(Base):
    __tablename__ = 'approvers'
    
    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    registered_at = Column(TIMESTAMP, default=datetime.date.today())
    company_id = Column(Integer, ForeignKey('companies.id'))
    # user_id = Column(Integer, ForeignKey('users.id'))
    

    # user = relationship('User', back_populates='approvers')
    company = relationship('Company', back_populates='approvers')
    approved_libraries = relationship('ApprovedLibrary', back_populates='approver')

    def __repr__(self):
        return f'Approver {self.id}, company_id {self.company_id}'


class ApprovedLibrary(Base):
    __tablename__ = 'approved_libraries'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    approver_id = Column(Integer, ForeignKey('approvers.id'))
    library_id = Column(Integer, ForeignKey('libraries.id'))

    approver = relationship('Approver', back_populates='approved_libraries')
    library = relationship('Library', back_populates='approved_libraries')

    def __repr__(self):
        return f'Approved Library {self.id}, {self.name}'
    

class Library(Base):
    __tablename__ = 'libraries'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    status = Column(Enum(Status), index=True)

    approved_libraries = relationship('ApprovedLibrary', back_populates='library')
    authors = relationship('Author', secondary=association_table, back_populates='libraries')
 
    def __repr__(self):
        return f'Library {self.id}, {self.name}'
    

class Author(Base):
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    libraries = relationship('Library', secondary=association_table, back_populates='authors')

    def __repr__(self):
        return f'Author {self.id}, {self.name}'
