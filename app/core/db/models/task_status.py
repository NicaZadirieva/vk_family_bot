from enum import Enum


class TaskStatus(Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"
