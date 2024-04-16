import sqlalchemy.orm as orm
from datetime import date
from typing import Optional, Self, Set
from onereport.data.base import db
from onereport.data.personnel_to_report import personnel_report_rel


class Personnel(db.Model):
    __tablename__ = "personnel"

    id: orm.Mapped[str] = orm.mapped_column(primary_key=True)
    first_name: orm.Mapped[str]
    last_name: orm.Mapped[str]
    company: orm.Mapped[str]
    platoon: orm.Mapped[str]
    active: orm.Mapped[bool] = orm.mapped_column(default=True)
    date_added: orm.Mapped[date] = orm.mapped_column(default=date.today)
    date_removed: orm.Mapped[Optional[date]] = orm.mapped_column(default=None)

    type: orm.Mapped[str]
    __mapper_args__ = {
        "polymorphic_identity": "personnel",
        "polymorphic_on": "type",
    }

    dates_present: orm.Mapped[Set["Report"]] = orm.relationship(  # noqa: F821 # type: ignore
        secondary=personnel_report_rel, back_populates="presence", lazy=True
    )

    def __init__(
        self: Self,
        id: str,
        first_name: str,
        last_name: str,
        company: str,
        platoon: str,
        /,
        **kwargs,
    ) -> None:
        super().__init__(
            id=id,
            first_name=first_name,
            last_name=last_name,
            company=company,
            platoon=platoon,
            **kwargs,
        )

    def update(self: Self, other: Self) -> Self:
        self.first_name, self.last_name = other.first_name, other.last_name
        self.company = other.company
        self.platoon = other.platoon
        self.active = other.active
        self.date_removed = other.date_removed
        return self

    def update_personnel(self: Self, other: Self) -> Self:
        return self.update(other)

    def __repr__(self: Self) -> str:
        return f"Personnel(id: {self.id}, full name:{' '.join((self.first_name, self.last_name))}, company: {self.company}, platoon: {self.platoon}, active: {self.active})"
