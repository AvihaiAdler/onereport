from typing import Self
import flask_wtf
import wtforms
import flask_login
import wtforms.validators as validators
import email_validator
from onereport.data import misc
from onereport.dal import order_attr

ID_LEN = 7


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
        if len(id.data) < ID_LEN:
            raise wtforms.ValidationError("המס' האישי חייב להכיל לפחות {ID_LEN} תווים")
        try:
            int(id.data)
        except ValueError as _:
            raise wtforms.ValidationError("מס' אישי לא תקין")

    def validate_company(self: Self, company: wtforms.SelectField) -> None:
        if not misc.Company.is_valid(company.data):
            raise wtforms.ValidationError("ערך לא תקין")

    def validate_platoon(self: Self, platoon: wtforms.SelectField) -> None:
        if not misc.Platoon.is_valid(platoon.data):
            raise wtforms.ValidationError("ערך לא תקין")


class UserRegistrationFrom(flask_wtf.FlaskForm):
    id = wtforms.StringField("מספר אישי")
    email = wtforms.EmailField(
        "אימייל",
        validators=[
            validators.InputRequired("שדה חובה"),
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
    platoon = wtforms.SelectField(
        "מחלקה",
        choices=[
            (name, member.value) for name, member in misc.Platoon._member_map_.items()
        ],
    )
    role = wtforms.SelectField(
        "תפקיד",
        choices=[
            (name, permission.value.name)
            for name, permission in misc.Role._member_map_.items()
        ],
    )

    submit = wtforms.SubmitField("הוסף משתמש")

    def validate_email(self: Self, email: wtforms.EmailField) -> None:
        try:
            email_validator.validate_email(email.data, check_deliverability=False)
        except email_validator.EmailNotValidError as _:
            raise wtforms.ValidationError("אימייל לא תקין")

    def validate_role(self: Self, role: wtforms.SelectField) -> None:
        if not misc.Role.is_valid(role.data):
            raise wtforms.ValidationError("תפקיד לא תקין")

        current_user_role_level = misc.Role.get_level(flask_login.current_user.role)
        if current_user_role_level is None:
            raise wtforms.ValidationError("הרשאתך אינה תקינה")

        if current_user_role_level > misc.Role.get_level(role.data):
            raise wtforms.ValidationError("אינך רשאי.ת ליצור משתמש עם הרשאה זו")


class PersonnelListForm(flask_wtf.FlaskForm):
    company = wtforms.SelectField(
        "פלוגה",
        choices=[
            (name, member.value) for name, member in misc.Company._member_map_.items()
        ],
    )
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
            raise wtforms.ValidationError("ערך לא תקין")

    def validate_order(self: Self, order: wtforms.SelectField) -> None:
        if not order_attr.Order.is_valid(order.data):
            raise wtforms.ValidationError("ערך לא תקין")


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
            raise wtforms.ValidationError("ערך לא תקין")

    def validate_active(self: Self, active: wtforms.SelectField) -> None:
        if not misc.Active.is_valid(active.data):
            raise wtforms.ValidationError("ערך לא תקין")

    def validate_platoon(self: Self, platoon: wtforms.SelectField) -> None:
        if not misc.Platoon.is_valid(platoon.data):
            raise wtforms.ValidationError("ערך לא תקין")


class UserUpdateForm(flask_wtf.FlaskForm):
    id = wtforms.StringField("מספר אישי")
    email = wtforms.EmailField("אימייל")
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
            (name, permission.value.name)
            for name, permission in misc.Role._member_map_.items()
        ],
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
    delete = wtforms.SubmitField("הסר")

    def validate_company(self: Self, company: wtforms.SelectField) -> None:
        if not misc.Company.is_valid(company.data):
            raise wtforms.ValidationError("ערך לא תקין")

    def validate_active(self: Self, active: wtforms.SelectField) -> None:
        if not misc.Active.is_valid(active.data):
            raise wtforms.ValidationError("ערך לא תקין")

    def validate_platoon(self: Self, platoon: wtforms.SelectField) -> None:
        if not misc.Platoon.is_valid(platoon.data):
            raise wtforms.ValidationError("ערך לא תקין")

    def validate_email(self: Self, email: wtforms.EmailField) -> None:
        try:
            email_validator.validate_email(email.data, check_deliverability=False)
        except email_validator.EmailNotValidError as _:
            raise wtforms.ValidationError("אימייל לא תקין")

    def validate_role(self: Self, role: wtforms.SelectField) -> None:
        if not misc.Role.is_valid(role.data):
            raise wtforms.ValidationError("תפקיד לא תקין")

        current_user_role_level = misc.Role.get_level(flask_login.current_user.role)
        if current_user_role_level is None:
            raise wtforms.ValidationError("הרשאתך אינה תקינה")

        if current_user_role_level > misc.Role.get_level(role.data):
            raise wtforms.ValidationError("אינך רשאי.ת ליצור משתמש עם הרשאה זו")


class UpdateReportForm(flask_wtf.FlaskForm):
    submit = wtforms.SubmitField("שלח")
