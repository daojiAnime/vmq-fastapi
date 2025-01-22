from enum import IntEnum, StrEnum


class OrderType(IntEnum):
    WECHAT = 1
    ALIPAY = 2


class OrderStatus(IntEnum):
    EXPIRED = -1
    PENDING = 0
    SUCCESS = 1
    NOTIFY_FAILED = 2


class AccessRole(StrEnum):
    SUPER = "super"
    ACTIVE = "active"
    INACTIVE = "inactive"


class RedisDBEnum(IntEnum):
    HEARTBEAT = 0
    ORDER = 1
