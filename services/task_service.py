from dao.task_dao import TaskDao
import re
from geopy.geocoders import Nominatim
from services.user_service import UserService
from model.entity.task import Task
from services.logger_service import logger


class TaskService:
    task_dao = TaskDao()
    bot = None
    geo_locator = Nominatim(user_agent="taskReminderBot")
    user_service = UserService()
    chat_id_tasks_cache = dict()

    def add_task_header_step(self, message):

        """
        New task header creation step.
        """

        cid = message.chat.id
        header = message.text
        self.chat_id_tasks_cache = dict()
        if header:
            msg = self.bot.reply_to(message, "Great, now please enter task body.")
            self.bot.register_next_step_handler(msg, self.add_task_body_step)
            self.chat_id_tasks_cache[cid] = header
        elif header == "/cancel" or header == "cancel":
            pass
        else:
            msg = self.bot.reply_to(message, "Header is empty, please provide correct header.")
            self.bot.register_next_step_handler(msg, self.add_task_body_step)

    def add_task_body_step(self, message):

        """
        New task body creation step.
        """

        cid = message.chat.id
        body = message.text
        user = self.user_service.get_user_by_chat_id(cid)
        if isinstance(user, list):
            user = user[0]

        if body:
            msg = self.bot.reply_to(message, "Fantastic, task is almost ready, \n"
                                             "if you like to add location or date reminder,\n"
                                             "please select set /location, \n"
                                             "if you don't need this, select /skip to finish and save created task.")
            self.bot.register_next_step_handler(msg, self.add_location_reminder)
            header = self.chat_id_tasks_cache[cid]
            task = Task(header, body, user)
            self.save_task(task)
            self.chat_id_tasks_cache[cid] = task
        elif body == "/cancel" or body == "cancel":
            pass
        else:
            msg = self.bot.reply_to(message, "Task body is empty, please provide correct task body.")
            self.bot.register_next_step_handler(msg, self.add_task_body_step)

    def add_location_reminder(self, message):

        """
        Add location reminder to task step 1.
        """

        text = message.text
        cid = message.chat.id
        task = self.chat_id_tasks_cache[cid]
        if text == "/skip":
            self.save_task(task)
            self.bot.reply_to(message, "Great, %s task was successfully saved." % message.chat.first_name)
        elif text == "/location":
            msg = self.bot.reply_to(message, "%s please enter desired location reminder for task. "
                                             "1) latitude, longitude"
                                             "2) or City, Street, Home"
                                             "arguments must be separated by spaces." % message.chat.first_name)
            self.bot.register_next_step_handler(msg, self.add_location_to_task)
        elif text == "/cancel" or text == "cancel":
            pass
        else:
            msg = self.bot.reply_to(message, "Wrong syntax, try again")
            self.bot.register_next_step_handler(msg, self.add_location_reminder)

    def add_location_to_task(self, message):

        """
        Add location reminder to task step 2.
        """

        location = message.text
        print("LOCATION"+location)
        cid = message.chat.id
        task = self.chat_id_tasks_cache[cid]
        if re.match(r'^(-?\d+(\.\d+)?),\s*(-?\d+(\.\d+)?)$', location):
            location_arguments = location.split(",")
            if len(location_arguments) == 2:
                latitude = location_arguments[0].strip()
                longitude = location_arguments[1].strip()
                task.location_latitude = latitude
                task.location_longitude = longitude
                self.check_founded_location_step(message)
        elif location:
            location = self.geo_locator.geocode(location)
            if location:
                task.location_latitude = location.latitude
                task.location_longitude = location.longitude
                self.check_founded_location_step(message)
            else:
                msg = self.bot.reply_to(message, "Sorry, specified location was not found, "
                                                 "please check entered address and try again")
                self.bot.register_next_step_handler(msg, self.add_location_to_task)
        elif location == "/cancel" or location == "cancel":
            pass
        else:
            self.bot_location_wrong_syntax(message)

    def bot_location_wrong_syntax(self, message):

        """
        Wrong syntax message during location adding to task.
        """

        self.bot.reply_to(message, "Wrong syntax.")
        msg = self.bot.reply_to(message, "%s please enter desired location reminder for task. "
                                         "You have two options:"
                                         "1) latitude, longitude  and notification radius in metres,"
                                         "2) or City, Street, Home "
                                         "arguments must be separated by spaces." % message.chat.first_name)
        self.bot.register_next_step_handler(msg, self.add_location_to_task)

    def finish_location_adding_to_task(self, message):

        """
        Finishing location adding to task.
        """

        text = message.text
        cid = message.chat.id
        task = self.chat_id_tasks_cache[cid]
        if text == "/yes":
            self.task_dao.save_task(task)
            self.bot.reply_to(message, "Fantastic, task was successfully saved.")
            logger.info("Task was successfully saved(cid=%s)." % cid)
        elif text == "/no":
            msg = self.bot.reply_to(message, "It look like we have wrong address, let's try it again!")
            self.bot.register_next_step_handler(msg, self.add_location_to_task)
        elif text == "/cancel" or text == "cancel":
            pass

    def check_founded_location_step(self, message):

        """
        Returns founded location step, for user to check if it correct.
        """

        cid = message.chat.id
        task = self.chat_id_tasks_cache[cid]
        location = self.geo_locator.reverse("%s, %s" % (task.location_latitude, task.location_longitude))
        msg = self.bot.reply_to(message,
                                "Please check that founded location is correct:\n\n%s \n\n/yes    /no" % location)
        self.bot.register_next_step_handler(msg, self.finish_location_adding_to_task)

    def get_task_by_id(self, task_id: int) -> Task:
        logger.info("Returning task with id=%s." % task_id)
        return self.task_dao.get_task_by_id(task_id)

    def delete_task_by_id(self, task_id: int):
        logger.info("Task with id=%s was successfully deleted." % task_id)
        self.task_dao.delete_task_by_id(task_id)

    def update_task(self, task: Task):
        if task:
            logger.info("Task with id=%s was successfully updated." % task.id)
            self.task_dao.save_task(task)

    def save_task(self, task: Task):
        if task:
            logger.info("Task with id=%s was successfully saved." % task.id)
            self.task_dao.save_task(task)
