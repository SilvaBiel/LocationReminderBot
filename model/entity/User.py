from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from model.entity.Base import Base
import hashlib


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    hashed_chat_id = Column(String)
    registration_date = Column(DateTime)

    geo_request_rate = Column(Integer)
    tasks_list = relationship("Task", back_populates="user")

    def __init__(self, chat_id: str):
        bytes_string_chat_id = str(chat_id).encode()
        self.hashed_chat_id = hashlib.md5(bytes_string_chat_id).hexdigest()
        now = datetime.now()
        self.registration_date = now.strftime("%d/%m/%Y %H:%M:%S")

