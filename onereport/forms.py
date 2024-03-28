from typing import Self
import flask_wtf
import wtforms
import flask_login
import wtforms.validators as validators
from onereport.data import misc
from onereport.dal import personnel_dal, user_dal, order_attr
from onereport.dto import personnel_dto


class PersonnelRegistrationFrom(flask_wtf.FlaskForm):
    id = wtforms.StringField(
        "מספר אישי",
        validators=[validators.InputRequired("שדה חובה"), validators.Length(7, 7)],
    )
    first_name = wtforms.StringField(
        "שם פרטי",
        validators=[validators.InputRequired("שדה חובה"), validators.Length(2, 10)],
    )
    last_name = wtforms.StringField(
        "שם משפחה",
        validators=[validators.InputRequired("שדה חובה"), validators.Length(2, 15)],
    )
    company = wtforms.SelectField(
        "פלוגה",
        choices=[
            (name, member.value) for name, member in misc.Company._member_map_.items()
        ],
    )
    platoon = wtforms.SelectField(
        "מחלקה",
        choices=[
            (name, member.value) for name, member in misc.Platoon._member_map_.items()
        ],
    )

    submit = wtforms.SubmitField("הוסף חייל")

    def validate_id(self: Self, id: wtforms.StringField) -> None:
        personnel = personnel_dal.find_personnel_by_id(id.data)
        if personnel:
            raise wtforms.ValidationError("Personnel already exists")

    def validate_company(self: Self, company: wtforms.SelectField) -> None:
        if not misc.Company.is_valid(company.data):
            raise wtforms.ValidationError("Invalid company")

    def validate_platoon(self: Self, platoon: wtforms.SelectField) -> None:
        if not misc.Platoon.is_valid(platoon.data):
            raise wtforms.ValidationError("Invalid platoon")


class UserRegistrationFrom(flask_wtf.FlaskForm):
    email = wtforms.EmailField(
        "אימייל",
        validators=[
            validators.InputRequired("שדה חובה"),
            validators.Email("שדה לא תקין"),
        ],
    )
    first_name = wtforms.StringField(
        "שם פרטי",
        validators=[validators.InputRequired("שדה חובה"), validators.Length(2, 25)],
    )
    last_name = wtforms.StringField(
        "שם משפחה",
        validators=[validators.InputRequired("שדה חובה"), validators.Length(2, 25)],
    )
    company = wtforms.SelectField(
        "פלוגה",
        choices=[
            (name, member.value) for name, member in misc.Company._member_map_.items()
        ],
    )
    role = wtforms.SelectField(
        "תפקיד",
        choices=[
            (name, member.value) for name, member in misc.Role._member_map_.items()
        ],
    )

    submit = wtforms.SubmitField("הוסף משתמש")

    def validate_email(self: Self, email: wtforms.StringField) -> None:
        user = user_dal.find_user_by_email(email.data)
        if user:
            raise wtforms.ValidationError("User already exists")

    def validate_role(self: Self, role: wtforms.SelectField) -> None:
        if not misc.Role.is_valid(role.data):
            raise wtforms.ValidationError("Invalid role")

        current_user_role = flask_login.current_user.role
        if not misc.Role.is_valid(current_user_role):
            raise wtforms.ValidationError("Invalid role")

        if (
            misc.Role[current_user_role] != misc.Role.ADMIN
            and role.data == misc.Role.ADMIN.name
        ):
            raise wtforms.ValidationError("Permission denied")


class PersonnelListForm(flask_wtf.FlaskForm):
    order_by = wtforms.SelectField(
        "סדר לפי",
        choices=[
            (name, member.value)
            for name, member in order_attr.PersonnelOrderBy._member_map_.items()
        ],
    )
    order = wtforms.SelectField(
        "בסדר",
        choices=[
            (name, member.value)
            for name, member in order_attr.Order._member_map_.items()
        ],
    )

    submit = wtforms.SubmitField("סדר")

    def validate_order_by(self: Self, order_by: wtforms.SelectField) -> None:
        if not order_attr.PersonnelOrderBy.is_valid(order_by.data):
            raise wtforms.ValidationError("Invalid order by")

    def validate_order(self: Self, order: wtforms.SelectField) -> None:
        if not order_attr.Order.is_valid(order.data):
            raise wtforms.ValidationError("Invalid order")


class PersonnelUpdateForm(flask_wtf.FlaskForm):
    id = wtforms.StringField("מספר אישי")
    first_name = wtforms.StringField(
        "שם פרטי",
        validators=[validators.InputRequired("שדה חובה"), validators.Length(2, 10)],
    )
    last_name = wtforms.StringField(
        "שם משפחה",
        validators=[validators.InputRequired("שדה חובה"), validators.Length(2, 15)],
    )
    company = wtforms.SelectField(
        "פלוגה",
        choices=[
            (name, member.value) for name, member in misc.Company._member_map_.items()
        ],
    )
    platoon = wtforms.SelectField(
        "מחלקה",
        choices=[
            (name, member.value) for name, member in misc.Platoon._member_map_.items()
        ],
    )
    active = wtforms.SelectField(
        "פעיל",
        choices=[
            (name, member.value) for name, member in misc.Active._member_map_.items()
        ],
    )

    submit = wtforms.SubmitField("עדכן")

    def validate_company(self: Self, company: wtforms.SelectField) -> None:
        if not misc.Company.is_valid(company.data):
            raise wtforms.ValidationError("Invalid company")

    def validate_active(self: Self, active: wtforms.SelectField) -> None:
        if not misc.Active.is_valid(active.data):
            raise wtforms.ValidationError("invalid value")

    def validate_platoon(self: Self, platoon: wtforms.SelectField) -> None:
        if not misc.Platoon.is_valid(platoon.data):
            raise wtforms.ValidationError("Invalid platoon")


class UserUpdateForm(flask_wtf.FlaskForm):
    email = wtforms.StringField("אימייל")
    first_name = wtforms.StringField(
        "שם פרטי",
        validators=[validators.InputRequired("שדה חובה"), validators.Length(2, 10)],
    )
    last_name = wtforms.StringField(
        "שם משפחה",
        validators=[validators.InputRequired("שדה חובה"), validators.Length(2, 15)],
    )
    role = wtforms.SelectField(
        "תפקיד",
        choices=[
            (name, member.value) for name, member in misc.Role._member_map_.items()
        ],
    )
    company = wtforms.SelectField(
        "פלוגה",
        choices=[
            (name, member.value) for name, member in misc.Company._member_map_.items()
        ],
    )
    active = wtforms.SelectField(
        "פעיל",
        choices=[
            (name, member.value) for name, member in misc.Active._member_map_.items()
        ],
    )

    submit = wtforms.SubmitField("עדכן")

    def validate_company(self: Self, company: wtforms.SelectField) -> None:
        if not misc.Company.is_valid(company.data):
            raise wtforms.ValidationError("Invalid company")

    def validate_active(self: Self, active: wtforms.SelectField) -> None:
        if not misc.Active.is_valid(active.data):
            raise wtforms.ValidationError("invalid value")

    def validate_role(self: Self, role: wtforms.SelectField) -> None:
        if not misc.Role.is_valid(role.data):
            raise wtforms.ValidationError("Invalid role")

        current_user_role = flask_login.current_user.role
        if not misc.Role.is_valid(current_user_role):
            raise wtforms.ValidationError("Invalid role")

        if (
            misc.Role[current_user_role] != misc.Role.ADMIN
            and role.data == misc.Role.ADMIN.name
        ):
            raise wtforms.ValidationError("Permission denied")


class UpdateReportForm(flask_wtf.FlaskForm):
    submit = wtforms.SubmitField("שלח")

    def append_all(self: Self, personnel: list[personnel_dto.PersonnelDTO]) -> None:
        for p in personnel:
            self.personnel.append_entry(wtforms.BooleanField())
            self.personnel.entries[-1].data = False
            self.personnel.entries[-1].id = p.id

        for entry in self.personnel.entries:
            print(entry)
