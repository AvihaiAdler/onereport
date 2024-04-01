from onereport import app, forms, generate_urlstr
from onereport.data import model, misc
from onereport.dto import report_dto, user_dto, personnel_dto
from onereport.dal import personnel_dal, user_dal, report_dal, order_attr
import flask
import flask_login
import datetime


def not_permitted() -> bool:
    if not misc.Role.is_valid(flask_login.current_user.role):
        return False
    return misc.Role.get_level(flask_login.current_user.role) > misc.Role.get_level(
        misc.Role.MANAGER.name
    )


@app.route("/onereport/managers/personnel/register", methods=["GET", "POST"])
@flask_login.login_required
def m_register_personnel() -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {flask_login.current_user}")
        return flask.redirect(flask.url_for("home"))

    form = forms.PersonnelRegistrationFrom()

    if form.validate_on_submit():
        personnel = model.Personnel(
            form.id.data.strip(),
            form.first_name.data.strip(),
            form.last_name.data.strip(),
            form.company.data,
            form.platoon.data,
        )

        old_personnel = personnel_dal.find_personnel_by_id(personnel.id)
        if old_personnel is None:
            personnel_dal.save(personnel)

            app.logger.debug(
                f"{flask_login.current_user} successfully registered {personnel}"
            )
            flask.flash(
                f"החייל.ת {form.first_name.data} {form.last_name.data} נוסף.ה בהצלחה",
                category="success",
            )
        elif old_personnel is not None and not old_personnel.active:
            old_personnel.update(personnel)
            if personnel_dal.update(old_personnel):
                app.logger.info(
                    f"{flask_login.current_user} successfully updated {old_personnel}"
                )
                flask.flash(f"החייל.ת {id} עודכן בהצלחה", category="success")
            else:
                app.logger.error(
                    f"{flask_login.current_user} failed to update {old_personnel}"
                )
                flask.flash(f"הפעולה עבור החייל.ת {id} לא הושלמה", category="danger")
        else:
            app.logger.error(
                f"{flask_login.current_user} tried to register {personnel} with the same id as {old_personnel}"
            )
            flask.flash(
                f"חייל.ת עם מס' אישי {old_personnel.id} כבר נמצא במערכת",
                category="danger",
            )

        return flask.redirect(flask.url_for("home"))

    return flask.render_template("personnel/personnel_registration.html", form=form)


@app.route("/onereport/managers/users/<id>/register", methods=["GET", "POST"])
@flask_login.login_required
def m_register_user(id: str) -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {flask_login.current_user}")
        return flask.redirect(flask.url_for("home"))

    personnel = personnel_dal.find_personnel_by_id(id)
    if personnel is None:
        app.logger.error(
            f"{flask_login.current_user} tried to register a non exiting user with id {id}"
        )
        flask.flash(f"המס' האישי {id} אינו במסד הנתונים", category="danger")
        
        return flask.redirect("home")

    form = forms.UserRegistrationFrom()
    if form.validate_on_submit():
        user = model.User(
            personnel.id,
            form.email.data.strip(),
            form.first_name.data.strip(),
            form.last_name.data.strip(),
            form.role.data,
            form.company.data,
            form.platoon.data,
        )

        current_user_level = misc.Role.get_level(flask_login.current_user.role)
        if current_user_level > misc.Role.get_level(form.role.data):
            app.logger.error(
                f"{flask_login.current_user} with permision level {current_user_level} tried to register a user with permission level {misc.Role.get_level(form.role.data)}"
            )
            flask.flash("אינך ראשי.ת לבצע פעולה זו", category="danger")
            
            return flask.redirect("home")

        old_user = user_dal.find_user_by_email(user.email)
        if old_user is None:
            personnel_dal.delete(personnel)  # delete personnel since it has the same id
            app.logger.info(
                f"{flask_login.current_user} successfully deleted {personnel}"
            )

            user_dal.save(user)
            app.logger.info(
                f"{flask_login.current_user} successfully registered {user}"
            )
            flask.flash(
                f"המשתמש.ת {' '.join((user.first_name, user.last_name))} נוסף.ה בהצלחה",
                category="success",
            )
        elif old_user is not None and not old_user.active:
            old_user.update(user)
            if user_dal.update(old_user):
                app.logger.info(
                    f"{flask_login.current_user} successfully updated {old_user}"
                )
                flask.flash(
                    f"המשתמש.ת {' '.join((user.first_name, user.last_name))} עודכן.ה בהצלחה",
                    category="success",
                )
            else:
                app.logger.error(
                    f"{flask_login.current_user} failed to update {old_user}"
                )
                flask.flash(
                    f"הפעולה עבור {' '.join((user.first_name, user.last_name))} לא הושלמה",
                    category="success",
                )
        else:
            app.logger.error(
                f"{flask_login.current_user} tried to register {user} with the same email as {old_user}"
            )
            flask.flash("משתמש.ת עם כתובת מייל זו כבר רשום.ה במערכת", category="danger")

        return flask.redirect(flask.url_for("home"))

    if flask.request.method == "GET":
        form.id.data = personnel.id
        form.first_name.data, form.last_name.data = (
            personnel.first_name,
            personnel.last_name,
        )
        form.company.data = personnel.company
        form.platoon.data = personnel.platoon

        return flask.render_template("users/user_registration.html", form=form)

    return flask.redirect(
        flask.url_for(
            generate_urlstr(flask_login.current_user.role, "register_user"), id=id
        )
    )


@app.route("/onereport/managers/personnel/<id>/update", methods=["GET", "POST"])
@flask_login.login_required
def m_update_personnel(id: str) -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {flask_login.current_user}")
        return flask.redirect(flask.url_for("home"))

    old_personnel = personnel_dal.find_personnel_by_id(id)
    if old_personnel is None:
        app.logger.error(
            f"{flask_login.current_user} tried to update non existing personnel with id {id}"
        )
        flask.flash(f"החייל {id} אינו במסד הנתונים", category="danger")

        return flask.redirect(
            flask.url_for(
                generate_urlstr(flask_login.current_user.role, "get_all_personnel")
            )
        )

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

        old_personnel.update(personnel)
        if personnel_dal.update(personnel):
            app.logger.info(
                f"{flask_login.current_user} successfully updated {old_personnel}"
            )
            flask.flash(f"החייל.ת {id} עודכן בהצלחה", category="success")
        else:
            app.logger.error(
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
        form.company.data, form.platoon.data = (
            old_personnel.company,
            old_personnel.platoon,
        )
        form.active.data = old_personnel.active

        return flask.render_template("personnel/personnel.html", form=form)

    return flask.redirect(
        flask.url_for(
            generate_urlstr(flask_login.current_user.role, "get_all_personnel")
        )
    )


@app.route("/onereport/managers/users/<email>/update", methods=["GET", "POST"])
@flask_login.login_required
def m_update_user(email: str) -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {flask_login.current_user}")
        return flask.redirect(flask.url_for("home"))

    old_user = user_dal.find_user_by_email(email)
    if old_user is None:
        app.logger.error(
            f"{flask_login.current_user} tried to update non exisiting user with id {id}"
        )
        flask.flash("המשתמש אינו במסד הנתונים", category="info")
        
        return flask.redirect(flask.url_for("home"))

    form = forms.UserUpdateForm()
    if form.validate_on_submit():
        if form.delete.data:
            personnel = model.Personnel(
                old_user.id,
                form.first_name.data.strip(),
                form.last_name.data.strip(),
                form.company.data,
                form.platoon.data,
            )

            user_dal.delete(old_user)  # delete user since it has the same id
            app.logger.info(
                f"{flask_login.current_user} successfully deleted {old_user}"
            )

            personnel_dal.save(personnel)
            app.logger.info(
                f"{flask_login.current_user} successfuly demoted {old_user} to a personnel {personnel}"
            )

            return flask.redirect(
                flask.url_for(
                    generate_urlstr(flask_login.current_user.role, "get_all_users")
                )
            )

        user = model.User(
            old_user.id,
            form.email.data,
            form.first_name.data.strip(),
            form.last_name.data.strip(),
            form.role.data,
            form.company.data,
            form.platoon.data,
        )
        user.active = misc.Active[form.active.data] == misc.Active.ACTIVE

        current_user_level = misc.Role.get_level(flask_login.current_user.role)
        if current_user_level > misc.Role.get_level(form.role.data):
            app.logger.error(
                f"{flask_login.current_user} with permision level {current_user_level} tried to register a user with permission level {misc.Role.get_level(form.role.data)}"
            )
            flask.flash("אינך ראשי.ת לבצע פעולה זו", category="danger")
            return flask.redirect("home")

        old_user.update(user)
        if user_dal.update(old_user):
            app.logger.info(
                f"{flask_login.current_user} successfully updated {old_user}"
            )
            flask.flash(f"המשתמש.ת {old_user.email} עודכן בהצלחה", category="success")
        else:
            app.logger.error(f"{flask_login.current_user} failed to update {old_user}")
            flask.flash(
                f"הפעולה עבור המשתמש.ת {old_user.email} לא הושלמה", category="success"
            )

        return flask.redirect(
            flask.url_for(
                generate_urlstr(flask_login.current_user.role, "get_all_users")
            )
        )

    if flask.request.method == "GET":
        form.id.data = old_user.id
        form.email.data = old_user.email
        form.first_name.data, form.last_name.data = (
            old_user.first_name,
            old_user.last_name,
        )
        form.role.data = old_user.role
        form.company.data, form.platoon.data = old_user.company, old_user.platoon
        form.active.data = old_user.active

        return flask.render_template("users/user.html", form=form)

    return flask.redirect(
        flask.url_for(generate_urlstr(flask_login.current_user.role, "get_all_users"))
    )


# TODO:
# pagination
@app.route("/onereport/managers/users", methods=["GET", "POST"])
@flask_login.login_required
def m_get_all_users() -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {flask_login.current_user}")
        return flask.redirect(flask.url_for("home"))

    order_by = flask.request.args.get("order_by", default="COMPANY")
    order = flask.request.args.get("order", "ASC")
    app.logger.debug(
        f"query all active non-admin users for {flask_login.current_user}\nquery params: order by: {order_by}, order: {order}"
    )

    if not order_attr.UserOrderBy.is_valid(order_by):
        app.logger.warning(f"received incorrect query param order by: {order_by}")
        flask.flash(f"אין אפשרות לסדר את העצמים לפי {order_by}", category="info")
        
        return flask.render_template("users/users.html", users=[])

    if not order_attr.Order.is_valid(order):
        app.logger.warning(f"received incorrect query param order: {order}")
        flask.flash(f"אין אפשרות לסדר את העצמים בסדר {order}", category="info")
        
        return flask.render_template("users.html", users=[])

    users = user_dal.find_all_active_users(
        order_attr.UserOrderBy[order_by], order_attr.Order(order)
    )

    if not users:
        app.logger.debug(f"there are no visible users for {flask_login.current_user}")

    app.logger.debug(
        f"passing {len(users)} personnel to users.html for {flask_login.current_user}"
    )
    return flask.render_template(
        "users/users.html", users=[user_dto.UserDTO(user) for user in users]
    )


# TODO:
# pagination
@app.route("/onereport/managers/personnel", methods=["GET", "POST"])
@flask_login.login_required
def m_get_all_personnel() -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {flask_login.current_user}")
        return flask.redirect(flask.url_for("home"))

    order_by = flask.request.args.get("order_by", default="LAST_NAME")
    order = flask.request.args.get("order", "ASC")
    app.logger.debug(
        f"query all active personnel for {flask_login.current_user}\nquery params: order by: {order_by}, order: {order}"
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

    personnel = personnel_dal.find_all_active_personnel(order_by, order)
    if not personnel:
        app.logger.debug(
            f"there are no visible personnel for {flask_login.current_user}"
        )

    app.logger.debug(
        f"passing {len(personnel)} personnel to personnel_list.html for {flask_login.current_user}"
    )
    return flask.render_template(
        "personnel/personnel_list.html",
        form=form,
        personnel=[personnel_dto.PersonnelDTO(p) for p in personnel],
    )


@app.route("/onereport/managers/report", methods=["GET", "POST"])
@flask_login.login_required
def m_create_report() -> str:
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
        app.logger.debug(f"no visibale users for {flask_login.current_user}")

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
            app.logger.error(
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

    app.logger.debug(
        f"passing {len(personnel_presence_list)} personnel to editable_report.html for {flask_login.current_user}"
    )
    return flask.render_template(
        "reports/editable_report.html",
        form=form,
        personnel_presence_list=personnel_presence_list,
    )


@app.get("/onereport/managers/reports")
@flask_login.login_required
def m_get_all_reports() -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {flask_login.current_user}")
        return flask.redirect(flask.url_for("home"))

    company = flask.request.args.get("company", default="")
    order = flask.request.args.get("order", "DESC")
    app.logger.debug(
        f"query all reports for {flask_login.current_user}\nquery params: company: {company}, order: {order}"
    )

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

    company = (
        misc.Company[company]
        if misc.Company.is_valid(company)
        else misc.Company[flask_login.current_user.company]
    )

    reports = report_dal.find_all_reports_by_company(company, order_attr.Order[order])
    if not reports:
        app.logger.debug(f"no visible reports for {flask_login.current_user}")

    app.logger.debug(
        f"passing {len(reports)} reports to reports.html for {flask_login.current_user}"
    )
    return flask.render_template(
        "reports/reports.html",
        reports=reports,
        company=misc.Company,
        current_company=company.value,
    )


@app.get("/onereport/managers/report/<int:id>")
@flask_login.login_required
def m_get_report(id: int) -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {flask_login.current_user}")
        return flask.redirect(flask.url_for("home"))

    company = flask.request.args.get("company", None)

    if not misc.Company.is_valid(flask_login.current_user.company):
        app.logger.warning(f"{flask_login.current_user} 's company is invalid")
        flask.flash(
            f"{flask_login.current_user.company} אינה פלוגה בגדוד", category="info"
        )

        return flask.redirect(flask.url_for("home"))

    company = (
        company if misc.Company.is_valid(company) else flask_login.current_user.company
    )
    report = report_dal.find_report_by_id_and_company(id, misc.Company[company])

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

    app.logger.debug(f"sends {report} to old_report.html for {flask_login.current_user}")
    return flask.render_template(
        "reports/old_report.html", report=report_dto.ReportDTO(report)
    )
