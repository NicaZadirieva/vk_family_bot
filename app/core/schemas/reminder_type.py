from enum import Enum


class ReminderType(Enum):
    EVENT_START = "event_start"
    EVENT_BIRTHDAY = "event_birthday"
    VACATION_START = "vacation_start"
    TASK_COMPLETE = "task_complete"
    TASK_DECLINE = "task_decline"
    REWARD_REQUEST = "reward_request"
    REWARD_DECLINE = "reward_decline"
