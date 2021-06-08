from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#TODO: CHANGE LINK TO ENVIROMENT VARIABLE
Engine = create_engine("postgresql://postgres:123@localhost:5432/reminder_assistance_db")
Session = sessionmaker(bind=Engine)

declarative_base = declarative_base()