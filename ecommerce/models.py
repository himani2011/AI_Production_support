from sqlalchemy import Column, Integer, String, ForeignKey
from ecommerce.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    price = Column(Integer, nullable=False)
    stock = Column(Integer, nullable=False)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)

    customer_id = Column(Integer, ForeignKey("customers.id"))

    product_id = Column(Integer, ForeignKey("products.id"))

    status = Column(String(50), nullable=False)