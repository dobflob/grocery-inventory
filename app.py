from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

engine = create_engine('sqlite:///inventory.db', echo=False)
Session = sessionmaker(engine)
session = Session()
Base = declarative_base()

if __name__ == '__main__':
    Base.metadata.create_all(engine)