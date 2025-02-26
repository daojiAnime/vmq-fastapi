from collections.abc import Awaitable
from datetime import datetime, timedelta

from redis import Redis

from app.core.config import settings
from app.enums import RedisDBEnum


class RedisClientHeartbeatManager:
    """
    客户端心跳管理器，用于管理客户端的心跳状态
    """

    def __is_online(self, value: str) -> bool:
        return value == "true"

    def __get_online(self, online: bool) -> str:
        return "true" if online else "false"

    def __init__(self, redis_url: str):
        self.redis = Redis.from_url(f"{redis_url}/{RedisDBEnum.HEARTBEAT}")

    def set_client_online(self, client_id: str, online: bool) -> None:
        self.redis.hset(client_id, "online", self.__get_online(online))
        self.redis.hset(client_id, "last_heartbeat", datetime.now().isoformat())

    def is_client_online(self, client_id: str) -> bool:
        value = self.redis.hget(client_id, "online")
        if value is None or isinstance(value, Awaitable):
            return False
        return self.__is_online(value)

    def get_last_heartbeat(self, client_id: str) -> str:
        last_heartbeat = self.redis.hget(client_id, "last_heartbeat")
        if last_heartbeat is None or isinstance(last_heartbeat, Awaitable):
            return ""
        return last_heartbeat

    def set_last_payment(self, client_id: str, payment: str) -> None:
        self.redis.hset(client_id, "last_payment", payment)

    def get_last_payment(self, client_id: str) -> str:
        last_payment = self.redis.hget(client_id, "last_payment")
        if last_payment is None or isinstance(last_payment, Awaitable):
            return ""
        return last_payment

    def check_offline_clients(self) -> list[str]:
        offline_clients = []
        for client_id in self.redis.scan_iter():
            online = self.redis.hget(client_id, "online")
            if online is None or isinstance(online, Awaitable):
                continue
            if not self.__is_online(online):
                offline_clients.append(client_id)
        return offline_clients

    def remove_offline_clients(self) -> None:
        for client_id in self.redis.scan_iter():
            last_heartbeat = self.redis.hget(client_id, "last_heartbeat")
            if last_heartbeat is None or isinstance(last_heartbeat, Awaitable):
                continue
            if datetime.fromisoformat(last_heartbeat) < datetime.now() - timedelta(seconds=settings.HEARTBEAT_TIMEOUT):
                self.redis.delete(client_id)


REDIS_MANAGER = RedisClientHeartbeatManager(str(settings.REDIS_URL))
