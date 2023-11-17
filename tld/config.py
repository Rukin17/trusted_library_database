import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    db_url: str


def load():
    return Config(
        db_url=os.environ['SQLALCHEMY_DATABASE_URL']
    )

my_config = load()