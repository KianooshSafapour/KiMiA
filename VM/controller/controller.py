import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import bot_father   # Assuming this module contains the coroutines
from utils.database_connector import AsyncDatabaseConnector
from asyncio import Queue, Semaphore
import httpx

DATABASE_URL = "sqlite+aiosqlite:///./database.sqlite3"  # Replace with your actual database URL
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
db_connector = AsyncDatabaseConnector(dbname="kimia_database", user="kimia", password="Kimia@1993")

db_update_semaphore = Semaphore(value=1)

async def login(driver,card_number):
    result = await bot_father.login(driver,card_number)
    return result

async def update(driver, destination_card, from_date:str=None, from_time:str=None, to_date:str=None, to_time:str=None):
    # Connect to the database
   # await db_connector.connect()
    # Create tables if they don't exist
   # await db_connector.create_tables_if_not_exist()
    print("###############updateupdateupdateupdateupdate####################")
    result = await bot_father.update_database(driver, destination_card, from_date, from_time, to_date, to_time)
    return result
async def status(driver,card_number):
    result =await bot_father.check_login(driver,card_number)
    return result

async def awake(driver,card_number):
    result =await bot_father.refresh(driver,card_number)
    return result
#function a
'''async def check_transaction(driver, customer_card, destination_card, transaction_code, from_date, from_time, to_date, to_time,):
    
        async with async_session() as session:
            # Replace the following with your actual database query using SQLAlchemy
            print("#################################check_transactioncheck_transactioncheck_transactioncheck_transaction#####################################")
            transaction = await session.execute(
                "SELECT * FROM transactions WHERE ccn = :customer_card AND acn = :destination_card AND tcn = :transaction_code",
                {
                    "customer_card": customer_card,
                    "destination_card": destination_card,
                    "transaction_code": transaction_code,
                   
                }
            )
            result = transaction.fetchall()
            print(f"########################################################{result}")
            if result and len(result) > 0:
                return result[0]  #
            else:
                if not result:
                    await request_queue.put((customer_card, destination_card, transaction_code, from_date, from_time, to_date, to_time))

                # If no transactions found, run the update function and check again
                update_result=await update(driver, db_update_semaphore, destination_card, from_date, from_time, to_date, to_time)
                # Replace the following with your actual database query after update
                print(f"update_result::::::{update_result}")
                if(update_result['status']=='success'):
                    transaction = await session.execute(
                        "SELECT * FROM transactions WHERE ccn = :customer_card AND acn = :destination_card AND tcn = :transaction_code",
                        {
                            "customer_card": customer_card,
                            "destination_card": destination_card,
                            "transaction_code": transaction_code,
                    
                        }
                    )
                    result = transaction.fetchall()
                    return result
'''
# async def update_status(driver):
#     # Assuming update_status is a function in bot_father.py
#     await bot_father.update_status("available")

async def check_transaction(customer_card, destination_card, transaction_code):
        async with async_session() as session:
            try:
                # Replace the following with your actual database query using SQLAlchemy
                transaction = await session.execute(
                    "SELECT * FROM transactions WHERE ccn = :customer_card AND acn = :destination_card AND tcn = :transaction_code",
                    {
                        "customer_card": customer_card,
                        "destination_card": destination_card,
                        "transaction_code": transaction_code,
                    }
                )
                result = transaction.fetchall()
                return result
            except Exception as e:
                # Handle the exception (log, raise, etc.)
                print(f"Error during database query: {e}")
                return None  # Or raise an appropriate exception   

