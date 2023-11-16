from dataclasses import dataclass
from typing import TypedDict


class UserJwtDto(TypedDict):
    id: int
    user_id: str
    email: str
    expire_at: str
