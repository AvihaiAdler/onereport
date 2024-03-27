from onereport import app, forms, generate_urlstr
from onereport.data import model
from onereport.data import misc
from onereport.dto import user_dto, personnel_dto
from onereport.dal import personnel_dal, user_dal, report_dal
from onereport.dal import order_attr
import flask
import flask_login
import datetime

def not_manager() -> bool:
  return misc.Role[flask_login.current_user.role] != misc.Role.MANAGER

def is_user() -> bool:
  return misc.Role.is_valid(flask_login.current_user.role) and misc.Role[flask_login.current_user.role] == misc.Role.USER

@app.route("/onereport/managers/register_personnel", methods=["GET", "POST"])
@flask_login.login_required
def m_register_personnel() -> str:
  if is_user():
    return flask.redirect(flask.url_for("home"))
  
  form = forms.PersonnelRegistrationFrom()
  
  if form.validate_on_submit():
    personnel = model.Personnel(form.id.data.strip(), form.first_name.data.strip(), form.last_name.data.strip(), form.company.data, "1")
    
    old_personnel = personnel_dal.find_personnel_by_id(personnel.id)
    if old_personnel is not None:
      old_personnel.update(personnel)
      model.db.session.commit()
      flask.flash(f"החייל {' '.join((personnel.first_name, personnel.last_name))} עודכן בהצלחה", category="success")
    else:
      model.db.session.add(personnel)
      model.db.session.commit()
      flask.flash(f"החייל {form.first_name.data} {form.last_name.data} נוסף בהצלחה", category="success")
    
    return flask.redirect(flask.url_for("home"))
    
  return flask.render_template("personnel/personnel_registration.html", form=form)

@app.route("/onereport/managers/register_user", methods=["GET", "POST"])
@flask_login.login_required
def m_register_user() -> str:
  if is_user():
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
      flask.flash(f"הפקיד {' '.join((user.first_name, user.last_name))} עודכן בהצלחה", category="success")
    else:
      model.db.session.add(user)
      model.db.session.commit()
      flask.flash(f"הפקיד {' '.join((user.first_name, user.last_name))} נוסף בהצלחה", category="success")
    
    return flask.redirect(flask.url_for("home"))
  
  return flask.render_template("users/user_registration.html", form=form)

@app.route("/onereport/managers/personnel/<id>/update", methods=["GET", "POST"])
@flask_login.login_required
def m_update_personnel(id: str) -> str:
  if is_user():
    return flask.redirect(flask.url_for("home"))
  
  old_personnel = personnel_dal.find_personnel_by_id(id)
  if old_personnel is None:
    flask.flash(f"החייל {id} אינו במסד הנתונים", category="danger")
    return flask.redirect(flask.url_for(generate_urlstr(flask_login.current_user.role, "get_all_personnel")))
  
  form = forms.PersonnelUpdateForm()
  if form.validate_on_submit():
    personnel = model.Personnel(old_personnel.id, form.first_name.data.strip(), form.last_name.data.strip(), form.company.data, "1")
    if misc.Active.is_valid(form.active.data):
      personnel.active = misc.Active[form.active.data] == misc.Active.ACTIVE 
    
    old_personnel.update(personnel)
    
    model.db.session.commit()
    
    flask.flash(f"החייל {id} עודכן בהצלחה", category="success")
    return flask.redirect(flask.url_for(generate_urlstr(flask_login.current_user.role, "get_all_personnel")))
  
  if flask.request.method == "GET":
    form.id.data = old_personnel.id
    form.first_name.data, form.last_name.data = old_personnel.first_name, old_personnel.last_name
    form.company.data = old_personnel.company
    form.active.data = old_personnel.active
  
    return flask.render_template("personnel/personnel.html", form=form, personnel=[personnel_dto.PersonnelDTO(old_personnel)])  
  
  return flask.redirect(flask.url_for(generate_urlstr(flask_login.current_user.role, "get_all_personnel")))

# TODO:
# pagination
@app.route("/onereport/managers/users", methods=["GET", "POST"])
@flask_login.login_required
def m_get_all_users() -> str:
  order_by = flask.request.args.get("order_by", default="COMPANY")
  order = flask.request.args.get("order", "ASC")
  
  if not_manager():
    return flask.redirect(flask.url_for("home"))
  
  if not order_attr.UserOrderBy.is_valid(order_by):
    flask.flash(f"אין אפשרות לסדר את העצמים לפי {order_by}", category="info")
    return flask.render_template("users/users.html", users=[])

  if not order_attr.Order.is_valid(order):
    flask.flash(f"אין אפשרות לסדר את העצמים בסדר {order}", category="info")
    return flask.render_template("users.html", users=[])
  
  # SELECT * FROM users WHERE user.active AND user.role != ADMIN ORDER_BY order_by order
  users = user_dal.find_all_active_users(order_attr.UserOrderBy[order_by], order_attr.Order(order))
  return flask.render_template("users/users.html", users=[user_dto.UserDTO(user) for user in users])

# TODO:
# pagination
@app.route("/onereport/managers/personnel", methods=["GET", "POST"])
@flask_login.login_required
def m_get_all_personnel() -> str:
  order_by = flask.request.args.get("order_by", default="LAST_NAME")
  order = flask.request.args.get("order", "ASC")
  
  if not_manager():
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
  personnel = personnel_dal.find_all_active_personnel(order_by, order)
  return flask.render_template("personnel/personnel_list.html", form=form, personnel=[personnel_dto.PersonnelDTO(p) for p in personnel])

@app.route("/onereport/managers/report", methods=["GET", "POST"])
@flask_login.login_required
def m_create_report() -> str:
  if is_user():
    return flask.redirect(flask.url_for("home"))
  
  if not misc.Company.is_valid(flask_login.current_user.company):
    return flask.redirect(flask.url_for("home"))
  
  company = misc.Company[flask_login.current_user.company]
  report = report_dal.find_report_by_date_and_company(datetime.date.today(), company)
  
  # no report for the current date has been opened
  if report is None:
    report = model.Report(company.name)
    model.db.session.add(report)
    model.db.session.commit()
  
  personnel = personnel_dal.find_all_active_personnel_by_company(company, order_attr.PersonnelOrderBy.LAST_NAME, order_attr.Order.ASC)  
  form = forms.UpdateReportForm()
  
  # there is a report opened for the day
  if form.validate_on_submit(): 
    report.presence = {p for p in personnel if p.id in flask.request.form}
    model.db.session.commit()
    
    return flask.redirect(flask.url_for(generate_urlstr(flask_login.current_user.role, "create_report")))
    
  personnel_presence_list = [(personnel_dto.PersonnelDTO(p), p in report.presence) for p in personnel] # list specifically to preserve the order
  return flask.render_template("reports/editable_report.html", form=form, personnel_presence_list=personnel_presence_list)

@app.get("/onereport/managers/reports")
@flask_login.login_required
def m_get_all_reports() -> str:
  company = flask.request.args.get("company", default="")
  order = flask.request.args.get("order", "DESC")
  
  if is_user():
    return flask.redirect(flask.url_for("home"))
  
  if not order_attr.Order.is_valid(order):
    flask.flash(f"אין אפשרות לסדר את העצמים בסדר {order}", category="info")
    return flask.redirect(flask.url_for("home"))
  
  if not misc.Company.is_valid(flask_login.current_user.company):
    return flask.redirect(flask.url_for("home"))
  
  company = misc.Company[company] if misc.Company.is_valid(company) else misc.Company[flask_login.current_user.company]
  reports = report_dal.find_all_reports_by_company(company, order_attr.Order[order])
  
  return flask.render_template("reports/reports.html", reports=reports, company=misc.Company, current_company=company.value)

@app.get("/onereport/managers/report/<int:id>")
@flask_login.login_required
def m_get_report(id: int) -> str:
  if is_user():
    return flask.redirect(flask.url_for("home"))
  
  report = report_dal.find_report_by_id(id)
  if report is None:
    flask.flash(f"הדוח {id} אינו במסד הנתונים", category="danger")
    return flask.redirect(flask.url_for(generate_urlstr(flask_login.current_user.role, "get_all_reports")))

  return flask.render_template("reports/old_report.html", report=report)