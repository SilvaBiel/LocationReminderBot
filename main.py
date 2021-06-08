from cryptography.fernet import Fernet
import telebot
import logging
from telebot import types

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


# start command handler
@bot.message_handler(commands=['start'])
def command_start_handler(message):
    cid = message.chat.id
    bot.send_chat_action(cid, 'typing')
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_geo = types.KeyboardButton(text='send location', request_location=True)
    markup.add(button_geo)
    bot.send_message(cid, 'Hello stranger, please choose commands from the menu', reply_markup=markup)


# application entry point
if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)