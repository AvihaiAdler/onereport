from typing import Optional, Self, Set
import sqlalchemy.orm as orm
from flask_sqlalchemy import SQLAlchemy
import datetime
import sqlalchemy
from flask_login import UserMixin, LoginManager


class Base(orm.DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
login_manager.login_view = "common.login"
login_manager.login_message_category = "info"
login_manager.login_message = "אנא התחבר למערכת על מנת להכנס"

personnel_report_rel = sqlalchemy.Table(
    "personnel_report_rel",
    Base.metadata,
    sqlalchemy.Column(
        "report_id", sqlalchemy.ForeignKey("report.id"), primary_key=True
    ),
    sqlalchemy.Column(
        "personnel_id", sqlalchemy.ForeignKey("personnel.id"), primary_key=True
    ),
)


class Personnel(db.Model):
    __tablename__ = "personnel"

    id: orm.Mapped[str] = orm.mapped_column(primary_key=True)
    first_name: orm.Mapped[str]
    last_name: orm.Mapped[str]
    company: orm.Mapped[str]
    platoon: orm.Mapped[str]
    active: orm.Mapped[bool] = orm.mapped_column(default=True)
    date_added: orm.Mapped[datetime.date] = orm.mapped_column(
        default=datetime.date.today
    )
    date_removed: orm.Mapped[Optional[datetime.date]] = orm.mapped_column(default=None)

    type: orm.Mapped[str]
    __mapper_args__ = {
        "polymorphic_identity": "personnel",
        "polymorphic_on": "type",
    }

    dates_present: orm.Mapped[Set["Report"]] = orm.relationship(
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


class User(Personnel, UserMixin):
    __tablename__ = "user"

    id: orm.Mapped[str] = orm.mapped_column(
        sqlalchemy.ForeignKey("personnel.id"), primary_key=True
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


class Report(db.Model):
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    date: orm.Mapped[datetime.date] = orm.mapped_column(default=datetime.date.today)
    company: orm.Mapped[str]
    last_edited: orm.Mapped[datetime.datetime] = orm.mapped_column(default=datetime.datetime.now)
    
    edited_by_id: orm.Mapped[Optional[str]] = orm.mapped_column(sqlalchemy.ForeignKey("user.id"))
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


@login_manager.user_loader
def load_user(email: str) -> User | None:
    return db.session.scalar(sqlalchemy.select(User).filter(User.email == email))
