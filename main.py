import configparser
from cryptography.fernet import Fernet
import telebot


def load_fernet_properties():

    """
    Loads fernet properties to decrypt token from disk.
    """

    return open("fernet.properties", "rb").read()


def read_bot_token():

    config = configparser.ConfigParser()
    config.read("config.properties")
    encrypted_token = config.get("BOT", "Token")

    f = Fernet(load_fernet_properties())
    token = f.decrypt(encrypted_token.encode())

    return token

bot = telebot.Telebot( read_bot_token() )

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет!")