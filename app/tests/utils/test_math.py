from decimal import Decimal

from rich import print  # noqa

from app.utils.math import find_next_price


def test_find_next_price():
    # 测试用例
    # assert find_next_price([], Decimal("0.1")) == Decimal("0.1")  # 空列表
    # assert find_next_price([Decimal("0.1")], Decimal("0.1")) == Decimal("0.2")  # 单元素
    # assert find_next_price([Decimal("0.1"), Decimal("0.3")], Decimal("0.1")) == Decimal("0.2")  # 中间缺口
    # assert find_next_price([Decimal("0.1"), Decimal("0.2")], Decimal("0.1")) == Decimal("0.3")  # 完整序列
    amount_list = [Decimal("0.1"), Decimal("0.2"), Decimal("0.4"), Decimal("0.5")]
    step = Decimal("0.1")
    start_price = amount_list[0]
    print(f"test list: {amount_list}")
    print(f"test step: {step}")
    print(f"test result: {find_next_price(amount_list, start_price, step)}")
    assert find_next_price(amount_list, start_price, step) == Decimal("0.3")
