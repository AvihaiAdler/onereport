from onereport import app
from onereport.data import misc
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

@app.get("/onereport/users/personnel")
@flask_login.login_required
def u_get_all_active_personnel(order_by: str = "ID", order: str = "ASC") -> str:
  if not order_attr.PersonnelOrderBy.is_valid_order(order_by):
    flask.flash(f"אין אפשרות לסדר את העצמים לפי {order_by}", category="info")
    return flask.render_template("personnel.html", personnel=[])

  if not order_attr.Order.is_valid_order(order):
    flask.flash(f"אין אפשרות לסדר את העצמים בסדר {order}", category="info")
    return flask.render_template("personnel.html", personnel=[])
  
  company = misc.Company[flask_login.current_user.company]
  personnel = personnel_dal.get_all_active_personnel_by_company(company, order_attr.PersonnelOrderBy[order_by], order_attr.Order[order])
  
  return flask.render_template("personnel.html", personnel=[personnel_dto.PersonnelDTO(p) for p in personnel])