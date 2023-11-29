from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from databases import Database
import asyncio
from datetime import datetime

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

# FastAPI Model
class Transaction(BaseModel):
    customer_card: str
    destination_card: str
    transaction_number: str
    confirmation_number: str
    transaction_date: str
    transaction_time: str
    details: str = None

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
database = Database(DATABASE_URL)

app = FastAPI()

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

async def execute_query(query: str):
    async with database.transaction():
        return await database.execute(query)

async def get_confirmation_code(transaction_id: int):
    query = f"SELECT confirmation_number FROM transactions WHERE id = {transaction_id}"
    result = await execute_query(query)
    return result.fetchone()

async def process_transaction(transaction: Transaction):
    # Check if the transactions table exists
    if not engine.dialect.has_table(engine, "transactions"):
        # If not, create the table
        Base.metadata.create_all(bind=engine)

    # Create a new transaction record
    new_transaction = TransactionModel(
        customer_card=transaction.customer_card,
        destination_card=transaction.destination_card,
        transaction_number=transaction.transaction_number,
        confirmation_number=transaction.confirmation_number,
        transaction_date=transaction.transaction_date,
        transaction_time=transaction.transaction_time,
        details=transaction.details,
    )

    # Add the transaction record to the database
    db = SessionLocal()
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    # Retrieve the confirmation code
    confirmation_code = await get_confirmation_code(new_transaction.id)
    
    return {"status": "success", "data": {"confirmation_code": confirmation_code}}

@app.post("/process_transactions/")
async def process_transactions(transactions: list[Transaction] = Query(...)):
    tasks = [process_transaction(transaction) for transaction in transactions]
    results = await asyncio.gather(*tasks)
    return results

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
