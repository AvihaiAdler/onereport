from typing import Self
from onereport.data import misc
from onereport.data import User


class UserDTO:
    def __init__(self: Self, user: User) -> None:
        self.id = user.id
        self.first_name = user.first_name
        self.last_name = user.last_name
        self.email = user.email
        self.role = misc.Role[user.role].value.name
        self.company = misc.Company[user.company].value
        self.platoon = misc.Platoon[user.platoon].value
        self.active = user.active
