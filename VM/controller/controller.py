import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import bot_father   # Assuming this module contains the coroutines

DATABASE_URL = "sqlite+aiosqlite:///./database.sqlite3"  # Replace with your actual database URL
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

async def login(driver):
    result = await bot_father.login(driver)
    return result

async def update(driver, semaphore, destination_card, from_date, from_time, to_date, to_time):
    result = await bot_father.update_database(driver, semaphore, destination_card, from_date, from_time, to_date, to_time)
    return result

async def awake(driver):
    result =await bot_father.refresh(driver)
    return result

async def check_transaction(driver, semaphore, customer_card, destination_card, transaction_code, from_date, from_time, to_date, to_time,):
    async with semaphore:
        async with async_session() as session:
            # Replace the following with your actual database query using SQLAlchemy
            transaction = await session.execute(
                "SELECT * FROM transactions WHERE customer_card = :customer_card AND destination_card = :destination_card "
                "AND transaction_code = :transaction_code AND date >= :from_date AND time >= :from_time "
                "AND date <= :to_date AND time <= :to_time",
                {
                    "customer_card": customer_card,
                    "destination_card": destination_card,
                    "transaction_code": transaction_code,
                    "from_date": from_date,
                    "from_time": from_time,
                    "to_date": to_date,
                    "to_time": to_time,
                }
            )
            result = transaction.fetchall()

            if result:
                return result
            else:
                # If no transactions found, run the update function and check again
                await update(driver, semaphore, destination_card, from_date, from_time, to_date, to_time)
                # Replace the following with your actual database query after update
                transaction = await session.execute(
                    "SELECT * FROM transactions WHERE customer_card = :customer_card AND destination_card = :destination_card "
                    "AND transaction_code = :transaction_code AND date >= :from_date AND time >= :from_time "
                    "AND date <= :to_date AND time <= :to_time",
                    {
                        "customer_card": customer_card,
                        "destination_card": destination_card,
                        "transaction_code": transaction_code,
                        "from_date": from_date,
                        "from_time": from_time,
                        "to_date": to_date,
                        "to_time": to_time,
                    }
                )
                result = transaction.fetchall()
                return result

# async def update_status(driver):
#     # Assuming update_status is a function in bot_father.py
#     await bot_father.update_status("available")