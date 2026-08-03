import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATABASE_URL = f"sqlite:///{BASE_DIR}/database/ecommerce.db"