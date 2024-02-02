import abc
from dataclasses import dataclass
import json
from typing import Any

from redis import Redis


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict):
        pass

    @abc.abstractmethod
    def retrieve_state(self):
        pass


@dataclass
class RedisStorage(BaseStorage):

    redis_adapter: Redis

    def __post_init__(self):
        self.data = self.redis_adapter.get('movies_db')

    def save_state(self, state: dict):
        self.redis_adapter.set('movies_db', json.dumps(state, default=str))
        self.redis_adapter.persist('movies_db')

    def retrieve_state(self):
        return json.loads(self.data) if self.data else {}


@dataclass
class State:

    storage: BaseStorage

    def __post_init__(self):
        self.data = self.storage.retrieve_state()

    def set_state(self, key: str, value: Any):
        self.data[key] = value
        self.storage.save_state(self.data)

    def get_state(self, key: str, default: Any = None):
        return self.data.get(key, default)