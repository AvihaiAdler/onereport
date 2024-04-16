import sqlalchemy.orm as orm
from sqlalchemy import ForeignKey
from typing import Optional, Self, Set
import datetime
from onereport.data.base import db
from onereport.data.personnel_to_report import personnel_report_rel
from onereport.data.user import User
from onereport.data.personnel import Personnel


class Report(db.Model):
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    date: orm.Mapped[datetime.date] = orm.mapped_column(default=datetime.date.today)
    company: orm.Mapped[str]
    last_edited: orm.Mapped[datetime.datetime] = orm.mapped_column(
        default=datetime.datetime.now
    )

    edited_by_id: orm.Mapped[Optional[str]] = orm.mapped_column(ForeignKey("user.id"))
    edited_by: orm.Mapped[Optional["User"]] = orm.relationship()

    presence: orm.Mapped[Set["Personnel"]] = orm.relationship(
        secondary=personnel_report_rel, back_populates="dates_present", lazy=True
    )

    def __init__(self: Self, company: str, user: User, /) -> None:
        super().__init__(company=company, edited_by=user)

    def __repr__(self: Self) -> str:
        return f"Report(date: {self.date.day}/{self.date.month}/{self.date.year}, company: {self.company})"

    def update(self: Self, presence: set[Personnel], user: User, /) -> None:
        self.presence = presence
        self.edited_by = user
        self.last_edited = datetime.datetime.now()
