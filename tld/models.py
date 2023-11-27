import datetime
import enum

from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Enum, Table, Boolean
from sqlalchemy.orm import relationship
from tld.db import Base
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class LibraryStatus(enum.Enum):
    approved = 'approved'
    malware = 'malware'
    untested = 'untested'



class Roles(enum.Enum):
    USER = 1
    APPROVER = 2
    MANAGER = 3
    ADMIN = 4



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
    username = Column(String, unique=True, nullable=False, index=True)
    fullname = Column(String, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    disabled = Column(Boolean, index=True)
    registered_at = Column(TIMESTAMP, default=datetime.date.today())
    
    approvers = relationship('Approver', back_populates='user')
    roles = relationship('Role', back_populates='user')

    def __repr__(self):
        return f'Company {self.id}, {self.fullname}'


class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, index=True)
    user = Column(Boolean, default=True, index=True)
    admin = Column(Boolean, default=False, index=True)
    approver = Column(Boolean, default=False, index=True)
    manager = Column(Boolean, default=False, index=True)

    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship('User', back_populates='roles')

    def __repr__(self):
        return f'Roles {id}'

class Company(Base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    approvers = relationship('Approver', back_populates='company')
    managers = relationship('Manager', back_populates='company')

    def __repr__(self):
        return f'Company {self.id}, {self.name}'


class Manager(Base):
    __tablename__ = 'managers'

    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True)

    company = relationship('Company', back_populates='managers')


class Approver(Base):
    __tablename__ = 'approvers'
    
    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    registered_at = Column(TIMESTAMP, default=datetime.date.today())
    is_active = Column(Boolean, default=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    

    user = relationship('User', back_populates='approvers')
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
    status = Column(Enum(LibraryStatus), index=True)

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
