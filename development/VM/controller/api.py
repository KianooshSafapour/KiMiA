from fastapi import FastAPI, Depends, HTTPException, Form, Request
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

app = FastAPI()

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

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
async def check_transaction_endpoint(ccn: str, dcn: str, tcn: str, fd: str, ft: str, td: str, tt: str):
    result = ctrl.check_transaction(driver, semaphore, ccn, dcn, tcn, fd, ft, td, tt)
    return result

@app.get("/status")
async def get_status():
    result = ctrl.status(driver)
    return result


# Web endpoints
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/login")
async def login_endpoint():
    result = await ctrl.login(driver)
    return result

@app.get("/refresh")
async def refresh_endpoint():
    result = await ctrl.awake(driver)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
