from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime, timedelta
import requests

app = FastAPI()

class TransactionRequest(BaseModel):
    customer_card: str
    destination_card: str
    transaction_code: str
    from_date: str = None
    from_time: str = None
    to_date: str = None
    to_time: str = None

@app.get("/get_card")
async def get_card():
    
    # Assuming get_worker is a function in manage.py
    result = get_worker()
    return {"status": result[0], "data": result[1]}

@app.post("/check_transaction")
async def check_transaction(request_data: TransactionRequest):
    # Set default values for from_date, from_time, to_date, and to_time if not provided
    if not request_data.from_date:
        request_data.from_date = (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d")
    if not request_data.from_time:
        request_data.from_time = (datetime.now() - timedelta(hours=1)).strftime("%H:%M:%S")
    if not request_data.to_date:
        request_data.to_date = datetime.now().strftime("%Y-%m-%d")
    if not request_data.to_time:
        request_data.to_time = datetime.now().strftime("%H:%M:%S")

    # Prepare data for the request
    transaction_data = {
        "customer_card": request_data.customer_card,
        "destination_card": request_data.destination_card,
        "transaction_code": request_data.transaction_code,
        "from_date": request_data.from_date,
        "from_time": request_data.from_time,
        "to_date": request_data.to_date,
        "to_time": request_data.to_time,
    }

    # Make a request to the external API
    try:
        response = requests.post("https://test.dev/check_transaction", json=transaction_data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error contacting external API: {str(e)}")
