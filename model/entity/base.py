from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# TODO: CHANGE LINK TO ENVIROMENT VARIABLE
Engine = create_engine("postgresql://postgres:123456@127.0.0.1:5432/reminder_assistance_db", echo=True)
Session = sessionmaker(bind=Engine)
Session = Session()
Base = declarative_base()

