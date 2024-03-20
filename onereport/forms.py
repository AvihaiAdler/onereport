from typing import Self
import flask_wtf
import wtforms
import flask_login
import wtforms.validators as validators
from onereport.data import misc
from onereport.dal import personnel_dal, user_dal

class PersonnelRegistrationFrom(flask_wtf.FlaskForm):
  id = wtforms.StringField("מספר אישי", validators=[validators.InputRequired("שדה חובה"), validators.Length(7,7)])
  first_name = wtforms.StringField("שם פרטי", validators=[validators.InputRequired("שדה חובה"), validators.Length(2, 10)])
  last_name = wtforms.StringField("שם משפחה", validators=[validators.InputRequired("שדה חובה"), validators.Length(2, 15)])
  company = wtforms.SelectField("פלוגה", choices=[(name, member.value) for name, member in misc.Company.__members__.items()])
  
  submit = wtforms.SubmitField("הוסף חייל")
  
  def validate_id(self: Self, id: wtforms.StringField) -> None:
    personnel = personnel_dal.get_personnel_by_id(id.data)
    if personnel:
      raise wtforms.ValidationError("Personnel already exists")
  
  
class UserRegistrationFrom(flask_wtf.FlaskForm):
  email = wtforms.EmailField("אימייל", validators=[validators.InputRequired("שדה חובה"), validators.Email("שדה לא תקין")])
  first_name = wtforms.StringField("שם פרטי", validators=[validators.InputRequired("שדה חובה"), validators.Length(2, 25)])
  last_name = wtforms.StringField("שם משפחה", validators=[validators.InputRequired("שדה חובה"), validators.Length(2, 25)])
  company = wtforms.SelectField("פלוגה", choices=[(name, member.value) for name, member in misc.Company.__members__.items()])
  role = wtforms.SelectField("תפקיד", choices=[(name, member.value) for name, member in misc.Role.__members__.items()])

  submit = wtforms.SubmitField("הוסף משתמש")
  
  def validate_email(self: Self, email: wtforms.StringField) -> None:
    user = user_dal.get_user_by_email(email.data)
    if user:
      raise wtforms.ValidationError("User already exists")
    
  def validate_role(self: Self, role: wtforms.SelectField) -> None:
    if misc.Role[flask_login.current_user.role] != misc.Role.ADMIN and role.data == "ADMIN":
      raise wtforms.ValidationError("Permission denied")