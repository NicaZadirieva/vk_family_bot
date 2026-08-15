from app.core.db.models.family import Family as FamilyDb
from app.core.schemas.family import Family as FamilyScheme


class DbToPydanticSchemeMapper:
    """Превращает dict(sql) -> Pydantic-схему"""

    @staticmethod
    def to_family_scheme(family_db: FamilyDb):
        return FamilyScheme(
            id=family_db.id,
            name=family_db.name,
            created_at=family_db.created_at,
            link=family_db.link,
        )
