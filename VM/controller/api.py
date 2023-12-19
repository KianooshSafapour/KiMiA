import json
from fastapi import FastAPI, Request,BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from typing import Optional
from requests import Session
import controller as ctrl
import asyncio
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
# Database setup (assuming SQLite3)
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from asyncio import Queue

app = FastAPI()

# Mount the static files directory
#app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
semaphore = asyncio.Semaphore(1)
DATABASE_URL = "sqlite:///./database.sqlite3"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

db_update_semaphore = asyncio.Semaphore(value=1)  # Set the value to the maximum number of concurrent accesses

# Global queue to store requests waiting for the database update
request_queue = Queue()


class Settings(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(Boolean, default=False)
    value = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# ccn: Customer Card Number, dcn: Destination Card Number, tcn: Transaction Confirmation Number
# fd: From Date, ft: From Time, td: To Date, tt: To Time

# API Endpoints
@app.post("/check_transaction")
async def check_transaction_endpoint(   
    background_tasks: BackgroundTasks, 
    ccn: str,
    dcn: str,
    tcn: str,
    fd: str = None,
    ft: str = None,
    td: str = None,
    tt: str = None):
    # Check the database asynchronously
    data_exists = await ctrl.check_transaction(ccn,dcn,tcn)

    if not data_exists:
        # Enqueue the background task to update the database asynchronously
        background_tasks.add_task(ctrl.update(driver,dcn, fd, ft, td, tt))
        update_res=await ctrl.update(driver, dcn, fd, ft, td, tt)  # Wait for the background task to complete
        print("###############print(update_res)print(update_res)###############")
        print(update_res['message'])
        print(update_res)
        
        if(update_res['status']=='success'):
        # After waiting for the update to complete, check the database again
            data_existsi = await ctrl.check_transaction(ccn,dcn,tcn)
            print(f"data_existsidata_existsi:::::::{data_existsi}::::{ccn}---{dcn}---{tcn}")
            if not data_existsi:
                return {'status':'failure',"message": "Database update failed."}
        
            transaction_id, from_card, to_card, transaction_confirm, date, time = data_existsi[0]

            result_json = {
                "status": "success",
                "transaction": {
                    "from_card": from_card,
                    "to_card": to_card,
                    "transaction_confirm": transaction_confirm,
                    "date": date,
                    "time": time
                }
            }

            result_json_string = json.dumps(result_json)
            return result_json_string
        else: return {'status':'failure',"message": "Database update failed. Please try again later"}
    else:            
        transaction_id, from_card, to_card, transaction_confirm, date, time = data_exists[0]

        result_json = {
                "status": "success",
                "transaction": {
                    "from_card": from_card,
                    "to_card": to_card,
                    "transaction_confirm": transaction_confirm,
                    "date": date,
                    "time": time
                }
            }

        result_json_string = json.dumps(result_json)
        return result_json_string


    
    #result =await ctrl.check_transaction(driver, semaphore, ccn, dcn, tcn, fd, ft, td, tt)
    #return result

@app.get("/status")
async def get_status(card_number:str):
    result = await ctrl.status(driver,card_number)
    return result


# Web endpoints
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/login")
async def login_endpoint(card_number:str):
    result = await ctrl.login(driver,card_number)
    return result

@app.get("/refresh")
async def refresh_endpoint(card_number:str):
    result = await ctrl.awake(driver,card_number)
    return result




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
