from dataclasses import dataclass
from typing import TypedDict


class GoogleJwtDto(TypedDict):
    id: int
    user_id: str
    email: str
    expire_at: str
    auth_type: str


class KakaoJwtDto(TypedDict):
    id: int
    user_id: str
    expire_at: str
    auth_type: str
