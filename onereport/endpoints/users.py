from onereport import app, forms
from onereport.data import model, misc
from onereport.dal import personnel_dal, report_dal, order_attr
from onereport.dto import personnel_dto, report_dto
import flask
import flask_login
import datetime


def not_user() -> bool:
    current_user_role = flask_login.current_user.role
    return (
        misc.Role.is_valid(current_user_role)
        and misc.Role[current_user_role] != misc.Role.USER
    )


@app.route("/onereport/users/personnel", methods=["GET", "POST"])
@flask_login.login_required
def u_get_all_personnel() -> str:
    order_by = flask.request.args.get("order_by", default="ID")
    order = flask.request.args.get("order", default="ASC")

    if not_user():
        return flask.redirect(flask.url_for("home"))

    form = forms.PersonnelListForm()
    if not order_attr.PersonnelOrderBy.is_valid(order_by):
        flask.flash(f"אין אפשרות לסדר את העצמים לפי {order_by}", category="info")
        return flask.render_template(
            "personnel/personnel_list.html", form=form, personnel=[]
        )

    if not order_attr.Order.is_valid(order):
        flask.flash(f"אין אפשרות לסדר את העצמים בסדר {order}", category="info")
        return flask.render_template(
            "personnel/personnel_list.html", form=form, personnel=[]
        )

    if form.validate_on_submit():
        order_by = order_attr.PersonnelOrderBy[form.order_by.data]
        order = order_attr.Order[form.order.data]
    elif flask.request.method == "GET":
        order_by = order_attr.PersonnelOrderBy[order_by]
        order = order_attr.Order[order]

    company = misc.Company[flask_login.current_user.company]
    personnel = personnel_dal.find_all_active_personnel_by_company(
        company, order_by, order
    )

    return flask.render_template(
        "personnel/personnel_list.html",
        form=form,
        personnel=[personnel_dto.PersonnelDTO(p) for p in personnel],
    )


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
        personnel = model.Personnel(
            old_personnel.id,
            form.first_name.data.strip(),
            form.last_name.data.strip(),
            form.company.data,
            form.platoon.data,
        )
        personnel.active = misc.Active[form.active.data] == misc.Active.ACTIVE
        personnel.company = (
            old_personnel.company
        )  # to ensure users cannot update Personnel::company

        old_personnel.update(personnel)
        if personnel_dal.update(personnel):
            flask.flash(f"החייל.ת {id} עודכן בהצלחה", category="success")
        else:
            flask.flash(f"הפעולה עבור החייל.ת {id} לא הושלמה", category="danger") 
        return flask.redirect(flask.url_for("u_get_all_active_personnel"))

    if flask.request.method == "GET":
        form.id.data = old_personnel.id
        form.first_name.data, form.last_name.data = (
            old_personnel.first_name,
            old_personnel.last_name,
        )
        form.company.data = old_personnel.company
        form.active.data = old_personnel.active

        return flask.render_template(
            "personnel/personnel.html",
            form=form,
            personnel=[personnel_dto.PersonnelDTO(old_personnel)],
        )

    return flask.redirect(flask.url_for("u_get_all_active_personnel"))


@app.route("/onereport/users/report", methods=["GET", "POST"])
@flask_login.login_required
def u_create_report() -> str:
    if not_user():
        return flask.redirect(flask.url_for("home"))

    if not misc.Company.is_valid(flask_login.current_user.company):
        return flask.redirect(flask.url_for("home"))

    company = misc.Company[flask_login.current_user.company]
    report = report_dal.find_report_by_date_and_company(datetime.date.today(), company)

    # no report for the current date has been opened
    if report is None:
        report = model.Report(company.name)
        report_dal.save(report)

    personnel = personnel_dal.find_all_active_personnel_by_company(
        company, order_attr.PersonnelOrderBy.LAST_NAME, order_attr.Order.ASC
    )
    form = forms.UpdateReportForm()

    # there is a report opened for the day
    if form.validate_on_submit():
        report.presence = {p for p in personnel if p.id in flask.request.form}
        if report_dal.update(report):
            flask.flash(f"הדוח ליום {datetime.date.today()} נשלח בהצלחה", category="success")
        else:
            flask.flash(f"הדוח ליום {datetime.date.today()} לא נשלח", category="danger")
        return flask.redirect(flask.url_for("u_create_report"))

    personnel_presence_list = [
        (personnel_dto.PersonnelDTO(p), p in report.presence) for p in personnel
    ]  # list specifically to preserve the order
    return flask.render_template(
        "reports/editable_report.html",
        form=form,
        personnel_presence_list=personnel_presence_list,
    )


@app.get("/onereport/users/reports")
@flask_login.login_required
def u_get_all_reports() -> str:
    order = flask.request.args.get("order", default="DESC")

    if not_user():
        return flask.redirect(flask.url_for("home"))

    if not order_attr.Order.is_valid(order):
        flask.flash(f"אין אפשרות לסדר את העצמים בסדר {order}", category="info")
        return flask.redirect(flask.url_for("home"))

    if not misc.Company.is_valid(flask_login.current_user.company):
        return flask.redirect(flask.url_for("home"))

    company = misc.Company[flask_login.current_user.company]
    
    reports = report_dal.find_all_reports_by_company(company, order_attr.Order[order])
    
    return flask.render_template("reports/reports.html", reports=reports)


@app.get("/onereport/users/report/<int:id>")
@flask_login.login_required
def u_get_report(id: int) -> str:
    if not_user():
        return flask.redirect(flask.url_for("home"))

    if not misc.Company.is_valid(flask_login.current_user.company):
        return flask.redirect(flask.url_for("home"))

    report = report_dal.find_report_by_id_and_company(
        id, misc.Company[flask_login.current_user.company]
    )
    if report is None:
        flask.flash(f"הדוח {id} אינו במסד הנתונים", category="danger")
        return flask.redirect(flask.url_for("u_get_all_reports"))

    return flask.render_template("reports/old_report.html", report=report_dto.ReportDTO(report))
