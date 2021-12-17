from model.entity.base import Session
from model.entity.task import Task
from sqlalchemy import delete, select


class TaskDao:

    def __init__(self):
        self.session = Session

    def get_all_tasks(self) -> list:
        all_tasks_list = self.session.query(Task).all()
        self.session.commit()
        return all_tasks_list

    def get_active_tasks(self) -> list:
        active_tasks_list = self.session.query(Task).filter(Task.state == "active")
        self.session.commit()
        return active_tasks_list

    def get_completed_tasks(self) -> list:
        active_tasks_list = self.session.query(Task).filter(Task.state == "completed")
        self.session.commit()
        return active_tasks_list

    def save_task(self, task: Task):
        self.session.add(task)
        self.session.commit()

    def delete_task_by_id(self, task_id: int) -> bool:
        statement = delete(Task).where(Task.id == task_id)
        result = self.session.execute(statement)

    def edit_task(self, task: Task):
        self.session.add(task)
        self.session.commit()

    def get_task_by_id(self, task_id: int) -> Task:
        statement = select(Task).where(Task.id == task_id)
        result = self.session.execute(statement)
        tasks = result.scalars().all()
        if tasks:
            return tasks[0]
        else:
            # TODO: LOG NOTHING IS FOUND
            pass