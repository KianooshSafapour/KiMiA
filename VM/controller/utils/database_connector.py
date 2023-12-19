import asyncpg

class AsyncDatabaseConnector:
    def __init__(self, dbname, user, password, host="localhost", port="5432"):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection = None

    async def connect(self):
        self.connection = await asyncpg.connect(
            user=self.user,
            password=self.password,
            database=self.dbname,
            host=self.host,
            port=self.port
        )

    async def create_tables_if_not_exist(self):
        await self.create_configs_table()
        await self.create_logs_table()
        await self.create_settings_table()
        await self.create_transactions_table()

    async def create_configs_table(self):
        if not await self.table_exists("configs"):
            config_table_query = """
            CREATE TABLE configs (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                config VARCHAR(255)
            );
            """
            await self.create_table(config_table_query)

    async def create_logs_table(self):
        if not await self.table_exists("logs"):
            logs_table_query = """
            CREATE TABLE logs (
                id SERIAL PRIMARY KEY,
                time TIMESTAMP,
                level VARCHAR(50),
                message TEXT
            );
            """
            await self.create_table(logs_table_query)

    async def create_settings_table(self):
        if not await self.table_exists("settings"):
            settings_table_query = """
            CREATE TABLE settings (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                value VARCHAR(255)
            );
            """
            await self.create_table(settings_table_query)

    async def create_transactions_table(self):
        if not await self.table_exists("transactions"):
            transactions_table_query = """
            CREATE TABLE transactions (
                id SERIAL PRIMARY KEY,
                ccn VARCHAR(16),
                acn VARCHAR(16),
                tcn VARCHAR(16),
                date DATE,
                time TIME
            );
            """
            await self.create_table(transactions_table_query)

    async def table_exists(self, table_name):
        result = await self.connection.fetchrow(
            "SELECT 1 FROM information_schema.tables WHERE table_name = $1;", table_name
        )
        return result is not None
    
    async def insert_transaction(self, ccn, acn, tcn, date, time):
        insert_query = """
        INSERT INTO transactions (ccn, acn, tcn, date, time)
        VALUES ($1, $2, $3, $4, $5);
        """
        await self.execute_update(insert_query, ccn, acn, tcn, date, time)

    async def create_table(self, table_query):
        async with self.connection.transaction():
            await self.connection.execute(table_query)

    async def execute_query(self, query, *args):
        return await self.connection.fetch(query, *args)

    async def execute_update(self, query, *args):
        async with self.connection.transaction():
            await self.connection.execute(query, *args)

    async def close_connection(self):
        await self.connection.close()
