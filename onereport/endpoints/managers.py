from onereport import app, forms
from onereport.data import model
from onereport.data import misc
from onereport.data import user_dto
import flask
import flask_login

@app.route("/onereport/managers/register_personnel", methods=["GET", "POST"])
@flask_login.login_required
def register_personnel() -> str:
  if misc.Role[flask_login.current_user.role] == misc.Role.USER:
    return flask.redirect(flask.url_for("home"))
  
  form = forms.PersonnelRegistrationFrom()
  
  if form.validate_on_submit():
    personnel = model.Personnel(form.id.data, form.first_name.data, form.last_name.data, form.company.data, "1")
    model.db.session.add(personnel)
    model.db.session.commit()
    
    flask.flash(f"החייל {form.first_name.data} {form.last_name.data} נוסף בהצלחה", "success")
    return flask.redirect(flask.url_for("home"))
    
  return flask.render_template("personnel_registration.html", form=form)

@app.route("/onereport/managers/register_user", methods=["GET", "POST"])
@flask_login.login_required
def register_user() -> str:
  if misc.Role[flask_login.current_user.role] == misc.Role.USER:
    return flask.redirect(flask.url_for("home"))
  
  form = forms.UserRegistrationFrom()
  
  if form.validate_on_submit():
    user = model.User(form.email.data, form.username.data, form.role.data, form.company.data)
    model.db.session.add(user)
    model.db.session.commit()
    
    flask.flash(f"הפקיד {form.username.data} נוסף בהצלחה")
    return flask.redirect(flask.url_for("home"))
  
  return flask.render_template("user_registration.html", form=form)

# TODO:
# pagination
@app.route("/onereport/managers/users", methods=["GET", "POST"])
@flask_login.login_required
def get_all_active_users() -> str:
  current_user = flask_login.current_user
  if misc.Role[current_user.role] == misc.Role.USER:
    return flask.redirect(flask.url_for("home"))
  
  users = model.db.session.query(model.User).filter(model.User.role != misc.Role.ADMIN.name).filter(model.User.active).all()
  return flask.render_template("users.html", users=[user_dto.UserDto(user) for user in users])