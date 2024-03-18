import telebot
import logging
from services.user_service import UserService
from services.task_service import TaskService
from services.delivery_service import DeliveryService
from services import help_search_service
from model.entity.user import User
from model.entity.task import Task
from model.entity.delivery import Delivery
from geopy.geocoders import Nominatim
from decimal import Decimal
import os
from datetime import datetime, timedelta
import threading
import time
from services.logger_service import logger


bot = telebot.TeleBot(os.getenv("REMINDER_BOT_TOKEN"))
task_service = TaskService()
user_service = UserService()
delivery_service = DeliveryService()
task_service.bot = bot

chat_id_cache = dict()


@bot.message_handler(commands=["start"])
def command_start_handler(message):

    """
    Initial start function, register user in database (based on chat id)

    /help//start - initial function, which register user based on chat id/help/
    """

    cid = message.chat.id
    bot.send_chat_action(cid, "typing")
    user = user_service.get_user_by_chat_id(cid)

    if user:
        bot.send_message(cid, "Ola, %s, a quanto tempo, como posso te ajudar?" % message.chat.first_name)
        get_help(message)
    else:
        new_user = User(cid)
        user_service.add_user(new_user)
        bot.send_message(cid, "Oi, %s, prazer em conhece-lo!" % message.chat.first_name)
        get_help(message)
        logger.info("Registered new user.")


@bot.message_handler(commands=["get_active_tasks"])
def get_active_tasks(message):

    """
    Returns all active tasks for current user.

    /help//get_active_tasks - returns all active tasks for current user/help/
    """

    cid = message.chat.id
    logger.info("Get active tasks for cid(%s)." % cid)
    user = user_service.get_user_by_chat_id(cid)
    user_tasks = user.tasks_list
    active_tasks = 0
    for task in user_tasks:
        if task.state == "active":
            active_tasks += 1
            result = "#%s\n" % task.id
            result += task.header + "\n" + task.body
            if task.location_latitude:
                geo_locator = Nominatim(user_agent="taskReminderBot")
                location = geo_locator.reverse("%s, %s" % (task.location_latitude, task.location_longitude))
                result += "\n" + "location: " + str(location) + "\n" + "radius: " + str(task.radius) + " meteres"
            bot.send_message(cid, result)

    if active_tasks == 0:
        bot.send_message(cid, "Nenhum frete encontrado para o usuário em questão.")


@bot.message_handler(commands=["help"])
def get_help(message):

    """
    Returns help descriptions for each available commands, which bot can handle.

    /help//help - will show available commands/help/
    """

    cid = message.chat.id
    bot.send_chat_action(cid, 'typing')
    help_data = help_search_service.get_help_for_all_commands()
    bot.send_message(cid, help_data)


@bot.message_handler(commands=["add_task"])
def add_task(message):

    """
    Function adds new task for current user.

    /help//add_task - will add a new task for you and save it in database/help/
    """

    logger.info("Adding new task.")
    msg = bot.reply_to(message, "Ótimo, vamos adicionar um novo frete!\nQual é o título deste frete?.")
    bot.register_next_step_handler(msg, task_service.add_task_header_step)


@bot.message_handler(commands=["delete_task"])
def delete_task(message):

    """
    Deletes task, based on id.

    /help//delete_task - delete task with id, specified after command,
    separated by space (for example: /delete_task 42)/help/
    """

    text = message.text
    task_id = text.split("/delete_task")[1]
    task_id = task_id.strip()
    if task_id.isdigit():
        task_service.delete_task_by_id(task_id)
        bot.reply_to(message, "Frete deletado com sucesso!")
        logger.info("Task with id=%s was deleted." % str(task_id))
    else:
        bot.reply_to(message, "Dados invalidos, nenhum frete com ID fornecido encontrado, tente novamente, "
                              "preencha o ID do frete corretamente.")


@bot.message_handler(commands=["complete_task"])
def complete_task(message):

    """
    Mark task as completed, based on task id.

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
            bot.reply_to(message, "Frete completo!")
            logger.info("Task with id=%s was marked as completed." % str(task_id))
        else:
            bot.reply_to(message, "Frete com o ID especificado não encontrado, por favor tenta novamente.")

    else:
        bot.reply_to(message, "Dados invalidos, nenhum frete com ID fornecido encontrado, tente novamente, "
                              "preencha o ID do frete corretamente.")


@bot.message_handler(commands=["edit_task"])
def edit_task(message):

    """
    Edit task by id and task parameters to edit.

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
                    else:
                        bot.reply_to(message, "Para com o nome fornecido não encontrado(param_name:%s)" % parameter)

                else:
                    bot.reply_to(message, "Dados incorretos, por favor tente novamente"
                                          "(exemplo de escrita: /edit_task #31 header=new_header body=new_body.")

            bot.reply_to(message, "Frete atualizado com sucesso!")
            logger.info("Task with id=%s was successfully edited." % str(task_id))
            task_service.update_task(task)
        else:
            bot.reply_to(message, "ID do frete não encontrado, por favor especifique o ID com # antes do ID, "
                                  "por exemplo: #12")
    else:
        bot.reply_to(message, "Dados incorretos, nenhum dado alterado.")



@bot.edited_message_handler(content_types=['location'])
def handle_live_location_delivery(message):

    """
    Checks current user location with each user task by task location and radius,
    if user in radius and coordinates it sends message to user.
    """

    chat_id = message.chat.id
    user = get_user_from_cache(chat_id)

    user_latitude = message.location.latitude
    user_longitude = message.location.longitude

    print("User location: ", user_latitude, user_longitude, message.chat.first_name)

    start_new_thread = False
    if "thread" not in chat_id_cache[chat_id].keys():
        start_new_thread = True
    elif not chat_id_cache[chat_id]["thread"]:
        start_new_thread = True

    if start_new_thread:
        thread = threading.Thread(target=refresh_live_location_notifier, args=[chat_id, message, bot])
        thread.start()

    chat_id_cache[chat_id]["last_live_location_share_time"] = datetime.now()
    delivery_list = delivery_service.get_all_deliveries()
    for delivery in delivery_list:
        pickup_latitude = delivery.pickup_latitude
        pickup_longitude = delivery.pickup_longitude
        radius = delivery.radius
        state = delivery.state
        notification_happened = delivery.notification_happened
        information = delivery.information
        price = delivery.price
        print("those are if conditions: ", delivery.notification_happened, pickup_latitude, pickup_longitude)
        if delivery.notification_happened < 2 and pickup_latitude and pickup_longitude and state == "waiting":
            task_radius_in_degrees = Decimal(radius * 0.00001)
            print("task_radius_in_degrees: ", task_radius_in_degrees)
            maximum_latitude_for_task_radius = pickup_latitude + task_radius_in_degrees
            minimum_latitude_for_task_radius = pickup_latitude - task_radius_in_degrees
            maximum_longitude_for_task_radius = pickup_longitude + task_radius_in_degrees
            minimum_longitude_for_task_radius = pickup_longitude - task_radius_in_degrees

            is_latitude_in_radius = minimum_latitude_for_task_radius < user_latitude < maximum_latitude_for_task_radius
            is_longitude_in_radius = minimum_longitude_for_task_radius < user_longitude < maximum_longitude_for_task_radius

            if is_latitude_in_radius and is_longitude_in_radius:
                bot.send_message(chat_id, "%s,  Ei, temos um frete pra você:\n R$%s\n informações:%s"
                                 % (message.chat.first_name, price, information))
                delivery.notification_happened = delivery.notification_happened+1
                msg = bot.reply_to(message, "Gostaria de aceitar este frete?.")
                bot.register_next_step_handler(msg, task_service.add_task_header_step)
                delivery.state = "in_route"
                task_service.update_task(delivery)
                logger.info("User entered to task area, task marked as notification happened, "
                            "task_id = %s" % str(delivery.id))



@bot.edited_message_handler(content_types=['location'])
def handle_live_location(message):

    """
    Checks current user location with each user task by task location and radius,
    if user in radius and coordinates it sends message to user.
    """

    chat_id = message.chat.id
    user = get_user_from_cache(chat_id)

    user_latitude = message.location.latitude
    user_longitude = message.location.longitude

    print("User location: ", user_latitude, user_longitude, message.chat.first_name)

    start_new_thread = False
    if "thread" not in chat_id_cache[chat_id].keys():
        start_new_thread = True
    elif not chat_id_cache[chat_id]["thread"]:
        start_new_thread = True

    if start_new_thread:
        thread = threading.Thread(target=refresh_live_location_notifier, args=[chat_id, message, bot])
        thread.start()

    chat_id_cache[chat_id]["last_live_location_share_time"] = datetime.now()
    tasks_list = user.tasks_list
    for task in tasks_list:
        task_latitude = task.location_latitude
        task_longitude = task.location_longitude
        task_radius = task.radius
        task_header = task.header
        task_body = task.body
        print("those are if conditions: ", task.notification_happened, task.location_latitude, task.location_longitude)
        if task.notification_happened and task.location_latitude and task.location_longitude:
            task_radius_in_degrees = Decimal(task_radius * 0.00001)
            print("task_radius_in_degrees: ", task_radius_in_degrees)
            maximum_latitude_for_task_radius = task_latitude + task_radius_in_degrees
            minimum_latitude_for_task_radius = task_latitude - task_radius_in_degrees
            maximum_longitude_for_task_radius = task_longitude + task_radius_in_degrees
            minimum_longitude_for_task_radius = task_longitude - task_radius_in_degrees

            is_latitude_in_radius = minimum_latitude_for_task_radius < user_latitude < maximum_latitude_for_task_radius
            is_longitude_in_radius = minimum_longitude_for_task_radius < user_longitude < maximum_longitude_for_task_radius

            if is_latitude_in_radius and is_longitude_in_radius:
                bot.send_message(chat_id, "%s,  Você esta na localização de entrega de um frete:\n%s\n%s"
                                 % (message.chat.first_name, task_header, task_body))
                task.notification_happened = True
                task_service.update_task(task)
                logger.info("User entered to task area, task marked as notification happened, "
                            "task_id = %s" % str(task.id))


def refresh_live_location_notifier(chat_id, message, bot_object):

    """
    if the user's location has stopped arriving and there has been no more than a minute,
    the function sends a notification to the user that he needs to share his location with the bot again
    """

    continue_loop_flag = True
    chat_id_cache[chat_id]["thread"] = True
    while continue_loop_flag:
        if "last_live_location_share_time" in chat_id_cache[chat_id]:
            last_location_share_time = chat_id_cache[chat_id]["last_live_location_share_time"]
        else:
            chat_id_cache[chat_id]["last_live_location_share_time"] = datetime.now()
            time.sleep(300)
            continue

        now = datetime.now()
        if (now - last_location_share_time) > timedelta(minutes=5):
            bot_object.send_message(chat_id, "%s, parece que o periodo de compartilhamento de localização acabou, "
                                             "por favor compartilhe novamente a localização, "
                                             "para que seja possível o acompanhamento dos fretes." % message.chat.first_name)
            continue_loop_flag = False
            chat_id_cache[chat_id]["thread"] = False
            logger.info("For chat_id=%s live location period was over, message sended." % chat_id)

        else:
            time.sleep(300)


def get_user_from_cache(chat_id):

    """
    Returns user from cache, if user not cached,
    function searches for it in database and adds to cache.
    """

    if chat_id in chat_id_cache and "user" in chat_id_cache[chat_id]:
        user = chat_id_cache[chat_id]["user"]
        return user
    else:
        if chat_id not in chat_id_cache:
            chat_id_cache[chat_id] = dict()
        user = user_service.get_user_by_chat_id(chat_id)
        chat_id_cache[chat_id]["user"] = user
        return user


if __name__ == '__main__':
    print("THIS IS .ENV ",os.getenv("REMINDER_BOT_TOKEN"))
    bot.polling()
