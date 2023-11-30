from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from faker import Faker
from datetime import datetime
import random

DATABASE_URL = "sqlite:///./database.sqlite3"

# SQLAlchemy Model
Base = declarative_base()

class TransactionModel(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    customer_card = Column(String(16), index=True)
    destination_card = Column(String(16), index=True)
    transaction_number = Column(String(20))
    confirmation_number = Column(String(20))
    transaction_date = Column(String(20))
    transaction_time = Column(String(20))
    details = Column(Text, nullable=True)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def generate_fake_transaction():
    fake = Faker()
    return {
        "customer_card": fake.credit_card_number(card_type="mastercard"),
        "destination_card": fake.credit_card_number(card_type="visa"),
        "transaction_number": fake.uuid4(),
        "confirmation_number": fake.uuid4(),
        "transaction_date": datetime.now().strftime("%Y-%m-%d"),
        "transaction_time": datetime.now().strftime("%H:%M:%S"),
        "details": fake.text(),
    }

def fill_transactions_table(num_records):
    db = SessionLocal()
    Base.metadata.create_all(bind=engine)

    for _ in range(num_records):
        fake_transaction = generate_fake_transaction()
        new_transaction = TransactionModel(**fake_transaction)
        db.add(new_transaction)

    db.commit()
    db.close()

if __name__ == "__main__":
    # Specify the number of records you want to generate and insert
    num_records_to_insert = 1000

    fill_transactions_table(num_records_to_insert)
    print(f"Inserted {num_records_to_insert} records into the transactions table.")
