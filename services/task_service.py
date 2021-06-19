from dao.task_dao import *
import re
from geopy.geocoders import Nominatim
from services.user_service import UserService


class TaskService:
    task_dao = TaskDao()
    bot = None
    chat_id_tasks_cache = dict()
    geo_locator = Nominatim(user_agent="taskReminderBot")
    user_service = UserService()

    def add_task_header_step(self, message):
        cid = message.chat.id
        header = message.text
        if header:
            msg = self.bot.reply_to(message, "Great, now please enter task body.")
            self.bot.register_next_step_handler(msg, self.add_task_body_step)
            self.chat_id_tasks_cache[cid] = header
        else:
            msg = self.bot.reply_to(message, "Header is empty, please provide correct header.")
            self.bot.register_next_step_handler(msg, self.add_task_body_step)

    def add_task_body_step(self, message):
        cid = message.chat.id
        body = message.text
        user = self.user_service.get_user_by_chat_id(cid)
        if body:
            msg = self.bot.reply_to(message, "Fantastic, task is ready, if you like to add location or date reminder, \
                                         please write /datetime or /location or /skip to finish and save created task.")
            self.bot.register_next_step_handler(msg, self.add_location_or_datetime_reminder)
            task = Task(self.chat_id_tasks_cache[cid], body, user)
            self.chat_id_tasks_cache[cid] = task
        else:
            msg = self.bot.reply_to(message, "Task body is empty, please provide correct task body.")
            self.bot.register_next_step_handler(msg, self.add_task_body_step)

    def add_location_or_datetime_reminder(self, message):
        text = message.text
        cid = message.chat.id
        task = self.chat_id_tasks_cache[cid]
        if text == "/skip":
            self.task_dao.save_task(task)
            self.bot.reply_to(message, "Great, %s task was successfully saved." % message.chat.first_name)
        elif text == "/location":
            msg = self.bot.reply_to(message, "%s please enter desired location reminder for task. "
                                             "You have two options:"
                                             "1) latitude, longitude"
                                             "2) or City, Street, Home"
                                             "arguments must be separated by spaces." % message.chat.first_name)
            self.bot.register_next_step_handler(msg, self.add_location_to_task)
        elif text == "/datetime":
            msg = self.bot.reply_to(message, "%s please enter time, "
                                             "day, month of reminding time in format like this: "
                                             "HH:mm DD:MM." % message.chat.first_name)
            self.bot.register_next_step_handler(msg, self.add_datetime_to_task)

    def add_location_to_task(self, message):
        location = message.text
        cid = message.chat.id
        task = self.chat_id_tasks_cache[cid]
        if not re.search('[a-zA-Z]', location):
            location_arguments = location.split(" ")
            if len(location) == 3:
                latitude = location_arguments[0]
                longitude = location_arguments[1]
                task.latitude = latitude
                task.longitude = longitude
                self.check_founded_location_step(message)
        elif location:
            location = self.geo_locator.geocode(location)
            if location:
                task.latitude = location.latitude
                task.longitude = location.longitude
                self.check_founded_location_step(message)
            else:
                msg = self.bot.reply_to(message, "Sorry, specified location was not found, "
                                                 "please check entered address and try again")
                self.bot.register_next_step_handler(msg, self.add_location_to_task)

        self.bot_location_wrong_syntax(message)

    def bot_location_wrong_syntax(self, message):
        self.bot.reply_to("Wrong syntax.")
        msg = self.bot.reply_to(message, "%s please enter desired location reminder for task. "
                                         "You have two options:"
                                         "1) latitude, longitude  and notification radius in metres,"
                                         "2) or City, Street, Home "
                                         "arguments must be separated by spaces." % message.chat.first_name)
        self.bot.register_next_step_handler(msg, self.finish_location_adding_to_task)

    def finish_location_adding_to_task(self, message):
        text = message.text
        cid = message.chat.id
        task = self.chat_id_tasks_cache[cid]
        if text == "yes":
            self.task_dao.save_task(task)

    def check_founded_location_step(self, message):
        cid = message.chat.id
        task = self.chat_id_tasks_cache[cid]
        location = self.geo_locator.revers(task.latitude, task.longitude)
        msg = self.bot.reply_to(message, "Please check that founded location is correct,"
                                         "founded location:%s" % location)
        self.bot.register_next_step_handler(msg, self.add_location_to_task)

    def add_datetime_to_task(self, message):
        datetime = message.text
