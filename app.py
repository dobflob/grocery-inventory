from models import Base, session, engine, Brands, Products
import csv

def app():
    print('app is running')

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    app()