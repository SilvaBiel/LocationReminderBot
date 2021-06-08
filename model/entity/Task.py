from sqlalchemy import Column, String, Integer, DateTime, Numeric
from sqlalchemy import Table, ForeignKey
from sqlalchemy.orm import relationship

from model.entity.Base import declarative_base
from model.entity.User import User

declarative_base.metadata.clear()
users_tasks_association = Table("users_tasks", declarative_base.metadata,
                                Column("user_id", Integer, ForeignKey("user.id")),
                                Column("task_id", Integer, ForeignKey("task.id")))


class Task(declarative_base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    header = Column(String)
    body = Column(String)
    location_latitude = Column(Numeric)
    location_longitude = Column(Numeric)
    radius = Column(Integer)
    datetime = Column(DateTime)
    state = Column(String)
    user = relationship("User", secondary=users_tasks_association)

    def __init__(self, header: str, body: str, user: User):
        self.header = header
        self.body = body
        self.user = user
