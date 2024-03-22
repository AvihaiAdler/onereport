from onereport import app, forms
from onereport.data import model, misc
from onereport.dal import personnel_dal, order_attr
from onereport.dto import personnel_dto
import flask
import flask_login

@app.get("/")
@app.get("/onereport/login") 
def login() -> str:
  return flask.render_template("login.html")

@app.get("/onereport/logout")
@flask_login.login_required
def logout() -> str:
    flask_login.logout_user()
    return flask.redirect(flask.url_for("login"))

@app.get("/onereport/home")
@flask_login.login_required
def home() -> str:
  title = misc.Company[flask_login.current_user.company].value
  return flask.render_template("home.html", title=title)

@app.get("/onereport/about")
@flask_login.login_required
def about() -> str:
  return "about"

def not_user() -> bool:
  return misc.Role[flask_login.current_user.role] != misc.Role.USER

@app.get("/onereport/users/personnel")
@flask_login.login_required
def u_get_all_active_personnel(order_by: str = "ID", order: str = "ASC") -> str:
  if not_user():
    return flask.redirect(flask.url_for("home"))
  
  if not order_attr.PersonnelOrderBy.is_valid(order_by):
    flask.flash(f"אין אפשרות לסדר את העצמים לפי {order_by}", category="info")
    return flask.render_template("personnel_list.html", personnel=[])

  if not order_attr.Order.is_valid(order):
    flask.flash(f"אין אפשרות לסדר את העצמים בסדר {order}", category="info")
    return flask.render_template("personnel_list.html", personnel=[])
  
  company = misc.Company[flask_login.current_user.company]
  personnel = personnel_dal.find_all_active_personnel_by_company(company, order_attr.PersonnelOrderBy[order_by], order_attr.Order[order])
  
  return flask.render_template("personnel_list.html", personnel=[personnel_dto.PersonnelDTO(p) for p in personnel])

@app.route("/onereport/users/personnel/<id>/update", methods=["GET", "POST"])
@flask_login.login_required
def u_update_personnel(id: str) -> str:
  if not_user():
    return flask.redirect(flask.url_for("home"))
  
  old_personnel = personnel_dal.find_personnel_by_id(id)
  if old_personnel is None:
    flask.flash(f"החייל {id} אינו במסד הנתונים", category="danger")
    return flask.redirect(flask.url_for("u_get_all_active_personnel"))
  
  form = forms.PersonnelUpdateForm()
  if form.validate_on_submit():
    personnel = model.Personnel(old_personnel.id, form.first_name.data.strip(), form.last_name.data.strip(), form.company.data, "1")
    if misc.Active.is_valid(form.active.data):
      personnel.active = misc.Active[form.active.data] == misc.Active.ACTIVE 
    
    old_personnel.update(personnel)
    personnel.company = old_personnel.company # to ensure users cannot update Personnel::company
    
    model.db.session.commit()
    
    flask.flash(f"החייל {id} עודכן בהצלחה", category="success")
    return flask.redirect(flask.url_for("u_get_all_active_personnel"))
  
  if flask.request.method == "GET":
    form.id.data = old_personnel.id
    form.first_name.data, form.last_name.data = old_personnel.first_name, old_personnel.last_name
    form.company.data = old_personnel.company
    form.active.data = old_personnel.active
  
    return flask.render_template("personnel.html", form=form, personnel=[personnel_dto.PersonnelDTO(old_personnel)])    
  
  return flask.redirect(flask.url_for("u_get_all_active_personnel"))
  