import httpx
from datetime import datetime
from faker import Faker
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./database.sqlite3"

# SQLAlchemy Model
Base = declarative_base()

class Log(Base):
    __tablename__ = "logs"
    id = Column(String(20), primary_key=True, index=True)
    time = Column(DateTime, default=datetime.utcnow)
    level = Column(String(8))
    message = Column(Text)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def generate_fake_request():
    fake = Faker()
    return {
        "customer_card": fake.credit_card_number(card_type="mastercard"),
        "destination_card": fake.credit_card_number(card_type="visa"),
        "transaction_number": fake.uuid4(),
        "confirmation_number": fake.uuid4(),
        "transaction_date": datetime.now().strftime("%Y-%m-%d"),
        "transaction_time": datetime.now().strftime("%H:%M:%S"),
        "details": fake.text(),
    }

def send_request(session, transaction_data, is_valid):
    api_url = "http://127.0.0.1:8000/process_transactions/"
    request_data = {"transactions": [transaction_data]} if is_valid else {"invalid_data": transaction_data}
    response = session.post(api_url, json=request_data)
    return response

def log_request_response(log_level, log_message, session, transaction_data, is_valid):
    log_id = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    db = SessionLocal()
    
    # Log the request
    request_log = Log(
        id=log_id,
        level=log_level,
        message=f"Request: {transaction_data}, Valid: {is_valid}",
    )
    db.add(request_log)
    db.commit()
    
    # Log the response
    response = send_request(session, transaction_data, is_valid)
    response_log = Log(
        id=log_id,
        level=log_level,
        message=f"Response: {response.status_code} - {response.json()}",
    )
    db.add(response_log)
    db.commit()

def simulate_requests(num_data_records, num_requests):
    fake = Faker()
    session = httpx.AsyncClient()

    # Randomly select data records from the transactions table
    selected_data_records = [generate_fake_request() for _ in range(num_data_records)]

    # Simulate both valid and invalid API requests
    with ThreadPoolExecutor(max_workers=num_requests) as executor:
        for _ in range(num_requests):
            transaction_data = random.choice(selected_data_records)
            is_valid = fake.boolean()
            log_level = "INFO" if is_valid else "ERROR"

            executor.submit(log_request_response, log_level, "API Request", session, transaction_data, is_valid)

    session.close()

if __name__ == "__main__":
    num_data_records = int(input("Enter the number of data records to select: "))
    num_requests = int(input("Enter the number of requests to simulate: "))

    simulate_requests(num_data_records, num_requests)
