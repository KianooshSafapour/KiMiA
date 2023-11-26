from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] - %(message)s",
    handlers=[
        RotatingFileHandler("api.log", maxBytes=1e6, backupCount=5),  # Rotating log file
        logging.StreamHandler(),  # Log to console
    ],
)

# FastAPI setup
app = FastAPI()

# Logger instance
logger = logging.getLogger(__name__)

# SQLite database setup
engine = create_engine("sqlite:///database.sqlite3", connect_args={"check_same_thread": False})
metadata = MetaData()

transactions = Table(
    "transactions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("ccn", String(length=16)),  # 16 digits varchar
    Column("acn", String(length=16)),  # 16 digits varchar
    Column("tcn", String(length=12)),  # 12 digits varchar
    # Add other columns as needed
)

metadata.create_all(bind=engine)

# Pydantic model for the request body
class TransactionRequest(BaseModel):
    ccn: str
    acn: str
    tcn: str

# API endpoint to check the transaction
@app.post("/check-transaction")
async def check_transaction(transaction_data: TransactionRequest = Body(...)):
    try:
        # Your transaction-checking logic here
        with engine.connect() as connection:
            query = transactions.select().where(
                transactions.c.ccn == transaction_data.ccn,
                transactions.c.acn == transaction_data.acn,
                transactions.c.tcn == transaction_data.tcn,
            )
            result = connection.execute(query)

            if result.fetchone():
                logger.info("Transaction found")
                return {"status": 200, "message": "Transaction found"}
            else:
                logger.info("Transaction not found")
                raise HTTPException(status_code=404, detail="Transaction not found")

    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
