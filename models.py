from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

engine = create_engine('sqlite:///inventory.db', echo=False)
Session = sessionmaker(engine)
session = Session()
Base = declarative_base()

class Brands(Base):
    __tablename__ = 'brands'

    brand_id = Column(Integer, primary_key=True)
    brand_name = Column(String, nullable=False)
    products = relationship('Products', back_populates='brand')
    
    def __repr__(self):
        return f"""
    Id: {self.brand_id},
    Name: {self.brand_name}
    """

class Products(Base):
    __tablename__ = 'products'

    product_id = Column(Integer, primary_key=True)
    product_name = Column(String, nullable=False)
    product_quantity = Column(Integer, nullable=False)
    product_price = Column(Integer, nullable=False)
    date_updated = Column(Date, nullable=False)
    brand_id = Column(Integer, ForeignKey('brands.brand_id'))
    brand = relationship('Brands', back_populates='products')
    
    def __repr__(self):
        return f"""
    Id: {self.product_id},
    Name: {self.product_name}
    Quantity: {self.product_quantity}
    Price: {self.product_price}
    Updated: {self.date_updated}
    Brand Id: {self.brand_id}
    """