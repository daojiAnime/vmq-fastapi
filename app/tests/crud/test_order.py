import uuid

# from app.tests.utils.utils import random_email, random_lower_string
from rich import inspect, print  # noqa
from sqlmodel import Session, select

from app import crud
from app.core import logger
from app.enums import OrderType
from app.models import Order, User
from app.schemas import OrderCreate


def test_create_order(db: Session) -> None:
    uid = db.exec(select(User.id)).first()
    assert uid is not None, "用户不存在"
    logger.info("查询用户 ID", uid=uid)
    order_in = OrderCreate(
        pay_id=f"demo_{uuid.uuid4()}",
        uid=uid,
        price=100,
        real_price=100,
        type=OrderType.WECHAT,
        notify_url=f"https://example.com/notify_{uuid.uuid4()}",
        return_url=f"https://example.com/return_{uuid.uuid4()}",
        callback_args={"demo": f"demo_{uuid.uuid4()}"},
    )
    order: Order = crud.create_order(session=db, obj_in=order_in, uid=uid)
    assert order.pay_id == order_in.pay_id
    assert order.uid == order_in.uid
    assert order.price == order_in.price
    assert order.real_price == order_in.real_price


def test_get_order(db: Session) -> None:
    order: Order = db.exec(select(Order)).first()
    assert order is not None, "订单不存在"
    inspect(order)
