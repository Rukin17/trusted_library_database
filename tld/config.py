import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    db_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int


def load():
    return Config(
        db_url=os.environ['SQLALCHEMY_DATABASE_URL'],
        secret_key=os.environ['SECRET_KEY'],
        algorithm=os.environ['ALGORITHM'],
        access_token_expire_minutes=os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'],

    )

my_config = load()