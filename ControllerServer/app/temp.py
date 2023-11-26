from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from random import choice

def get_random_ready_account_card(connection_string):
    engine = create_engine(connection_string)

    Session = sessionmaker(bind=engine)

    try:
        with Session() as session:
            # Select a random record from the nodes table with status "ready"
            result = session.execute(text("SELECT account_number FROM nodes WHERE status = 'ready' ORDER BY RAND() LIMIT 1;"))
            node_result = result.fetchone()

            if node_result:
                account_number = node_result[0]

                # Check if the account exists in the accounts table
                result = session.execute(text("SELECT card_number FROM accounts WHERE account_number = :account_number;"), {'account_number': account_number})
                account_result = result.fetchone()

                if account_result:
                    card_number = account_result[0]
                    return card_number

    except SQLAlchemyError as e:
        print(f"SQLAlchemy Error: {e}")
    finally:
        engine.dispose()

    return None

# Example usage
connection_string = "mysql+pymysql://username:password@localhost:3306/srvr"
result = get_random_ready_account_card(connection_string)

if result:
    print(f"Random ready account card number: {result}")
else:
    print("No ready account found.")
