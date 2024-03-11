from data.item_entity import ItemEntity
from data.misc import Role, Space
from data.user_entity import UserEntity
from dto.item_dto import ItemDTO
from dto.user_dto import UserDTO


def item_dto_to_entity(dto: ItemDTO) -> ItemEntity:
  pass

def item_entity_to_dto(entity: ItemEntity) -> ItemDTO:
  pass

def user_dto_to_entity(dto: UserDTO) -> UserEntity:
  if dto.role.upper() not in Role.__members__.keys():
    raise ValueError()
  
  if dto.space.upper() not in Space.__members__.keys():
    raise ValueError()
  
  return UserEntity(dto.username, dto.role, dto.space)

def user_entity_to_dto(entity: UserEntity) -> UserDTO:
  return UserDTO(entity.username, entity.role, entity.space)