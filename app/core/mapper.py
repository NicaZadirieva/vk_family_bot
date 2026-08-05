from app.database.entities.auth_users import AuthUsers as AuthUsersDb
from app.database.entities.family import Family as FamilyDb
from app.database.entities.user import User as UserDb
from app.database.entities.user_role import UserRole as UserRoleDb
from app.domain.auth_users import AuthUsers as AuthUsersDto
from app.domain.family import Family as FamilyDto
from app.domain.user import User as UserDto
from app.domain.user_role import UserRole as UserRoleDto


class Mapper:
    @staticmethod
    def to_roleDTO(roleDb: UserRoleDb):
        return UserRoleDto[roleDb.name]

    @staticmethod
    def to_userDTO(userDb: UserDb):
        return UserDto(
            id=userDb.id,
            role=Mapper.to_roleDTO(userDb.role),
            username=userDb.username,
            family_id=userDb.family_id,
            timezone=userDb.timezone,
            vk_id=userDb.vk_id,
            child_profile_id=userDb.child_profile_id,
        )

    @staticmethod
    def to_roleDb(roleDto: UserRoleDto):
        return UserRoleDb[roleDto.name]

    @staticmethod
    def to_userDb(userDto: UserDto):
        return UserDb(
            id=userDto.id,
            role=Mapper.to_roleDb(userDto.role),
            username=userDto.username,
            family_id=userDto.family_id,
            timezone=userDto.timezone,
            vk_id=userDto.vk_id,
            child_profile_id=userDto.child_profile_id,
        )

    @staticmethod
    def to_FamilyDto(familyDb: FamilyDb):
        return FamilyDto(
            id=familyDb.id,
            name=familyDb.name,
            link=familyDb.link,
            created_at=familyDb.created_at,
        )
