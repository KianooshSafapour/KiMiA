import array
import random
import aiohttp
import asyncio
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select, update
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

Base = declarative_base()

class Node(Base):
    __tablename__ = 'nodes'

    id = Column(Integer, primary_key=True)
    name = Column(String(16))
    ip = Column(String(15))
    username = Column(String(16))
    password = Column(String(64))
    secret = Column(String(256))
    config = Column(Integer)  # Assuming tinyint corresponds to Integer
    status = Column(String(20))

class Account(Base):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True)
    name = Column(String(16))
    number = Column(String(20))
    bank = Column(String(20))
    card = Column(String(16))
    username = Column(String(16))
    password = Column(String(64))
    host = Column(Integer)
    status = Column(String(50))


# Database configuration
DATABASE_URL = "sqlite+aiosqlite:///.././database.sqlite3"
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def check_status(card_number, session):
    account = await session.execute(select(Account).where(Account.card == card_number))
    account_record = account.scalar()

    if account_record:
        host_id = account_record.host

        node = await session.execute(select(Node).where(Node.id == host_id))
        node_record = node.scalar()

        if node_record:
            node_ip = node_record.ip
            node_id = node_record.id
            try:
                async with aiohttp.ClientSession() as client_session:
                    async with client_session.get(f"http://{node_ip}/status") as response:
                        if response.status == 200:
                            response_json = await response.json()
                            if response_json["status"] == "ready":
                                return response_json
                            else:
                                return "crap inactive"
                        else:
                            await update_node_status(node_id, "offline", session)
                            return "inactive"

            except:
                await update_node_status(node_id, "offline", session)
                return "offline"
        else:
            await update_node_status(node_id, "offline", session)
            return "inactive"
    else:
        await update_node_status(node_id, "offline", session)
        return "inactive"

async def select_worker(session):
    # async with session.begin() as db:
    #     ready_nodes = await db.execute(Node.select().where(Node.status == 'ready'))
    #     ready_nodes_list = await ready_nodes.fetchall()

    #     for selected_node in ready_nodes_list:
    #         node_ip = selected_node.ip
    #         status = await check_status(node_ip, session)
    #         account = await db.execute(Account.select().where(Account.host == selected_node.id))
    #         card_number = account.scalar().card_number
    #         if card_number:
    #             return card_number


    #         if status == "active":
    #             # If the status is "active", retrieve and return the card_number
    #             account = await db.execute(Account.select().where(Account.host == selected_node.id))
    #             card_number = account.scalar().card_number
    #             if card_number:
    #                 return card_number
    #         else:
    #             # Update the node status to offline if not ready
    #             await update_node_status(node_ip, "offline", session)

    #     return "No active workers found"
    async with session.begin() as db:
        cards = []
        ready_nodes = await session.execute(select(Node).where(Node.status == 'ready'))
        ready_nodes_list = ready_nodes.fetchall()


        for selected_node in ready_nodes_list:
            worker_node = selected_node["Node"].id
            account = await session.execute(select(Account).where(Account.host == selected_node["Node"].id))
            selected_account = account.scalars().all()
            if selected_account:
                cards.append(selected_account)

        if cards:
            card_number = random.choice(cards)
            return card_number[0].card
        return "No active workers found"

async def update_node_status(node_id, status, session):
    await session.execute(update(Node).where(Node.id == node_id).values(status=status))

async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)() as session:
        card_number = "1234567890123456"
        status = await check_status(card_number, session)
        print(f"Status for card number {card_number}: {status}")

        selected_worker_status = await select_worker(session)
        print(f"Selected worker status: {selected_worker_status}")

if __name__ == "__main__":
    asyncio.run(main())
