import random
import aiohttp
import asyncio
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    card_number = Column(String)
    host_id = Column(Integer, ForeignKey('nodes.id'))

class Node(Base):
    __tablename__ = 'nodes'
    id = Column(Integer, primary_key=True)
    ip = Column(String)
    status = Column(String)

# Database configuration
DATABASE_URL = "mysql+aiomysql://root:!QAZ2wsx#E@localhost/srvr"
engine = create_engine(DATABASE_URL, echo=True, future=True)

async def check_status(card_number, session):
    async with session.begin() as db:
        account = await db.execute(Account.select().where(Account.card_number == card_number))
        account_record = account.scalar()

        if account_record:
            host_id = account_record.host

            node = await db.execute(Node.select().where(Node.id == host_id))
            node_record = node.scalar()

            if node_record:
                node_ip = node_record.ip

                async with aiohttp.ClientSession() as client_session:
                    async with client_session.get(f"http://{node_ip}/check_status") as response:
                        if response.status == 200:
                            response_json = await response.json()
                            if response_json["status"] == "ready":
                                return "active"
                            else:
                                await update_node_status(node_ip, "offline", session)
                                return "inactive"
                        else:
                            return "inactive"
            else:
                return "inactive"
        else:
            return "inactive"

async def select_worker(session):
    async with session.begin() as db:
        ready_nodes = await db.execute(Node.select().where(Node.status == 'ready'))
        ready_nodes_list = await ready_nodes.fetchall()

        if ready_nodes_list:
            selected_node = random.choice(ready_nodes_list)
            node_ip = selected_node.ip

            status = await check_status(node_ip, session)
            if status == "active":
                # If the status is "active", retrieve and return the card_number
                account = await db.execute(Account.select().where(Account.host_id == selected_node.id))
                card_number = account.scalar().card_number
                return f"Active worker with card number: {card_number}"
            else:
                return "Selected worker is not active"
        else:
            return "No ready nodes available"

async def update_node_status(node_ip, status, session):
    async with session.begin() as db:
        await db.execute(Node.update().where(Node.ip == node_ip).values(status=status))

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
