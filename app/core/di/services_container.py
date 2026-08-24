from dependency_injector import containers, providers
from app.core.db.session import async_sessionmaker

from app.core.repositories import (
    ChildProfileRepo,
    EventExceptionRepo,
    EventRepo,
    FamilyRepo,
    NoteRepo,
    PasswordRepo,
    PointsTransactionRepo,
    RewardRepo,
    RewardRequestRepo,
    SentReminderRepo,
    TaskRepo,
    UserRepo,
)
from app.core.repositories.in_memory_user_state_repo import InMemoryUserStateRepo
from app.core.services import (
    ChildProfileService,
    EventExceptionService,
    EventService,
    FamilyService,
    NoteService,
    PasswordService,
    PointsTransactionService,
    RewardRequestService,
    RewardService,
    SentReminderService,
    TaskService,
    UserService,
)
from app.core.services.user_state import UserStateService


class ServicesContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    session = providers.Resource(
        async_sessionmaker,
        # shutdown - закрытие сессии при завершении
    )
    # Репозитории с передачей сессии
    child_profile_repo = providers.Factory(
        ChildProfileRepo,
        session=session,  # или session_factory
    )
    event_exception_repo = providers.Factory(EventExceptionRepo, session=session)
    event_repo = providers.Factory(EventRepo, session=session)
    family_repo = providers.Factory(FamilyRepo, session=session)
    note_repo = providers.Factory(NoteRepo, session=session)
    password_repo = providers.Factory(PasswordRepo, session=session)
    points_transaction_repo = providers.Factory(PointsTransactionRepo, session=session)
    reward_request_repo = providers.Factory(RewardRequestRepo, session=session)
    reward_repo = providers.Factory(RewardRepo, session=session)
    sent_reminder_repo = providers.Factory(SentReminderRepo, session=session)
    task_repo = providers.Factory(TaskRepo, session=session)
    user_repo = providers.Factory(UserRepo, session=session)

    # заменить на redis
    user_state_repo = providers.Singleton(InMemoryUserStateRepo)

    # Сервисы
    child_profile_service = providers.Factory(
        ChildProfileService,
        repository=child_profile_repo,
    )
    event_exception_service = providers.Factory(
        EventExceptionService,
        repository=event_exception_repo,
    )
    event_service = providers.Factory(
        EventService,
        repository=event_repo,
    )
    family_service = providers.Factory(
        FamilyService,
        repository=family_repo,
    )
    note_service = providers.Factory(
        NoteService,
        repository=note_repo,
    )
    password_service = providers.Factory(
        PasswordService,
        repository=password_repo,
    )
    points_transaction_service = providers.Factory(
        PointsTransactionService,
        repository=points_transaction_repo,
    )
    reward_request_service = providers.Factory(
        RewardRequestService,
        repository=reward_request_repo,
    )
    reward_service = providers.Factory(
        RewardService,
        repository=reward_repo,
    )
    sent_reminder_service = providers.Factory(
        SentReminderService,
        repository=sent_reminder_repo,
    )
    task_service = providers.Factory(
        TaskService,
        repository=task_repo,
    )
    user_service = providers.Factory(
        UserService,
        repository=user_repo,
    )
    user_state_service = providers.Factory(UserStateService, repository=user_state_repo)
