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
        except ImportError as exc:  # pragma: no cover
            raise SessionRepositoryError(
                "redis package is required for RedisSessionRepository. "
                "Install it with `pip install redis`."
            ) from exc

        self._redis_module = redis
        self._redis = redis.Redis.from_url(redis_url, decode_responses=True)
        self._ttl_seconds = ttl_seconds
        self._keys = SessionKeyBuilder(prefix=key_prefix)
        self._serializer = JsonSerializer()
        self._redis_url = redis_url

    def _wrap_redis_error(self, exc: Exception, operation: str) -> SessionRepositoryError:
        return SessionRepositoryError(
            f"Redis session backend unavailable during '{operation}' "
            f"(url={self._redis_url!r}). Original error: {exc}"
        )

    def create_session(self, session_id: str) -> None:
        meta_key = self._keys.meta(session_id)
        history_key = self._keys.history(session_id)
        now = time.time()

        try:
            pipe = self._redis.pipeline()
            pipe.hset(meta_key, mapping={"session_id": session_id, "created_at": now})
            pipe.sadd(self._keys.index(), session_id)
            pipe.delete(history_key)
            if self._ttl_seconds > 0:
                pipe.expire(meta_key, self._ttl_seconds)
                pipe.expire(history_key, self._ttl_seconds)
            pipe.execute()
        except self._redis_module.exceptions.RedisError as exc:
            raise self._wrap_redis_error(exc, "create_session") from exc

    def exists(self, session_id: str) -> bool:
        try:
            return bool(self._redis.exists(self._keys.meta(session_id)))
        except self._redis_module.exceptions.RedisError as exc:
            raise self._wrap_redis_error(exc, "exists") from exc

    def list_sessions(self) -> list[str]:
        try:
            session_ids = sorted(self._redis.smembers(self._keys.index()))
            return [
                session_id
                for session_id in session_ids
                if self._redis.exists(self._keys.meta(session_id))
            ]
        except self._redis_module.exceptions.RedisError as exc:
            raise self._wrap_redis_error(exc, "list_sessions") from exc

    def append_event(self, session_id: str, entry: dict) -> None:
        if not self.exists(session_id):
            raise SessionNotFoundError(session_id)

        meta_key = self._keys.meta(session_id)
        history_key = self._keys.history(session_id)
        payload = self._serializer.dumps(entry)

        try:
            pipe = self._redis.pipeline()
            pipe.rpush(history_key, payload)
            if self._ttl_seconds > 0:
                pipe.expire(meta_key, self._ttl_seconds)
                pipe.expire(history_key, self._ttl_seconds)
            pipe.execute()
        except self._redis_module.exceptions.RedisError as exc:
            raise self._wrap_redis_error(exc, "append_event") from exc

    def get_history(self, session_id: str) -> list[dict]:
        if not self.exists(session_id):
            raise SessionNotFoundError(session_id)

        try:
            values = self._redis.lrange(self._keys.history(session_id), 0, -1)
            return [self._serializer.loads(item) for item in values]
        except self._redis_module.exceptions.RedisError as exc:
            raise self._wrap_redis_error(exc, "get_history") from exc

    def ping(self) -> bool:
        try:
            return bool(self._redis.ping())
        except self._redis_module.exceptions.RedisError as exc:
            raise self._wrap_redis_error(exc, "ping") from exc

    def close(self) -> None:
        connection_pool: Any = getattr(self._redis, "connection_pool", None)
        if connection_pool is not None:
            connection_pool.disconnect()