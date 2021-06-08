from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy import Table, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from model.entity.Base import declarative_base

users_tasks_association = Table("users_tasks", declarative_base.metadata,
                                Column("user_id", Integer, ForeignKey("user.id")),
                                Column("task_id", Integer, ForeignKey("task.id")))


class User(declarative_base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    login = Column(String)
    password = Column(String)
    registration_date = Column(DateTime)

    geo_request_rate = Column(Integer)
    tasks_list = relationship("Task", secondary=users_tasks_association)

    def __init__(self, login: str, password: str):
        self.login = login
        self.password = password

        now = datetime.now()
        self.registration_date = now.strftime("%d/%m/%Y %H:%M:%S")
