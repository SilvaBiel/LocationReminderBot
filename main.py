import configparser
from cryptography.fernet import Fernet
import telebot

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


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет!")


bot.polling()
