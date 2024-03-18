import flask_wtf
import wtforms
import wtforms.validators as validators
from .data.misc import Space, Role
from .data import model

class PersonnelRegistrationFrom(flask_wtf.FlaskForm):
  id = wtforms.StringField("מספר אישי", validators=[validators.DataRequired(), validators.Length(7,7)])
  first_name = wtforms.StringField("שם פרטי", validators=[validators.DataRequired(), validators.Length(2, 10)])
  last_name = wtforms.StringField("שם משפחה", validators=[validators.DataRequired(), validators.Length(2, 15)])
  company = wtforms.SelectField("פלוגה", choices=[(name, member.value) for name, member in Space.__members__.items()])
  
  submit = wtforms.SubmitField("הוסף חייל")
  
  def validate_id(self, id: wtforms.StringField) -> None:
    personnel = model.Personnel.query.filter_by(id=id.data).first()
    if personnel:
      raise wtforms.ValidationError("Personnel already exists")
  
  
class UserRegistrationFrom(flask_wtf.FlaskForm):
  email = wtforms.EmailField("אימייל", validators=[validators.DataRequired(), validators.Email()])
  username = wtforms.StringField("שם", validators=[validators.DataRequired(), validators.Length(2, 25)])
  company = wtforms.SelectField("פלוגה", choices=[(name, member.value) for name, member in Space.__members__.items()])
  role = wtforms.SelectField("תפקיד", choices=[(name, member.value) for name, member in Role.__members__.items()])
  
  submit = wtforms.SubmitField("הוסף משתמש")
  
  def validate_email(self, email: wtforms.StringField) -> None:
    user = model.User.query.filter_by(email=email.data).first()
    if user:
      raise wtforms.ValidationError("User already exists")