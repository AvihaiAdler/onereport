from onereport import app, forms
from onereport.data import model
from onereport.data import misc
from onereport.dto import user_dto, personnel_dto
from onereport.dal import personnel_dal, user_dal
from onereport.dal import order_attr
import flask
import flask_login

# TODO:
# might want to implement a better upsert

@app.route("/onereport/managers/register_personnel", methods=["GET", "POST"])
@flask_login.login_required
def m_register_personnel() -> str:
  if misc.Role[flask_login.current_user.role] != misc.Role.MANAGER:
    return flask.redirect(flask.url_for("home"))
  
  form = forms.PersonnelRegistrationFrom()
  
  if form.validate_on_submit():
    personnel = model.Personnel(form.id.data.strip(), form.first_name.data.strip(), form.last_name.data.strip(), form.company.data, "1")
    
    # SELECT p FROM personnel WHERE p.id == personnel.id
    old_personnel = personnel_dal.get_personnel_by_id(personnel.id)
    if old_personnel is not None:
      # model.db.session.delete(old_personnel)
      old_personnel.update(personnel)
      model.db.session.commit()
      flask.flash(f"החייל {' '.join((personnel.first_name, personnel.last_name))} עודכן בהצלחה", category="success")
    else:
      model.db.session.add(personnel)
      model.db.session.commit()
      flask.flash(f"החייל {form.first_name.data} {form.last_name.data} נוסף בהצלחה", category="success")
    
    return flask.redirect(flask.url_for("home"))
    
  return flask.render_template("personnel_registration.html", form=form)

@app.route("/onereport/managers/register_user", methods=["GET", "POST"])
@flask_login.login_required
def m_register_user() -> str:
  if misc.Role[flask_login.current_user.role] != misc.Role.MANAGER:
    return flask.redirect(flask.url_for("home"))
  
  form = forms.UserRegistrationFrom()
  
  if form.validate_on_submit():
    user = model.User(form.email.data.strip(), form.first_name.data.strip(), form.last_name.data.strip(), form.role.data, form.company.data)
    
    # SELECT old_user FROM users WHERE old_user.email == user.email
    old_user = user_dal.get_user_by_email(user.email)
    if old_user is not None:
      # model.db.session.delete(old_user)
      old_user.update(user)
      model.db.session.commit()
      flask.flash(f"הפקיד {' '.join((user.first_name, user.last_name))} עודכן בהצלחה", category="success")
    else:
      model.db.session.add(user)
      model.db.session.commit()
      flask.flash(f"הפקיד {' '.join((user.first_name, user.last_name))} נוסף בהצלחה", category="success")
    
    return flask.redirect(flask.url_for("home"))
  
  return flask.render_template("user_registration.html", form=form)

# TODO:
# pagination
@app.route("/onereport/managers/users", methods=["GET", "POST"])
@flask_login.login_required
def m_get_all_active_users(order_by: str = "COMPANY", order: str = "ASC") -> str:
  current_user = flask_login.current_user
  if misc.Role[current_user.role] != misc.Role.MANAGER:
    return flask.redirect(flask.url_for("home"))
  
  if not order_attr.UserOrderBy.is_valid(order_by):
    flask.flash(f"אין אפשרות לסדר את העצמים לפי {order_by}", category="info")
    return flask.render_template("users.html", users=[])

  if not order_attr.Order.is_valid(order):
    flask.flash(f"אין אפשרות לסדר את העצמים בסדר {order}", category="info")
    return flask.render_template("users.html", users=[])
  
  # SELECT * FROM users WHERE user.active AND user.role != ADMIN ORDER_BY order_by order
  users = user_dal.get_all_active_users(order_attr.UserOrderBy[order_by], order_attr.Order(order))
  return flask.render_template("users.html", users=[user_dto.UserDTO(user) for user in users])

# TODO:
# pagination
@app.route("/onereport/managers/personnel", methods=["GET", "POST"])
@flask_login.login_required
def m_get_all_personnel(order_by: str = "LAST_NAME", order: str = "ASC") -> str:
  if misc.Role[flask_login.current_user.role] != misc.Role.MANAGER:
    return flask.redirect(flask.url_for("home"))
  
  form = forms.PersonnelListForm()
  if form.validate_on_submit():
    order_by = order_attr.PersonnelOrderBy[form.order_by.data]
    order = order_attr.Order[form.order.data]
    
    personnel = personnel_dal.get_all_active_personnel(order_by, order)
    return flask.render_template("personnel.html", personnel=[personnel_dto.PersonnelDTO(p) for p in personnel])
  
  if not order_attr.PersonnelOrderBy.is_valid(order_by):
    flask.flash(f"אין אפשרות לסדר את העצמים לפי {order_by}", category="info")
    return flask.render_template("personnel.html", personnel=[])

  if not order_attr.Order.is_valid(order):
    flask.flash(f"אין אפשרות לסדר את העצמים בסדר {order}", category="info")
    return flask.render_template("personnel.html", personnel=[])
  
  # SELECT * FROM personnel WHERE personnel.active ORDER_BY order_by order
  personnel = personnel_dal.get_all_active_personnel(order_attr.PersonnelOrderBy[order_by], order_attr.Order[order])
  return flask.render_template("personnel.html", personnel=[personnel_dto.PersonnelDTO(p) for p in personnel])