from cryptography.fernet import Fernet
import telebot
import logging
from telebot import types
from services.task_service import  TaskService
from services.user_service import UserService
from model.entity.User import User
from model.entity.Task import Task

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

key_filename = "fernet.properties"
token_filename = "token.properties"
path = "C:/Users/golub/Documents/ReminderAssistantBot/"

key_path = path + key_filename
encrypted_token_path = path + token_filename


def read_file(filepath: str):
    """
    Load the previously generated key
    """

    return open(filepath, "rb").read()


def decrypt_message(encrypted_data: bytes):
    """
    Decrypts an encrypted message
    """
    loaded_key = read_file(key_path)
    fernet_object = Fernet(loaded_key)
    decrypted_message = fernet_object.decrypt(encrypted_data)

    return decrypted_message.decode()


def get_bot_token():
    encrypted_token = open(encrypted_token_path, "rb").read()
    token = decrypt_message(encrypted_token)

    return token

bot = telebot.TeleBot(get_bot_token())
user_service = UserService()
task_service = TaskService()


@bot.message_handler(commands=["start"])
def command_start_handler(message):
    cid = message.chat.id
    bot.send_chat_action(cid, "typing")

    user = user_service.get_user_by_chat_id(cid)
    if user:
        bot.send_message(cid, "Hello, %s, long time no see, how can i be helpfull?" % message.chat.first_name)
    else:
        new_user = User(cid)
        user_service.add_user(new_user)
        bot.send_message(cid, "Hello, %s, it\'s nice to meet you, how can i help you?" % message.chat.first_name)
        bot.send_message(cid, "Super cool help commands:")


@bot.message_handler(commands=["help"])
def get_help(message):
    cid = message.chat.id
    bot.send_chat_action(cid, 'typing')
    # TODO: add help lines
    bot.send_message(cid, "help!")


@bot.message_handler(commands=["add_task"])
def add_task(message):
    cid = message.chat.id
    user = user_service.get_user_by_chat_id(cid)
    if user:
        text_arguments = message.text.split("/add_task", 1)
        if text_arguments:
            text_arguments = text_arguments[-1]
            print("text_arguments:", text_arguments)
        pass
        # after task was added if it have location coordinates than ask if user want to
        # shar his location

"""
@bot.message_handler(commands=['get_all_tasks'])
def get_all_tasks(message):
    cid = message.chat.id
    bot.send_chat_action(cid, 'typing')
    
    user = user_service.get_user_by_chat_id(cid)
    if user:
        print use
    else:
        bot.send_message(cid, 'Hello stranger, please choose commands from the menu', reply_markup=markup)

    #get phone number
    #encrypt it
    #ask db service to return user all tasks




def edit_task(message):


def delete_task(message):


def complete_task(message):


def start_tracking(message):
    
    # here you need to count time which passed since this message,
    # after it will come to the live tracking limit, bot must send message to the user
    # so user can share live location again
    
    
def get_last_five_news(message):


def get_weather_today():


def get_weather_week():


"""
# application entry point
if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)