from data.misc import Role, Space
from data.personnel_entity import Personnel
from data.user_entity import User
from dto.user_dto import UserDTO
from dto.personnel_dto import PersonnelDTO


def personnel_dto_to_entity(dto: PersonnelDTO) -> Personnel:
  return Personnel(dto.id, dto.first_name, dto.last_name, dto.active)

def personnel_entity_to_dto(entity: Personnel) -> PersonnelDTO:
  return PersonnelDTO(entity.id, entity.first_name, entity.last_name, entity.active)

def user_dto_to_entity(dto: UserDTO) -> User:
  if dto.role.upper() not in Role.__members__.keys():
    raise ValueError()
  
  if dto.space.upper() not in Space.__members__.keys():
    raise ValueError()
  
  return User(dto.email, dto.username, dto.role.upper(), dto.space.upper(), dto.active)

def user_entity_to_dto(entity: User) -> UserDTO:
  return UserDTO(entity.email, entity.username, entity.role, entity.space, entity.active)