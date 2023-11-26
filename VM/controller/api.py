from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fetcher import update_database  # Import your Selenium bot function
import sqlite3

app = FastAPI()

# Define a Pydantic model for the request payload
class TransactionRequest(BaseModel):
    customerCard: str
    destinationCard: str
    transactionID: str

# SQLite connection setup
conn = sqlite3.connect('database.sqlite3')
cursor = conn.cursor()

# Check if the transactions table exists, and create it if not
cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customerCard VARCHAR(16),
        destinationCard VARCHAR(16),
        transactionID VARCHAR(20),
        transactionDate VARCHAR(20),
        transactionTime VARCHAR(20),
        details TEXT
    )
''')
conn.commit()

# FastAPI route to handle incoming requests
@app.post("/check_transaction")
async def check_transaction(request: TransactionRequest):
    # Check if the transaction exists in the database
    cursor.execute(
        "SELECT * FROM transactions WHERE customerCard = ? AND destinationCard = ? AND transactionID = ?",
        (request.customerCard, request.destinationCard, request.transactionID),
    )
    result = cursor.fetchone()

    if result:
        # Transaction found, return success with details
        transaction_details = {
            "transactionDate": result[3],
            "transactionTime": result[4],
            "details": result[5] if result[5] else "No details available",
        }
        return {"status": "success", "details": transaction_details}

    else:
        # Transaction not found, run the Selenium bot
        bot_result = update_database(request.customerCard, request.destinationCard)

        if bot_result["status"] == "success":
            # Bot ran successfully, check the database again and return success with log message
            cursor.execute(
                "SELECT * FROM transactions WHERE customerCard = ? AND destinationCard = ? AND transactionID = ?",
                (request.customerCard, request.destinationCard, request.transactionID),
            )
            result_after_bot = cursor.fetchone()

            if result_after_bot:
                transaction_details_after_bot = {
                    "transactionDate": result_after_bot[3],
                    "transactionTime": result_after_bot[4],
                    "details": result_after_bot[5] if result_after_bot[5] else "No details available",
                }
                return {"status": "success", "log_message": bot_result["log_message"], "details": transaction_details_after_bot}
            else:
                raise HTTPException(status_code=500, detail="Bot ran successfully, but transaction still not found in the database")

        else:
            # Bot failed to update the database, return failure with log message
            raise HTTPException(status_code=500, detail=bot_result["log_message"])

# Lifespan event handler to close the SQLite connection when the FastAPI app shuts down
@app.on_event("shutdown")
def shutdown_event():
    conn.close()
