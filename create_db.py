from ecommerce.database import engine, Base
from ecommerce.models import Customer, Product, Order

Base.metadata.create_all(engine)

print("Database Created Successfully!")