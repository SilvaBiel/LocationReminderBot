from sqlalchemy import Column, String, Integer, Numeric, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from model.entity.base import Base
from model.entity.user import User


class Delivery(Base):
    __tablename__ = "delivery"

    id = Column(Integer, primary_key=True)
    pickup_latitude = Column(Numeric)
    pickup_longitude = Column(Numeric)
    information = Column(String)
    price = Column(Numeric)
    radius = Column(Integer)
    state = Column(String)  # waiting, in_route, delivered, canceled
    notification_happened = Column(Numeric)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="delivery_list")

    def __init__(self, pickup_latitude: str, pickup_longitude: str, user: User, radius: Integer = 5000, information: str = "", notification_happened: Numeric = 0, price: Numeric = 0.0):
        self.pickup_latitude = pickup_latitude
        self.pickup_longitude = pickup_longitude
        self.user = user
        self.radius = radius
        self.state = "waiting"
        self.notification_happened = notification_happened
        self.information = information
        self.price = price

    def set_attr(self, attribute_name, value):
        setattr(self, attribute_name, value)