from decimal import Decimal


def find_next_price(prices: list[Decimal], start_price: Decimal, step: Decimal) -> Decimal:
    """
    查找第一个缺失的步进值
    :param prices: 已排序的Decimal列表 (需确保已排序)
    :param start_price: 起始价格
    :param step: 固定步长
    :return: 第一个缺口值或末尾+步长
    """
    if isinstance(step, float):
        raise ValueError("step must be a Decimal")
    vir_prices = [start_price + step * i for i in range(len(prices))]
    # 找出第一个缺失的值
    for vir_price in vir_prices:
        if vir_price not in prices:
            return vir_price
    return vir_prices[-1] + step
