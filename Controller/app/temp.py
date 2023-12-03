from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Replace these values with your actual database credentials
db_url = 'mysql+mysqlconnector://root:!QAZ2wsx#E@localhost:3306/srvr'

# SQLAlchemy engine and session setup
engine = create_engine(db_url)
Base = declarative_base()
metadata = MetaData(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()

# Define the Node model
class Node(Base):
    __tablename__ = 'nodes'

    id = Column(Integer, primary_key=True)
    name = Column(String(16))
    ip = Column(String(15))
    username = Column(String(16))
    password = Column(String(64))
    secret = Column(String(256))
    config = Column(Integer)
    status = Column(String(20))

# Create the nodes table if it does not exist
Base.metadata.create_all()

# Sample data to be inserted into the nodes table
sample_data = [
    Node(id=3, name='Node3', ip='192.168.1.3', username='user3', password='password', secret='secret', config=0, status="active"),
    Node(id=4, name='Node4', ip='192.168.1.4', username='user4', password='pass', secret='secret', config=0, status="offline"),
    Node(id=5, name='Node5', ip='192.168.1.5', username='user5', password='pass', secret='secret', config=0, status="active"),
    Node(id=6, name='Node6', ip='192.168.1.6', username='user6', password='pass', secret='secret', config=0, status="online"),
    Node(id=7, name='Node7', ip='192.168.1.7', username='user7', password='pass', secret='secret', config=0, status="active"),
    Node(id=8, name='Node8', ip='192.168.1.8', username='user8', password='pass', secret='secret', config=0, status="ready"),
    Node(id=9, name='Node9', ip='192.168.1.9', username='user9', password='pass', secret='secret', config=0, status="active"),
    Node(id=10, name='Node10', ip='192.168.1.10', username='user10', password='pass', secret='secret', config=0, status="ready"),
    Node(id=11, name='Node11', ip='192.168.1.11', username='user11', password='pass', secret='secret', config=0, status="active"),
    Node(id=12, name='Node12', ip='192.168.1.12', username='user12', password='pass', secret='secret', config=0, status="offline"),
    Node(id=13, name='Node13', ip='192.168.1.13', username='user13', password='pass', secret='secret', config=0, status="offline"),
    Node(id=14, name='Node14', ip='192.168.1.14', username='user14', password='pass', secret='secret', config=0, status="online"),
    Node(id=15, name='Node15', ip='192.168.1.15', username='user15', password='pass', secret='secret', config=0, status="active"),
    Node(id=16, name='Node16', ip='192.168.1.16', username='user16', password='pass', secret='secret', config=0, status="ready"),
    Node(id=17, name='Node17', ip='192.168.1.17', username='user17', password='pass', secret='secret', config=0, status="online"),
    Node(id=18, name='Node18', ip='192.168.1.18', username='user18', password='pass', secret='secret', config=0, status="active"),
    Node(id=19, name='Node19', ip='192.168.1.19', username='user19', password='pass', secret='secret', config=0, status="ready"),
    Node(id=20, name='Node20', ip='192.168.1.20', username='user20', password='password', secret='secret', config=0, status="active")
    # Add more rows as needed
]

# Insert sample data into the nodes table
session.bulk_save_objects(sample_data)
session.commit()

# Query and print the contents of the nodes table
nodes = session.query(Node).all()
for node in nodes:
    print(f"ID: {node.id}, Name: {node.name}, IP: {node.ip}, Username: {node.username}, Status: {node.status}")

# Close the session
session.close()
