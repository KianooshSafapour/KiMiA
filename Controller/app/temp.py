# from sqlalchemy import create_engine, text
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.exc import SQLAlchemyError
# from random import choice

# def get_random_ready_account_card(connection_string):
#     engine = create_engine(connection_string)

#     Session = sessionmaker(bind=engine)

#     try:
#         with Session() as session:
#             # Select a random record from the nodes table with status "ready"
#             result = session.execute(text("SELECT account_number FROM nodes WHERE status = 'ready' ORDER BY RAND() LIMIT 1;"))
#             node_result = result.fetchone()

#             if node_result:
#                 account_number = node_result[0]

#                 # Check if the account exists in the accounts table
#                 result = session.execute(text("SELECT card_number FROM accounts WHERE account_number = :account_number;"), {'account_number': account_number})
#                 account_result = result.fetchone()

#                 if account_result:
#                     card_number = account_result[0]
#                     return card_number

#     except SQLAlchemyError as e:
#         print(f"SQLAlchemy Error: {e}")
#     finally:
#         engine.dispose()

#     return None

# # Example usage
# connection_string = "mysql+pymysql://username:password@localhost:3306/srvr"
# result = get_random_ready_account_card(connection_string)

# if result:
#     print(f"Random ready account card number: {result}")
# else:
#     print("No ready account found.")


import random
import requests
import mariadb
from mariadb import connect, Error

# Function to check the status of a card number
def check_status(card_number):
    # Connect to the MariaDB database
    try:
        conn = connect(
            user="your_username",
            password="your_password",
            host="your_host",
            database="your_database"
        )
        cursor = conn.cursor()

        # Query to find the account record for the given card_number
        cursor.execute(f"SELECT * FROM accounts WHERE card_number = {card_number}")
        account_record = cursor.fetchone()

        if account_record:
            # Extract the host value from the account record
            host_id = account_record[2]

            # Query to find the node record using the host_id
            cursor.execute(f"SELECT * FROM nodes WHERE id = {host_id}")
            node_record = cursor.fetchone()

            if node_record:
                # Extract the IP address from the node record
                node_ip = node_record[1]

                # Send a request to the check_status endpoint of the node
                response = requests.get(f"http://{node_ip}/check_status")

                if response.status_code == 200 and response.json()["status"] == "ready":
                    return "active"
                else:
                    # If the response is not ready, update the node status to offline
                    update_node_status(node_ip, "offline")
                    return "inactive"
            else:
                return "inactive"
        else:
            return "inactive"

    except Error as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

# Function to select a random worker with "ready" status
def select_worker():
    try:
        conn = connect(
            user="your_username",
            password="your_password",
            host="your_host",
            database="your_database"
        )
        cursor = conn.cursor()

        # Query to find nodes with "ready" status
        cursor.execute("SELECT * FROM nodes WHERE status = 'ready'")
        ready_nodes = cursor.fetchall()

        if ready_nodes:
            # Choose a random node
            selected_node = random.choice(ready_nodes)

            # Extract the IP address from the selected node
            node_ip = selected_node[1]

            # Use check_status function to find and return the status
            return check_status(node_ip)
        else:
            return "No ready nodes available"

    except Error as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

# Function to update the status of a node
def update_node_status(node_ip, status):
    try:
        conn = connect(
            user="your_username",
            password="your_password",
            host="your_host",
            database="your_database"
        )
        cursor = conn.cursor()

        # Update the status of the node
        cursor.execute(f"UPDATE nodes SET status = '{status}' WHERE ip = '{node_ip}'")
        conn.commit()

    except Error as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

# Example usage
card_number = "1234567890123456"
status = check_status(card_number)
print(f"Status for card number {card_number}: {status}")

selected_worker_status = select_worker()
print(f"Selected worker status: {selected_worker_status}")
