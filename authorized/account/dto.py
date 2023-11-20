from dataclasses import dataclass
from typing import TypedDict


class OAuthJwtDto(TypedDict):
    auth_type: str
    id: int
    user_id: str
    expire_at: str
