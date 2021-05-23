from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlarchemy.orm import sessionmaker

engine = create_engine("postgresql://postgres:123@localhost:5432/reminder_assistance_db")
Session = sessionmaker(bind=engine)

Base = declarative_base()