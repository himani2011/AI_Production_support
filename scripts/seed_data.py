from ecommerce.database import SessionLocal
from ecommerce.models import Customer, Product, Order

session = SessionLocal()

customer1 = Customer(
    name="John",
    email="john@test.com"
)

customer2 = Customer(
    name="Alice",
    email="alice@test.com"
)

product1 = Product(
    name="Laptop",
    price=1200,
    stock=5
)

product2 = Product(
    name="Mouse",
    price=50,
    stock=20
)

order1 = Order(
    customer_id=1,
    product_id=1,
    status="Completed"
)

order2 = Order(
    customer_id=2,
    product_id=2,
    status="Pending"
)

session.add_all([
    customer1,
    customer2,
    product1,
    product2,
    order1,
    order2
])

session.commit()

session.close()

print("Sample data inserted.")