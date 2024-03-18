from model.entity.base import Session
from model.entity.delivery import Delivery
from sqlalchemy import delete, select


class DeliveryDao:

    def __init__(self):
        self.session = Session

    def get_all_deliveries(self) -> list:
        all_deliveries_list = self.session.query(Delivery).all()
        self.session.commit()
        return all_deliveries_list

    def get_active_deliveries(self) -> list:
        active_deliveries_list = self.session.query(Delivery).filter(Delivery.state == "active")
        self.session.commit()
        return active_deliveries_list

    def get_completed_deliveries(self) -> list:
        active_deliveries_list = self.session.query(Delivery).filter(Delivery.state == "completed")
        self.session.commit()
        return active_deliveries_list

    def save_delivery(self, delivery: Delivery):
        self.session.add(delivery)
        self.session.commit()

    def delete_delivery_by_id(self, delivery_id: int) -> bool:
        statement = delete(Delivery).where(Delivery.id == delivery_id)
        result = self.session.execute(statement)

    def edit_delivery(self, delivery: Delivery):
        self.session.add(delivery)
        self.session.commit()

    def get_delivery_by_id(self, delivery_id: int) -> Delivery:
        statement = select(Delivery).where(Delivery.id == delivery_id)
        result = self.session.execute(statement)
        deliveries = result.scalars().all()
        if deliveries:
            return deliveries[0]
        else:
            # TODO: LOG NOTHING IS FOUND
            pass