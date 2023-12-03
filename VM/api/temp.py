from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
import sqlite3

app = FastAPI()

class TransactionRequest(BaseModel):
    card_number: int
    dest_number: int
    transaction_number: int

def check_transaction(request: TransactionRequest):
    # Connect to the SQLite database
    conn = sqlite3.connect('database.sqlite3')
    cursor = conn.cursor()

    # Check if a record with the provided information exists in the transactions table
    cursor.execute('''
        SELECT * FROM transactions
        WHERE customer_card = ? AND account_card = ? AND transaction_confirmation = ?
    ''', (request.card_number, request.dest_number, request.transaction_number))

    result = cursor.fetchone()

    # Close the database connection
    conn.close()

    if result:
        return {"status": "200", "message": "Transaction found"}
    else:
        raise HTTPException(status_code=404, detail="Transaction not found")

@app.post("/check-transaction")
def check_transaction_route(request: TransactionRequest = Body(...)):
    return check_transaction(request)
