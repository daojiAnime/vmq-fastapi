import uuid

from sqlmodel import Session

from app.enums import OrderStatus
from app.models.order import Order
from app.schemas import OrderCreate


def create_order(*, session: Session, obj_in: OrderCreate, uid: uuid.UUID) -> Order:
    db_obj = Order.model_validate(
        obj_in.model_dump(exclude_unset=True),
        update={"uid": uid, "state": OrderStatus.PENDING},
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj
