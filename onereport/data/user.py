import sqlalchemy.orm as orm
from sqlalchemy import ForeignKey
from flask_login import UserMixin
from typing import Self
from onereport.data.personnel import Personnel


class User(Personnel, UserMixin):
    __tablename__ = "user"

    id: orm.Mapped[str] = orm.mapped_column(
        ForeignKey("personnel.id"), primary_key=True
    )
    email: orm.Mapped[str] = orm.mapped_column(unique=True)
    role: orm.Mapped[str]

    __mapper_args__ = {
        "polymorphic_identity": "user",
    }

    def __init__(
        self: Self,
        id: str,
        email: str,
        first_name: str,
        last_name: str,
        role: str,
        company: str,
        platoon: str,
        /,
    ) -> None:
        super().__init__(
            id, first_name, last_name, company, platoon, email=email, role=role
        )

    def update_user(self: Self, other: Self) -> Self:
        self.update(other)
        self.role = other.role
        return self

    def __repr__(self: Self) -> str:
        repr_str = super().__repr__()
        return f"User({repr_str} email: {self.email}, role: {self.role})"

    def get_id(self: Self) -> str:
        return self.email
