from onereport import app, forms
from onereport.data import model
from onereport.data import misc
from onereport.dto import user_dto, personnel_dto
from onereport.dal import user_dal, personnel_dal
from onereport.dal import order_attr
import flask
import flask_login

def not_admin() -> bool:
  return misc.Role[flask_login.current_user.role] != misc.Role.ADMIN

@app.route("/onereport/admins/register_personnel", methods=["GET", "POST"])
@flask_login.login_required
def a_register_personnel() -> str:
  if not_admin():
    return flask.redirect(flask.url_for("home"))
  
  form = forms.PersonnelRegistrationFrom()
  
  if form.validate_on_submit():
    personnel = model.Personnel(form.id.data.strip(), form.first_name.data.strip(), form.last_name.data.strip(), form.company.data, "1")
    
    # SELECT p FROM personnel WHERE p.id == personnel.id
    old_personnel = personnel_dal.find_personnel_by_id(personnel.id)
    if old_personnel is not None:
      # model.db.session.delete(old_personnel)
      old_personnel.update(personnel)
      model.db.session.commit()
      flask.flash(f"החייל {' '.join((old_personnel.first_name, old_personnel.last_name))} עודכן בהצלחה", category="success")
    else:  
      model.db.session.add(personnel)
      model.db.session.commit()
      flask.flash(f"החייל {' '.join((personnel.first_name, personnel.last_name))} נוסף בהצלחה", category="success")
    
    return flask.redirect(flask.url_for("home"))
    
  return flask.render_template("personnel_registration.html", form=form)

@app.route("/onereport/admins/register_user", methods=["GET", "POST"])
@flask_login.login_required
def a_register_user() -> str:
  if not_admin():
    return flask.redirect(flask.url_for("home"))
  
  form = forms.UserRegistrationFrom()
  
  if form.validate_on_submit():
    user = model.User(form.email.data.strip(), form.first_name.data.strip(), form.last_name.data.strip(), form.role.data, form.company.data)
    
    # SELECT old_user FROM users WHERE old_user.email == user.email
    old_user = user_dal.find_user_by_email(user.email)
    if old_user is not None:
      # model.db.session.delete(old_user)
      old_user.update(user)
      model.db.session.commit()
      flask.flash(f"הפקיד {' '.join((old_user.first_name, old_user.last_name))} עודכן בהצלחה", category="success")
    else:
      model.db.session.add(user)
      model.db.session.commit()
      flask.flash(f"הפקיד {' '.join((user.first_name, user.last_name))} נוסף בהצלחה", category="success")
    
    return flask.redirect(flask.url_for("home"))
  
  return flask.render_template("user_registration.html", form=form)

@app.route("/onereport/admins/personnel/<id>/update", methods=["GET", "POST"])
@flask_login.login_required
def a_update_personnel(id: str) -> str:
  if not_admin():
    return flask.redirect(flask.url_for("home"))
  
  old_personnel = personnel_dal.find_personnel_by_id(id)
  if old_personnel is None:
    print(f"couldn't find {id}")
    flask.flash(f"החייל {id} אינו במסד הנתונים", category="danger")
    return flask.redirect(flask.url_for("a_get_all_personnel"))
  
  print("personel found")
  form = forms.PersonnelUpdateForm()
  if form.validate_on_submit():
    personnel = model.Personnel(old_personnel.id, form.first_name.data.strip(), form.last_name.data.strip(), form.company.data, "1")
    if misc.Active.is_valid(form.active.data):
      personnel.active = misc.Active[form.active.data] == misc.Active.ACTIVE 
    
    old_personnel.update(personnel)
    
    model.db.session.commit()
    
    flask.flash(f"החייל {id} עודכן בהצלחה", category="success")
    return flask.redirect(flask.url_for("a_get_all_personnel"))
  
  if flask.request.method == "GET":
    form.id.data = old_personnel.id
    form.first_name.data, form.last_name.data = old_personnel.first_name, old_personnel.last_name
    form.company.data = old_personnel.company
    form.active.data = old_personnel.active
  
    return flask.render_template("personnel.html", form=form)  
  
  return flask.redirect(flask.url_for("a_get_all_personnel"))

# TODO:
# pagination
@app.route("/onereport/admins/users", methods=["GET", "POST"])
@flask_login.login_required
def a_get_all_users(order_by: str = "COMPANY", order: str = "ASC") -> str:
  if not_admin():
    return flask.redirect(flask.url_for("home"))
  
  if not order_attr.UserOrderBy.is_valid(order_by):
    flask.flash(f"אין אפשרות לסדר את העצמים לפי {order_by}", category="info")
    return flask.render_template("users.html", users=[])

  if not order_attr.Order.is_valid(order):
    flask.flash(f"אין אפשרות לסדר את העצמים בסדר {order}", category="info")
    return flask.render_template("users.html", users=[])
  
  # SELECT * from users
  users = user_dal.find_all_users(order_attr.UserOrderBy[order_by], order_attr.Order[order])
  return flask.render_template("users.html", users=[user_dto.UserDTO(user) for user in users])

@app.route("/onereport/admins/personnel", methods=["GET", "POST"])
@flask_login.login_required
def a_get_all_personnel(order_by: str = "LAST_NAME", order: str = "ASC") -> str:
  if not_admin():
    return flask.redirect(flask.url_for("home"))
  
  form = forms.PersonnelListForm()
  if not order_attr.PersonnelOrderBy.is_valid(order_by):
    flask.flash(f"אין אפשרות לסדר את העצמים לפי {order_by}", category="info")
    return flask.render_template("personnel_list.html", form=form, personnel=[])

  if not order_attr.Order.is_valid(order):
    flask.flash(f"אין אפשרות לסדר את העצמים בסדר {order}", category="info")
    return flask.render_template("personnel_list.html", form=form, personnel=[])
  
  if form.validate_on_submit():
    order_by = order_attr.PersonnelOrderBy[form.order_by.data]
    order = order_attr.Order[form.order.data]
  elif flask.request.method == "GET":
    order_by = order_attr.PersonnelOrderBy[order_by]
    order = order_attr.Order[order] 

  
  # SELECT * FROM personnel WHERE personnel.active ORDER_BY order_by order
  personnel = personnel_dal.find_all_personnel(order_by, order)
  return flask.render_template("personnel_list.html", form=form, personnel=[personnel_dto.PersonnelDTO(p) for p in personnel])

 