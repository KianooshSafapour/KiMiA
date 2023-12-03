from fastapi import FastAPI, Depends, HTTPException, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from typing import Optional
import controller as ctrl

app = FastAPI()

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Database setup (assuming SQLite3)
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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


# API Endpoints
@app.post("/check_transaction")
async def check_transaction_endpoint(
    customer_card: str,
    destination_card: str,
    transaction_card: str,
    from_date: datetime,
    from_time: datetime,
    to_date: datetime,
    to_time: datetime,
):
    result = ctrl.check_transaction(
        customer_card,
        destination_card,
        transaction_card,
        from_date,
        from_time,
        to_date,
        to_time,
    )
    return {"result": result}


@app.get("/status")
async def get_status(db: Session = Depends(get_db)):
    current_status = ctrl.status(db)
    return {"status": current_status}


# Web endpoints
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.post("/login")
async def login_endpoint(card_number: str = Form(...), db: Session = Depends(get_db)):
    login_result = ctrl.login(card_number, db)
    return {"login_result": login_result}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
