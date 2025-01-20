import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String, Integer,Float,Boolean,DateTime, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# Initialize Base
Base = declarative_base()

load_dotenv()

# Load environment variables for DB connection
server_name = os.getenv("SERVER_NAME")
server_port = os.getenv("SERVER_PORT")
username = os.getenv("DB_USERNAME")
password = os.getenv("PASSWORD")
database_name = os.getenv("DATABASE_NAME")
ssl_mode = os.getenv("SSL_MODE")
endpoint_id = os.getenv("ENDPOINT_ID")

# Construct the connection string
connection_string = (
    f"postgresql+psycopg2://{username}:{password}@{server_name}:{server_port}/{database_name}"
    f"?sslmode={ssl_mode}&options=endpoint%3D{endpoint_id}"
)

# Create engine
engine = create_engine(connection_string)

# Define the session
Session = sessionmaker(bind=engine)
db_session = Session()  # Renamed session to db_session

# Define the ManualSFS model
class ManualSFS(Base):
    __tablename__ = "manual_SFS"
    ASIN = Column(String, primary_key=True, nullable=False)

# Define the User model
class User(Base):
    __tablename__ = 'NEW_USER_REGISETER'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)

# class AtoaReport(Base):
#     __tablename__ = 'Final_UK_USA_5M_common'

class AtoaReport(Base):
    __tablename__ = 'Final_UK_USA_5M_common'
    id = Column(Integer, primary_key=True, autoincrement=True)  # Add a primary key
    ASIN = Column(String)
    Brand = Column(String)
    Title = Column(String)
    existsInUk = Column(String)  # Assuming this is a string; adjust if necessary
    hasBeenProcessed = Column(Boolean)
    profit = Column(Float)  # Assuming profit is a float; adjust if necessary
    roi = Column(Float)     # Assuming ROI is a float; adjust if necessary
    ukAmazonCurrent = Column(Float)
    ukAvailableOnAmazon = Column(String)  # Assuming this is a string
    ukBuyBoxPrice = Column(Float)
    ukPackageWeight = Column(Float)
    updatedAt = Column(DateTime)
    usAvgBb360Day = Column(Float)
    usAvgBb90Day = Column(Float)
    usBsrDrop = Column(Float)
    usBuyBoxPrice = Column(Float)
    usFbaFee = Column(Float)
    usReferralFee = Column(Float)
# Create tables
Base.metadata.create_all(engine)
