# TODO: write funcs to get all users, get user, edit user, delete user,

from dao.user_dao import UserDao
from model.entity.user import  User


class UserService:
    def __init__(self):
        self.user_dao = UserDao()

    def get_user_by_chat_id(self, user_chat_id: str):
        if user_chat_id:
            return self.user_dao.get_user_by_chat_id(user_chat_id)
        else:
            # TODO: APPLY LOG HERE
            pass

    def add_user(self, user: User):
        if User:
            self.user_dao.add_user(user)
