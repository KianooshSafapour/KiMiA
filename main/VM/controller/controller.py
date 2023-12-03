import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import bot_father  # Assuming this module contains the coroutines


DATABASE_URL = "sqlite+aiosqlite:///./database.sqlite3"  # Replace with your actual database URL
engine = create_async_engine(DATABASE_URL, echo=True)

async_session = sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)

async def login(semaphore):
    # Login and update status
    await bot_father.login()
    async with semaphore:
        await update_status()

async def update_status():
    # Assuming update_status is a function in bot_father.py
    await bot_father.update_status("available")

async def update(destination_card, from_date, from_time, to_date, to_time, semaphore):
    # Call update_database function with parameters and check the return
    success = await bot_father.update_database(semaphore, destination_card, from_date, from_time, to_date, to_time)
    if success:
        print("Update successful")
    else:
        print("Update failed")

async def awake():
    # Run refresh coroutine if no calls made to bot_father.py for 15 minutes
    await asyncio.sleep(900)  # 15 minutes
    await bot_father.refresh()

async def check_transaction(customer_card, destination_card, transaction_code, from_date, from_time, to_date, to_time, semaphore):
    async with semaphore:
        async with async_session() as session:
            # Replace the following with your actual database query using SQLAlchemy
            result = await session.execute(
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
            result = result.fetchall()

            if result:
                # Transaction found
                return result
            else:
                # If no transactions found, run the update function and check again
                await update(destination_card, from_date, from_time, to_date, to_time, semaphore)
                # Replace the following with your actual database query after update
                result_after_update = await session.execute(
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
                result_after_update = result_after_update.fetchall()

                if result_after_update:
                    return result_after_update
                else:
                    return "No transaction found"
                

async def status():
    # Call check_login method and receive the status
    status = await bot_father.check_login()
    print("Bot status:", status)

async def main():
    semaphore = asyncio.Semaphore(1)  # Initialize with value 1 for mutual exclusion

    # Example usage
    await login(semaphore)
    await update("1234567890123456", "2023-01-01", "12:00", "2023-01-02", "14:00", semaphore)
    await awake()
    result = await check_transaction("1111222233334444", "1234567890123456", "ABCDE12345",
                                     "2023-01-01", "12:00", "2023-01-02", "14:00", semaphore)
    print(result)
    await status()

# Run the main coroutine
asyncio.run(main())
