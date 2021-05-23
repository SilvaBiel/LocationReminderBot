from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy import Table, ForeignKey
from sqlalchemy.orm import relationship

from Base import Base
from User import User

users_tasks_association = Table("users_tasks", Base.metadata,
                                Column("user_id", Integer, ForeignKey("user.id")),
                                Column("task_id"), Integer, ForeignKey("task.id"))


class Task(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    header = Column(String)
    body = Column(String)
    # location =
    radius = Column(Integer)
    datetime = Column(DateTime)
    state = Column(String)
    user = relationship("User", secondary=users_tasks_association)

    def __init__(self, header: str, body: str, user: User):
        self.header = header
        self.body = body
        self.user = user
