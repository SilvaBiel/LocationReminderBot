import telebot
import logging
from services.user_service import UserService
from services.task_service import TaskService
from services import help_search_service
from model.entity.user import User
from model.entity.task import Task
from geopy.geocoders import Nominatim
from decimal import Decimal
import os

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

key_filename = "fernet.properties"
token_filename = "token.properties"
path = "C:/Users/golub/Documents/ReminderAssistantBot/"

key_path = path + key_filename
encrypted_token_path = path + token_filename

bot = telebot.TeleBot(os.getenv("REMINDER_BOT_TOKEN"))
task_service = TaskService()
user_service = UserService()
task_service.bot = bot
user_temp_cache = dict()

chat_id_tasks_cache = dict()


@bot.message_handler(commands=["start"])
def command_start_handler(message):
    """
    TODO:description
    """

    cid = message.chat.id
    bot.send_chat_action(cid, "typing")
    user = user_service.get_user_by_chat_id(cid)

    if user:
        bot.send_message(cid, "Hello, %s, long time no see, how can i be helpful?" % message.chat.first_name)
        get_help(message)
    else:
        new_user = User(cid)
        user_service.add_user(new_user)
        bot.send_message(cid, "Hello, %s, it\'s nice to meet you!" % message.chat.first_name)
        get_help(message)


@bot.message_handler(commands=["get_active_tasks"])
def get_active_tasks(message):
    """
    TODO:description

    /help//get_active_tasks - returns all active tasks for current user/help/
    """

    cid = message.chat.id
    user = user_service.get_user_by_chat_id(cid)
    user_tasks = user.tasks_list
    active_tasks = 0
    for task in user_tasks:
        if task.state == "active":
            active_tasks += 1
            result = "#%s\n" % task.id
            result += task.header + "\n" + task.body
            if task.location_latitude or task.datetime:
                result += "\n---"
            if task.location_latitude:
                geo_locator = Nominatim(user_agent="taskReminderBot")
                location = geo_locator.reverse("%s, %s" % (task.location_latitude, task.location_longitude))
                result += "\n" + "location: " + str(location) + "\n" + "radius: " + str(task.radius) + " meteres"
            if task.datetime:
                result += "\n" + str(task.datetime)
            bot.send_message(cid, result)

    if active_tasks == 0:
        bot.send_message(cid, "No task were founded for current user.")


@bot.message_handler(commands=["help"])
def get_help(message):
    """
    TODO:description
    /help//help - will show available commands/help/
    """

    cid = message.chat.id
    bot.send_chat_action(cid, 'typing')
    help_data = help_search_service.get_help_for_all_commands()
    bot.send_message(cid, help_data)


@bot.message_handler(commands=["add_task"])
def add_task(message):
    """
    /help//add_task - will add a new task for you and save it in database/help/
    """

    msg = bot.reply_to(message, "Great, let's add a new task!\nPlease enter task header.")
    bot.register_next_step_handler(msg, task_service.add_task_header_step)


@bot.message_handler(commands=["delete_task"])
def delete_task(message):
    """
    /help//delete_task - delete task with id, specified after command,
    separated by space (for example: /delete_task 42)/help/
    """

    text = message.text
    task_id = text.split("/delete_task")[1]
    task_id = task_id.strip()
    if task_id.isdigit():
        task_service.delete_task_by_id(task_id)
        bot.reply_to(message, "Task has been deleted!")
    else:
        bot.reply_to(message, "Wrong input, no valid task id was found, please try again, "
                              "enter correct task id after command.")


@bot.message_handler(commands=["complete_task"])
def complete_task(message):
    """
    /help//complete_task - mark task as completed,
    task id must be specified after command, separated by space
    (for example: /complete_task 42)/help/
    """

    text = message.text
    task_id = text.split("/complete_task")[1]
    task_id = task_id.strip()
    if task_id.isdigit():

        task = task_service.get_task_by_id(task_id)
        if task:
            task.state = "done"
            task_service.update_task(task)
            bot.reply_to(message, "Task has been marked as completed!")
        else:
            bot.reply_to(message, "Task with such is has not been found, please try again.")

    else:
        bot.reply_to(message, "Wrong input, no valid task id was found, please try again, "
                              "enter correct task id after command.")


@bot.message_handler(commands=["edit_task"])
def edit_task(message):
    """
    /help//edit_task - command will edit task with given id,
    syntax must be like this: /edit_task 34 header=new_header body=new_body,
    so after command goes task id, separated by space, after id
    will go parameters which you want to edit with parameter name equals value
    task id must be specified after command, separated by space/help/
    """

    text = message.text
    text = text.split("/edit_task", 1)[1].strip()
    if "=" in text:
        text = text.split(" ")
        if text and text[0].strip().isdigit():
            task_id = text[0].replace("#", "")
            task = task_service.get_task_by_id(task_id)
            for arg in text[1:]:
                arg = arg.strip()
                if "=" in arg:
                    parameter = arg.split("=", 1)[0]
                    value = arg.split("=", 1)[1]
                    if hasattr(task, parameter):
                        task.set_attr(parameter, value)
                        bot.reply_to(message, "Task has been successfully updated!")
                    else:
                        bot.reply_to(message, "Parameter with such name not found(param_name:%s)" % parameter)

                else:
                    bot.reply_to(message, "Wrong input arguments, please try again "
                                          "(syntax example: /edit_task #31 header=new_header body=new_body.")

            task_service.update_task(task)
        else:
            bot.reply_to(message, "No task id been found, please specify task_id with # before id and try again, "
                                  "for example: #12")
    else:
        bot.reply_to(message, "Wrong input, no data to change been found.")


@bot.message_handler(content_types=['location'])
def handle_location(message):
    pass


@bot.edited_message_handler(content_types=['location'])
def handle_location(message):
    cid = message.chat.id
    user = get_user_from_cache(cid)
    user_latitude = message.location.latitude
    user_longitude = message.location.longitude

    tasks_list = user.tasks_list
    for task in tasks_list:
        task_latitude = task.location_latitude
        task_longitude = task.location_longitude
        task_radius = task.radius
        task_header = task.header
        task_body = task.body

        if task.location_latitude and task.location_longitude:
            task_radius_in_degrees = Decimal(task_radius * 0.00001)
            maximum_latitude_for_task_radius = task_latitude + task_radius_in_degrees
            minimum_latitude_for_task_radius = task_latitude - task_radius_in_degrees
            maximum_longitude_for_task_radius = task_longitude + task_radius_in_degrees
            minimum_longitude_for_task_radius = task_longitude - task_radius_in_degrees

            is_latitude_in_radius = minimum_latitude_for_task_radius < user_latitude < maximum_latitude_for_task_radius
            is_longitude_in_radius = minimum_longitude_for_task_radius < user_longitude < maximum_longitude_for_task_radius
            print("user_latitude:", user_latitude, "user_longitude:", user_longitude, "is_latitude_in_radius:",
                  is_latitude_in_radius, "is_longitude_in_radius:", is_longitude_in_radius)
            print("minimum_latitude:", minimum_latitude_for_task_radius)
            print("maximum_latitude:", maximum_latitude_for_task_radius)
            print("minimum_longitude:", minimum_longitude_for_task_radius)
            print("maximum_longitude:", maximum_longitude_for_task_radius)

            if is_latitude_in_radius and is_longitude_in_radius:
                bot.send_message(cid, "%s, you are entered task area:\n%s\n%s"
                                 % (message.chat.first_name, task_header, task_body))


def get_user_from_cache(chat_id):
    if chat_id in chat_id_tasks_cache:
        user = chat_id_tasks_cache[chat_id]
        return user
    else:
        user = user_service.get_user_by_chat_id(chat_id)
        return user


# application entry point
if __name__ == '__main__':
    bot.polling()
