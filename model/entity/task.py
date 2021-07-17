from sqlalchemy import Column, String, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from model.entity.base import Base
from model.entity.user import User


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    header = Column(String)
    body = Column(String)
    location_latitude = Column(Numeric)
    location_longitude = Column(Numeric)
    radius = Column(Integer)
    state = Column(String)  # state = "active" or "done" string
    notification_happened = Column(bool)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="tasks_list")

    def __init__(self, header: str, body: str, user: User, radius: Integer = 1000):
        self.header = header
        self.body = body
        self.user = user
        self.radius = radius
        self.state = "active"
        self.notification_happened = False

    def set_attr(self, attribute_name, value):
        setattr(self, attribute_name, value)

