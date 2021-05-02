from sqlalchemy import create_engine

from vocabulizer import DATABASE_URI
from vocabulizer.etl.models import Base

engine = create_engine(DATABASE_URI)


def recreate_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def register_new_user():
    pass


if __name__ == "__main__":
    Base.metadata.create_all(engine)
