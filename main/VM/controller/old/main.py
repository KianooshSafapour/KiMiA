from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from databases import Database
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import asyncio

DATABASE_URL = "sqlite:///./database.sqlite3"
database = Database(DATABASE_URL)

# SQLAlchemy Model
Base = declarative_base()

class TransactionModel(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    customer_card = Column(String(16), index=True)
    transaction_number = Column(String(20))
    confirmation_number = Column(String(20))
    transaction_date = Column(String(20))
    transaction_time = Column(String(20))
    details = Column(Text, nullable=True)

# FastAPI Model
class TransactionRequest(BaseModel):
    customer_card: str
    transaction_number: str

class TransactionResponse(BaseModel):
    status: str
    data: dict

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI()

async def execute_query(query: str):
    async with database.transaction():
        result = await database.execute(query)
        return result

async def get_transaction_data(customer_card: str, transaction_number: str):
    query = f"SELECT * FROM transactions WHERE customer_card = '{customer_card}' AND transaction_number = '{transaction_number}'"
    result = await execute_query(query)

    transaction_data = await result.fetchone()

    if transaction_data:
        # Assuming you have specific columns you want to retrieve, update this accordingly
        columns = ["id", "customer_card", "transaction_number", "confirmation_number", "transaction_date", "transaction_time", "details"]
        transaction_data_dict = dict(zip(columns, transaction_data))
        return transaction_data_dict
    else:
        return None

async def process_transaction(request: TransactionRequest):
    # Check the database for the transaction
    transaction_data = await get_transaction_data(request.customer_card, request.transaction_number)

    if transaction_data:
        return {"status": "success", "data": dict(transaction_data)}
    else:
        raise HTTPException(status_code=404, detail="Transaction not found")

@app.post("/process_transaction/")
async def process_transaction_endpoint(request: TransactionRequest):
    return await process_transaction(request)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
