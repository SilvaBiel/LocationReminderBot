from cryptography.fernet import Fernet
import telebot
import logging
from services.user_service import UserService
from services.task_service import TaskService
from model.entity.user import User
from model.entity.task import Task


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
task_service = TaskService()
user_service = UserService()
task_service.bot = bot

chat_id_tasks_cache = dict()


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
    # TODO: automate help, which will iterate over all funcs of this method(maybe marked for example)
    # with returning info docs for each function
    bot.send_message(cid, "help!")


@bot.message_handler(commands=["add_task"])
def add_task(message):
    msg = bot.reply_to(message, "Great, let's add a new task!\nPlease enter task header.")
    bot.register_next_step_handler(msg, task_service.add_task_header_step)






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
