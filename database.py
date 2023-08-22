from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


username = "root"
password = "Karthik24!"  # Replace with your actual password
host = "127.0.0.1"
port = "3306"
database_name = "loanapplication"
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database_name}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)




"""
SQLALCHEMY_DATABASE_URL = "sqlite:///.loanapp.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL,connect_args = {"check_same_thread":False })
"""
SessionLocal = sessionmaker(autocommit = False, autoflush = False,bind = engine)

Base =declarative_base()
