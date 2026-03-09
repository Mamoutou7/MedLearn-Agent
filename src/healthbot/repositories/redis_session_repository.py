"""Redis-backed session repository."""

from __future__ import annotations

import time
from typing import Any

from src.healthbot.repositories.session_repository import (
    JsonSerializer,
    SessionKeyBuilder,
    SessionNotFoundError,
    SessionRepositoryError,
)


class RedisSessionRepository:
    """Store session metadata and history in Redis."""

    def __init__(
        self,
        redis_url: str,
        ttl_seconds: int = 86400,
        key_prefix: str = "medlearn",
    ) -> None:
        try:
            import redis
        except ImportError as exc:  # pragma: no cover - depends on optional package
            raise SessionRepositoryError(
                "redis package is required for RedisSessionRepository. "
                "Install it with `pip install redis`."
            ) from exc

        self._redis = redis.Redis.from_url(redis_url, decode_responses=True)
        self._ttl_seconds = ttl_seconds
        self._keys = SessionKeyBuilder(prefix=key_prefix)
        self._serializer = JsonSerializer()

    def create_session(self, session_id: str) -> None:
        meta_key = self._keys.meta(session_id)
        history_key = self._keys.history(session_id)
        now = time.time()
        pipe = self._redis.pipeline()
        pipe.hset(meta_key, mapping={"session_id": session_id, "created_at": now})
        pipe.sadd(self._keys.index(), session_id)
        pipe.delete(history_key)
        if self._ttl_seconds > 0:
            pipe.expire(meta_key, self._ttl_seconds)
            pipe.expire(history_key, self._ttl_seconds)
        pipe.execute()

    def exists(self, session_id: str) -> bool:
        return bool(self._redis.exists(self._keys.meta(session_id)))

    def list_sessions(self) -> list[str]:
        session_ids = sorted(self._redis.smembers(self._keys.index()))
        return [
            session_id
            for session_id in session_ids
            if self._redis.exists(self._keys.meta(session_id))
        ]

    def append_event(self, session_id: str, entry: dict) -> None:
        if not self.exists(session_id):
            raise SessionNotFoundError(session_id)

        meta_key = self._keys.meta(session_id)
        history_key = self._keys.history(session_id)
        payload = self._serializer.dumps(entry)

        pipe = self._redis.pipeline()
        pipe.rpush(history_key, payload)
        if self._ttl_seconds > 0:
            pipe.expire(meta_key, self._ttl_seconds)
            pipe.expire(history_key, self._ttl_seconds)
        pipe.execute()

    def get_history(self, session_id: str) -> list[dict]:
        if not self.exists(session_id):
            raise SessionNotFoundError(session_id)
        values = self._redis.lrange(self._keys.history(session_id), 0, -1)
        return [self._serializer.loads(item) for item in values]

    def ping(self) -> bool:
        return bool(self._redis.ping())

    def close(self) -> None:
        connection_pool: Any = getattr(self._redis, "connection_pool", None)
        if connection_pool is not None:
            connection_pool.disconnect()

