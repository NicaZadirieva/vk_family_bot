from dataclasses import dataclass


@dataclass
class AuthUsers:
    id: int
    user_id: int
    family_id: int
    password_hash: str
