from model.entity.base import Session
from model.entity.task import Task


class TaskDao:

    def __init__(self):
        self.session = Session()

    def get_all_tasks(self) -> list:
        all_tasks_list = self.session.query(Task).all()
        return all_tasks_list

    def get_active_tasks(self) -> list:
        active_tasks_list = self.session.query(Task).filter(Task.state == "active")
        return active_tasks_list

    def get_completed_tasks(self) -> list:
        active_tasks_list = self.session.query(Task).filter(Task.state == "completed")
        return active_tasks_list

    def save_task(self, task: Task):
        self.session.add(task)
        self.session.commit()

    def delete_task(self, task: Task):
        self.session.add(task)
        self.session.commit()

    def edit_task(self, task: Task):
        self.session.add(task)
        self.session.commit()
