from dao.delivery_dao import DeliveryDao
import re
from geopy.geocoders import Nominatim
from services.user_service import UserService
from model.entity.delivery import Delivery
from services.logger_service import logger

class DeliveryService:
    delivery_dao = DeliveryDao()
    bot = None
    geo_locator = Nominatim(user_agent="taskReminderBot")
    user_service = UserService()
    chat_id_deliveries_cache = dict()
    
    def add_delivery_pickup_step(self, message):

        """
        New delivery header creation step.
        """

        cid = message.chat.id
        header = message.text
        self.chat_id_deliveries_cache = dict()
        if header:
            msg = self.bot.reply_to(message, "Otimo, agora o local de coleta.")
            self.bot.register_next_step_handler(msg, self.add_pickup_location_step)
            self.chat_id_deliveries_cache[cid] = header
        elif header == "/cancel" or header == "cancel":
            pass
        else:
            msg = self.bot.reply_to(message, "Por favor, preencha a location do frete.")
            self.bot.register_next_step_handler(msg, self.add_pickup_location_step)

    def add_pickup_location_step(self, message):

        """
        New delivery body creation step.
        """

        cid = message.chat.id
        body = message.text
        user = self.user_service.get_user_by_chat_id(cid)
        if isinstance(user, list):
            user = user[0]

        if body:
            msg = self.bot.reply_to(message, "Fantastico, frete esta quase pronto, \n" 
                                             "para adicionar a localização de entrega,\n"
                                             "digite /location, \n"
                                             "para deixar em branco, digite /skip e o frete será criado como rascunho.")
            self.bot.register_next_step_handler(msg, self.add_location_reminder)
            header = self.chat_id_deliveries_cache[cid]
            delivery = Delivery(header, body, user)
            self.save_delivery(delivery)
            self.chat_id_deliveries_cache[cid] = delivery
        elif body == "/cancel" or body == "cancel":
            pass
        else:
            msg = self.bot.reply_to(message, "A descrição do frete esta em branco, favor preencher.")
            self.bot.register_next_step_handler(msg, self.add_pickup_location_step)

    def add_location_reminder(self, message):

        """
        Add location reminder to delivery step 1.
        """

        text = message.text
        cid = message.chat.id
        delivery = self.chat_id_deliveries_cache[cid]
        if text == "/skip":
            self.save_delivery(delivery)
            self.bot.reply_to(message, "Perfeito, %s frtete criado com sucesso." % message.chat.first_name)
        elif text == "/location":
            msg = self.bot.reply_to(message, "%s por favor, preencha a localização do frete. "
                                             "1) latitude, longitude"
                                             "2) ou estado, cidade, rua, numero"
                                             "separe por espaço os valores." % message.chat.first_name)
            self.bot.register_next_step_handler(msg, self.add_delivery_location)
        elif text == "/cancel" or text == "cancel":
            pass
        else:
            msg = self.bot.reply_to(message, "Formato invalido, digite novamente.")
            self.bot.register_next_step_handler(msg, self.add_location_reminder)

    def add_delivery_location(self, message):

        """
        Add location reminder to delivery step 2.
        """

        location = message.text
        print("LOCATION"+location)
        cid = message.chat.id
        delivery = self.chat_id_deliveries_cache[cid]
        if re.match(r'^(-?\d+(\.\d+)?),\s*(-?\d+(\.\d+)?)$', location):
            location_arguments = location.split(",")
            if len(location_arguments) == 2:
                latitude = location_arguments[0].strip()
                longitude = location_arguments[1].strip()
                delivery.location_latitude = latitude
                delivery.location_longitude = longitude
                self.check_founded_location_step(message)
        elif location:
            location = self.geo_locator.geocode(location)
            if location:
                delivery.location_latitude = location.latitude
                delivery.location_longitude = location.longitude
                self.check_founded_location_step(message)
            else:
                msg = self.bot.reply_to(message, "Desculpa, nao foi possivel confirmar a localização, "
                                                 "verifique o endereço e tente novamente. ")
                self.bot.register_next_step_handler(msg, self.add_delivery_location)
        elif location == "/cancel" or location == "cancel":
            pass
        else:
            self.bot_location_wrong_syntax(message)

    def bot_location_wrong_syntax(self, message):

        """
        Wrong syntax message during location adding to delivery.
        """

        self.bot.reply_to(message, "Formato incorreto.")
        msg = self.bot.reply_to(message, "%s por favor, preencha a localização do frete. "
                                             "1) latitude, longitude"
                                             "2) ou estado, cidade, rua, numero"
                                             "separe por espaço os valores." % message.chat.first_name)
        self.bot.register_next_step_handler(msg, self.add_delivery_location)

    def finish_location_adding_to_delivery(self, message):

        """
        Finishing location adding to delivery.
        """

        text = message.text
        cid = message.chat.id
        delivery = self.chat_id_deliveries_cache[cid]
        if text == "/yes":
            self.delivery_dao.save_delivery(delivery)
            self.bot.reply_to(message, "Fantastico, frete criado com sucesso.")
            logger.info("Task was successfully saved(cid=%s)." % cid)
        elif text == "/no":
            msg = self.bot.reply_to(message, "Parece que temos o endereço errado, vamos tentar novamente!")
            self.bot.register_next_step_handler(msg, self.add_delivery_location)
        elif text == "/cancel" or text == "cancel":
            pass

    def check_founded_location_step(self, message):

        """
        Returns founded location step, for user to check if it correct.
        """

        cid = message.chat.id
        delivery = self.chat_id_deliveries_cache[cid]
        location = self.geo_locator.reverse("%s, %s" % (delivery.location_latitude, delivery.location_longitude))
        msg = self.bot.reply_to(message,
                                "Por favor, verifique se a localiozação esta correta:\n\n%s \n\n/yes    /no" % location)
        self.bot.register_next_step_handler(msg, self.finish_location_adding_to_delivery)

    def get_delivery_by_id(self, delivery_id: int) -> Delivery:
        logger.info("Returning delivery with id=%s." % delivery_id)
        return self.delivery_dao.get_delivery_by_id(delivery_id)

    def delete_delivery_by_id(self, delivery_id: int):
        logger.info("Delivery with id=%s was successfully deleted." % delivery_id)
        self.delivery_dao.delete_delivery_by_id(delivery_id)

    def update_delivery(self, delivery: Delivery):
        if delivery:
            logger.info("Delivery with id=%s was successfully updated." % delivery.id)
            self.delivery_dao.save_delivery(delivery)

    def save_delivery(self, delivery: Delivery):
        if delivery:
            logger.info("Delivery with id=%s was successfully saved." % delivery.id)
            self.delivery_dao.save_delivery(delivery)

    def get_all_deliveries(self) -> list:
        logger.info("Returning all deliveries.")
        return self.delivery_dao.get_all_deliveries()