from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, Column, String, DateTime, Integer, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
import httpx
from datetime import datetime

# SQLite database connection
DATABASE_URL = "sqlite:///./database.sqlite3"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define Connection model
class Connection(Base):
    __tablename__ = "connections"
    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String, index=True)
    date = Column(String)
    time = Column(String)
    log = Column(String)

# Define Config model
class Config(Base):
    __tablename__ = "configs"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    config = Column(String)

Base.metadata.create_all(bind=engine)

app = FastAPI()

class CardNumberResponse(BaseModel):
    card_number: str

class RequestModel(BaseModel):
    client_ip: str
    log: str

@app.post("/api")
async def process_request(request: Request, request_model: RequestModel):
    # Log the request in the connections table
    connection_data = {
        "ip": request_model.client_ip,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M:%S"),
        "log": request_model.log,
    }
    with SessionLocal() as db:
        db.add(Connection(**connection_data))
        db.commit()

    # Read controller server IP and config from configs table
    with SessionLocal() as db:
        query = db.execute(text("SELECT config FROM configs WHERE name = 'host'"))
        host_config = query.scalar()

    if not host_config:
        raise HTTPException(status_code=500, detail="Host config not found")

    # Send a request to the host's API
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{host_config}/get_card_number")

    # Process the response from the host's API
    try:
        card_number_response = CardNumberResponse.parse_raw(response.text)
        return JSONResponse(content={"card_number": card_number_response.card_number})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing host response: {str(e)}")
