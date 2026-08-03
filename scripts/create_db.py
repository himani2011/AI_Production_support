from ecommerce.database import engine, Base

# Import all models
from ecommerce.models import Customer, Product, Order

Base.metadata.create_all(bind=engine)

print("Database Created Successfully!")