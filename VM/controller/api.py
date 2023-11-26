from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import sqlite3

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
conn = sqlite3.connect("database.sqlite3")
cursor = conn.cursor()

# FastAPI route to handle requests
@app.post("/check-transaction")
async def check_transaction(card_number: str, destination_card: str, transaction_number: str):
    # Check the transaction in the database
    cursor.execute("SELECT * FROM transactions WHERE card_number = ? AND destination_card = ? AND transaction_number = ?", (card_number, destination_card, transaction_number))
    transaction_result = cursor.fetchone()

    if transaction_result:
        return {"status": "success", "message": "Transaction found"}

    # If transaction not found, run the bot
    return run_bot()

def run_bot():
    # Fetch the active account from the database
    cursor.execute("SELECT * FROM accounts WHERE status = 'active'")
    active_account = cursor.fetchone()

    if not active_account:
        raise HTTPException(status_code=400, detail="No active account found")

    bank = active_account[1]
    username = active_account[3]
    password = active_account[4]
    url = active_account[5]

    # Run Selenium bot
    try:
        if bank == "example_bank":
            run_example_bank_bot(username, password, url)
        # Add more banks as needed
        else:
            raise HTTPException(status_code=400, detail="Invalid bank")

        # Update transaction status in the database if successful
        cursor.execute("INSERT INTO transactions (card_number, destination_card, transaction_number) VALUES (?, ?, ?)", (card_number, destination_card, transaction_number))
        conn.commit()

        return {"status": "success", "message": "Transaction successful"}

    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": f"Bot error: {str(e)}"})


def run_example_bank_bot(username, password, url):
    # Replace this with your Selenium bot logic for the specific bank
    driver = webdriver.Chrome()  # You may need to download the appropriate webdriver for your browser
    driver.get(url)

    # Add your bot logic here using the provided username and password
    # ...

    driver.quit()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
