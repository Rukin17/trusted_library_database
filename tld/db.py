from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from tld.config import config

# SQLALCHEMY_DATABASE_URL = 'postgres://uuwbzbfr:5NRzWL_nrV3stNmNK6s99r5LsnDifWtw@cornelius.db.elephantsql.com:5432/uuwbzbfr'
# , connect_args={'check_same_thread': False}
engine = create_engine(config.db_url)
db_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
