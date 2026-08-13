from dataclasses import dataclass
from datetime import datetime

from app.core.schemas.request_status import RequestStatus


@dataclass
class RewardRequest:
    """Модель запроса на получение награды"""

    id: int
    child_profile_id: int
    reward_id: int
    created_at: datetime
    updated_at: datetime
    status: RequestStatus = RequestStatus.PENDING
    comment: str | None = None
    processed_at: datetime | None = None
    processed_by: int | None = None
    deleted_at: datetime | None = None
