from onereport import app, forms, generate_urlstr
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
  return flask.redirect(flask.url_for(generate_urlstr(misc.Role.MANAGER.name, "register_personnel")))

@app.route("/onereport/admins/register_user", methods=["GET", "POST"])
@flask_login.login_required
def a_register_user() -> str:
  return flask.redirect(flask.url_for(generate_urlstr(misc.Role.MANAGER.name, "register_user")))

@app.route("/onereport/admins/personnel/<id>/update", methods=["GET", "POST"])
@flask_login.login_required
def a_update_personnel(id: str) -> str:
  return flask.redirect(flask.url_for(generate_urlstr(misc.Role.MANAGER.name, "update_personnel"), id=id))

# TODO:
# pagination
@app.route("/onereport/admins/users", methods=["GET", "POST"])
@flask_login.login_required
def a_get_all_users() -> str:
  order_by = flask.request.args.get("order_by", default="COMPANY")
  order = flask.request.args.get("order", "ASC")
  
  if not_admin():
    return flask.redirect(flask.url_for("home"))
  
  if not order_attr.UserOrderBy.is_valid(order_by):
    flask.flash(f"אין אפשרות לסדר את העצמים לפי {order_by}", category="info")
    return flask.render_template("users/users.html", users=[])

  if not order_attr.Order.is_valid(order):
    flask.flash(f"אין אפשרות לסדר את העצמים בסדר {order}", category="info")
    return flask.render_template("users.html", users=[])
  
  # SELECT * from users
  users = user_dal.find_all_users(order_attr.UserOrderBy[order_by], order_attr.Order[order])
  return flask.render_template("users/users.html", users=[user_dto.UserDTO(user) for user in users])

@app.route("/onereport/admins/personnel", methods=["GET", "POST"])
@flask_login.login_required
def a_get_all_personnel() -> str:
  order_by = flask.request.args.get("order_by", default="LAST_NAME")
  order = flask.request.args.get("order", "ASC")
  
  if not_admin():
    return flask.redirect(flask.url_for("home"))
  
  form = forms.PersonnelListForm()
  if not order_attr.PersonnelOrderBy.is_valid(order_by):
    flask.flash(f"אין אפשרות לסדר את העצמים לפי {order_by}", category="info")
    return flask.render_template("personnel/personnel_list.html", form=form, personnel=[])

  if not order_attr.Order.is_valid(order):
    flask.flash(f"אין אפשרות לסדר את העצמים בסדר {order}", category="info")
    return flask.render_template("personnel/personnel_list.html", form=form, personnel=[])
  
  if form.validate_on_submit():
    order_by = order_attr.PersonnelOrderBy[form.order_by.data]
    order = order_attr.Order[form.order.data]
  elif flask.request.method == "GET":
    order_by = order_attr.PersonnelOrderBy[order_by]
    order = order_attr.Order[order] 

  
  # SELECT * FROM personnel WHERE personnel.active ORDER_BY order_by order
  personnel = personnel_dal.find_all_personnel(order_by, order)
  return flask.render_template("personnel/personnel_list.html", form=form, personnel=[personnel_dto.PersonnelDTO(p) for p in personnel])

@app.route("/onereport/admins/report", methods=["GET", "POST"])
@flask_login.login_required
def a_create_report() -> str:
  return flask.redirect(flask.url_for(generate_urlstr(misc.Role.MANAGER.name, "create_report")))

@app.get("/onereport/admins/reports")
@flask_login.login_required
def a_get_all_reports() -> str:
  company = flask.request.args.get("company", default="")
  order = flask.request.args.get("order", default="DESC")
  return flask.redirect(flask.url_for(generate_urlstr(misc.Role.MANAGER.name, "get_all_reports"), company=company, order=order))

@app.get("/onereport/admins/report/<int:id>")
@flask_login.login_required
def a_get_report(id: int) -> str:
  return flask.redirect(flask.url_for(generate_urlstr(misc.Role.MANAGER.name, "get_report"), id=id))

 