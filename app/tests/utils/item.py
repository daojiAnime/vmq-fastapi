from sqlmodel import Session

from app import crud
from app.models import Order
from app.schemas.order import OrderCreate
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def create_random_order(db: Session) -> Order:
    user = create_random_user(db)
    owner_id = user.id
    assert owner_id is not None
    title = random_lower_string()
    description = random_lower_string()
    item_in = OrderCreate(title=title, description=description)
    return crud.create_order(session=db, obj_in=item_in, uid=owner_id)
