from datetime import datetime, timedelta

from redis import Redis

from app.core.config import settings
from app.enums import RedisDBEnum


class RedisClientHeartbeatManager:
    """
    客户端心跳管理器，用于管理客户端的心跳状态
    """

    def __init__(self, redis_url: str):
        self.redis = Redis.from_url(f"{redis_url}/{RedisDBEnum.HEARTBEAT}")

    def set_client_online(self, client_id: str, online: bool) -> None:
        self.redis.hset(client_id, "online", int(online))
        self.redis.hset(client_id, "last_heartbeat", datetime.now().isoformat())

    def is_client_online(self, client_id: str) -> bool:
        value = self.redis.hget(client_id, "online")
        return value == b"1"

    def get_last_heartbeat(self, client_id: str) -> str:
        last_heartbeat = self.redis.hget(client_id, "last_heartbeat")
        return last_heartbeat if last_heartbeat else None

    def check_offline_clients(self) -> list[str]:
        offline_clients = []
        for client_id in self.redis.scan_iter():
            if self.redis.hget(client_id, "online") == b"0":
                offline_clients.append(client_id)
        return offline_clients

    def remove_offline_clients(self) -> None:
        for client_id in self.redis.scan_iter():
            last_heartbeat = self.redis.hget(client_id, "last_heartbeat")
            if last_heartbeat and datetime.fromisoformat(last_heartbeat) < datetime.now() - timedelta(
                seconds=settings.HEARTBEAT_TIMEOUT
            ):
                self.redis.delete(client_id)


REDIS_MANAGER = RedisClientHeartbeatManager(str(settings.REDIS_URL))
