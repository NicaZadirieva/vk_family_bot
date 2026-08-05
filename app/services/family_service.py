from app.core.mapper import Mapper
from app.database.repositories.family_repository import FamilyRepository


class FamilyService:
    def __init__(self, family_repo: FamilyRepository):
        self._family_repo = family_repo

    async def search_family_by_link(self, link: str):
        family_entry = await self._family_repo.search_family_by_link(link)
        if family_entry:
            return Mapper.to_FamilyDto(family_entry)
        else:
            return None
