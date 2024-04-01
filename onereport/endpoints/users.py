from onereport import app, forms, generate_urlstr
from onereport.data import model, misc
from onereport.dal import personnel_dal, report_dal, order_attr
from onereport.dto import personnel_dto, report_dto
import flask
import flask_login
import datetime


def not_permitted() -> bool:
    if not misc.Role.is_valid(flask_login.current_user.role):
        return False
    return misc.Role.get_level(flask_login.current_user.role) > misc.Role.get_level(
        misc.Role.USER.name
    )


@app.route("/onereport/users/personnel", methods=["GET", "POST"])
@flask_login.login_required
def u_get_all_personnel() -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {flask_login.current_user}")
        return flask.redirect(flask.url_for("home"))

    order_by = flask.request.args.get("order_by", default="ID")
    order = flask.request.args.get("order", default="ASC")

    app.logger.info(
        f"query all personnel for {flask_login.current_user}\nquery params: order by: {order_by}, order: {order}"
    )

    form = forms.PersonnelListForm()
    if not order_attr.PersonnelOrderBy.is_valid(order_by):
        app.logger.warning(f"received incorrect query param order by: {order_by}")
        flask.flash(f"אין אפשרות לסדר את העצמים לפי {order_by}", category="info")

        return flask.render_template(
            "personnel/personnel_list.html", form=form, personnel=[]
        )

    if not order_attr.Order.is_valid(order):
        app.logger.warning(f"received incorrect query param order: {order}")
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

    if not personnel:
        app.logger.debug(
            f"there are no visible personnel for {flask_login.current_user}"
        )

    app.logger.info(
        f"passing {len(personnel)} personnel to personnel_list.html for {flask_login.current_user}"
    )

    return flask.render_template(
        "personnel/personnel_list.html",
        form=form,
        personnel=[personnel_dto.PersonnelDTO(p) for p in personnel],
    )


@app.route("/onereport/users/personnel/<id>/update", methods=["GET", "POST"])
@flask_login.login_required
def u_update_personnel(id: str) -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {flask_login.current_user}")
        return flask.redirect(flask.url_for("home"))

    old_personnel = personnel_dal.find_personnel_by_id(id)
    if old_personnel is None:
        app.logger.error(
            f"{flask_login.current_user} tried to update a non exisiting personnel with id {id}"
        )
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
            app.logger.info(
                f"{flask_login.current_user} successfully updated {old_personnel}"
            )
            flask.flash(f"החייל.ת {id} עודכן בהצלחה", category="success")
        else:
            app.logger.warning(
                f"{flask_login.current_user} failed to update {old_personnel}"
            )
            flask.flash(f"הפעולה עבור החייל.ת {id} לא הושלמה", category="danger")
        return flask.redirect(
            flask.url_for(
                generate_urlstr(flask_login.current_user.role, "get_all_personnel")
            )
        )

    if flask.request.method == "GET":
        form.id.data = old_personnel.id
        form.first_name.data, form.last_name.data = (
            old_personnel.first_name,
            old_personnel.last_name,
        )
        form.company.data = old_personnel.company
        form.active.data = old_personnel.active

        app.logger.info(
            f"passing {personnel} personnel.html for {flask_login.current_user}"
        )
        return flask.render_template(
            "personnel/personnel.html",
            form=form,
            personnel=[personnel_dto.PersonnelDTO(old_personnel)],
        )

    return flask.redirect(
        flask.url_for(
            generate_urlstr(flask_login.current_user.role, "get_all_personnel")
        )
    )


@app.route("/onereport/users/report", methods=["GET", "POST"])
@flask_login.login_required
def u_create_report() -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {flask_login.current_user}")
        return flask.redirect(flask.url_for("home"))

    if not misc.Company.is_valid(flask_login.current_user.company):
        app.logger.warning(f"{flask_login.current_user} 's company is invalid")
        return flask.redirect(flask.url_for("home"))

    company = misc.Company[flask_login.current_user.company]
    report = report_dal.find_report_by_date_and_company(datetime.date.today(), company)

    # no report for the current date has been opened
    if report is None:
        report = model.Report(company.name)
        report_dal.save(report)

        app.logger.info(f"{flask_login.current_user} successfully created {report}")

    personnel = personnel_dal.find_all_active_personnel_by_company(
        company, order_attr.PersonnelOrderBy.LAST_NAME, order_attr.Order.ASC
    )

    if not personnel:
        app.logger.warning(f"no visibale users for {flask_login.current_user}")

    form = forms.UpdateReportForm()

    # there is a report opened for the day
    if form.validate_on_submit():
        report.presence = {p for p in personnel if p.id in flask.request.form}
        if report_dal.update(report):
            app.logger.info(
                f"{flask_login.current_user} successfully updated the report {report}"
            )
            flask.flash(
                f"הדוח ליום {datetime.date.today()} נשלח בהצלחה", category="success"
            )
        else:
            app.logger.info(
                f"{flask_login.current_user} failed to update the report {report}"
            )
            flask.flash(f"הדוח ליום {datetime.date.today()} לא נשלח", category="danger")
        return flask.redirect(
            flask.url_for(
                generate_urlstr(flask_login.current_user.role, "create_report")
            )
        )

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
    if not_permitted():
        app.logger.warning(f"unauthorized access by {flask_login.current_user}")
        return flask.redirect(flask.url_for("home"))

    order = flask.request.args.get("order", default="DESC")

    if not order_attr.Order.is_valid(order):
        app.logger.warning(f"received incorrect query param order: {order}")
        flask.flash(f"אין אפשרות לסדר את העצמים בסדר {order}", category="info")

        return flask.redirect(flask.url_for("home"))

    if not misc.Company.is_valid(flask_login.current_user.company):
        app.logger.warning(f"{flask_login.current_user} 's company is invalid")
        flask.flash(
            f"{flask_login.current_user.company} אינה פלוגה בגדוד", category="info"
        )
        return flask.redirect(flask.url_for("home"))

    company = misc.Company[flask_login.current_user.company]

    reports = report_dal.find_all_reports_by_company(company, order_attr.Order[order])
    if not reports:
        app.logger.debug(f"no visible reports for {flask_login.current_user}")

    app.logger.info(
        f"passing {len(reports)} reports to reports.html for {flask_login.current_user}"
    )
    return flask.render_template("reports/reports.html", reports=reports)


@app.get("/onereport/users/report/<int:id>")
@flask_login.login_required
def u_get_report(id: int) -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {flask_login.current_user}")
        return flask.redirect(flask.url_for("home"))

    if not misc.Company.is_valid(flask_login.current_user.company):
        app.logger.warning(f"{flask_login.current_user} 's company is invalid")
        flask.flash(
            f"{flask_login.current_user.company} אינה פלוגה בגדוד", category="info"
        )

        return flask.redirect(flask.url_for("home"))

    report = report_dal.find_report_by_id_and_company(
        id, misc.Company[flask_login.current_user.company]
    )
    if report is None:
        app.logger.error(
            f"{flask_login.current_user} tried to get a non existing report with id {id} for company {flask_login.current_user.company}"
        )
        flask.flash(f"הדוח {id} אינו במסד הנתונים", category="danger")
        return flask.redirect(
            flask.url_for(
                generate_urlstr(flask_login.current_user.role, "get_all_reports")
            )
        )

    app.logger.info(f"sends {report} to old_report.html for {flask_login.current_user}")
    return flask.render_template(
        "reports/old_report.html", report=report_dto.ReportDTO(report)
    )
