from sqlalchemy import Column, String, Integer, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from model.entity.Base import Base
from model.entity.User import User


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    header = Column(String)
    body = Column(String)
    location_latitude = Column(Numeric)
    location_longitude = Column(Numeric)
    radius = Column(Integer)
    datetime = Column(DateTime)
    state = Column(String)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="tasks_list")

    def __init__(self, header: str, body: str, user: User):
        self.header = header
        self.body = body
        self.user = user
        self.user_id = user.id

