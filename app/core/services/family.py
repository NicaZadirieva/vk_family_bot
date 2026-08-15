import logging

from app.core.mappers.db_to_pydantic import DbToPydanticSchemeMapper
from app.core.repositories.family import FamilyRepo
from app.core.schemas.family import Family
from app.exceptions.not_found_error import NotFoundError

logger = logging.getLogger(__name__)


class FamilyService:
    """Работа над сущностью Семья"""

    def __init__(self, repo: FamilyRepo):
        self._repo = repo

    async def get_family_by_link(self, link: str):
        family = await self._repo.get_family_by_link(link)
        if family:
            return DbToPydanticSchemeMapper.to_family_scheme(family[0])
        else:
            raise NotFoundError(entity="Семья", identifier=f"link {link}")

    async def create(self, name: str, link: str) -> Family:
        new_family = await self._repo.create_family(name, link)
        new_family_scheme = DbToPydanticSchemeMapper.to_family_scheme(new_family)
        return new_family_scheme
