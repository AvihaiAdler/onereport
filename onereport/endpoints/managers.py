from onereport import app, forms, generate_urlstr
from onereport.data import model, misc
from onereport.dto import report_dto, user_dto, personnel_dto
from onereport.dal import personnel_dal, user_dal, report_dal, order_attr
from flask import url_for, redirect, flash, render_template, request
from flask_login import current_user, login_required
import datetime


def not_permitted() -> bool:
    if not misc.Role.is_valid(current_user.role):
        return False
    return misc.Role.get_level(current_user.role) > misc.Role.get_level(
        misc.Role.MANAGER.name
    )


def demote_user(user: model.User, form: forms.UserUpdateForm, /) -> None:
    if current_user.id == user.id:
        app.logger.warning(f"{current_user} tried to demote themselves")
        flash("אינך רשאי.ת לבצע פעולה זו")

        return

    personnel = model.Personnel(
        user.id,
        form.first_name.data.strip(),
        form.last_name.data.strip(),
        form.company.data,
        form.platoon.data,
    )

    user_dal.delete(user)  # delete user since it has the same id
    app.logger.info(f"{current_user} successfully deleted {user}")

    personnel_dal.save(personnel)
    app.logger.info(
        f"{current_user} successfuly demoted {user} to a personnel {personnel}"
    )


@app.route("/onereport/managers/personnel/register", methods=["GET", "POST"])
@login_required
def m_register_personnel() -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect(url_for("home"))

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
        match old_personnel:
            case None:
                personnel_dal.save(personnel)
                app.logger.debug(f"{current_user} successfully registered {personnel}")
                flash(
                    f"החייל.ת {form.first_name.data} {form.last_name.data} נוסף.ה בהצלחה",
                    category="success",
                )
            case op if not op.active:
                op.update(personnel)
                if personnel_dal.update(op):
                    app.logger.info(f"{current_user} successfully updated {op}")
                    flash(f"החייל.ת {id} עודכן בהצלחה", category="success")
                else:
                    app.logger.error(f"{current_user} failed to update {op}")
                    flash(f"הפעולה עבור החייל.ת {id} לא הושלמה", category="danger")
            case _:
                app.logger.error(
                    f"{current_user} tried to register {personnel} with the same id as {old_personnel}"
                )
                flash(
                    f"חייל.ת עם מס' אישי {old_personnel.id} כבר נמצא במערכת",
                    category="danger",
                )
        return redirect(url_for("home"))

    return render_template("personnel/personnel_registration.html", form=form)


@app.route("/onereport/managers/users/<id>/register", methods=["GET", "POST"])
@login_required
def m_register_user(id: str) -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect(url_for("home"))

    personnel = personnel_dal.find_personnel_by_id(id)
    if personnel is None:
        app.logger.error(
            f"{current_user} tried to register a non exiting user with id {id}"
        )
        flash(f"המס' האישי {id} אינו במסד הנתונים", category="danger")

        return redirect("home")

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

        current_user_level = misc.Role.get_level(current_user.role)
        if current_user_level > misc.Role.get_level(form.role.data):
            app.logger.error(
                f"{current_user} with permision level {current_user_level} tried to register a user with permission level {misc.Role.get_level(form.role.data)}"
            )
            flash("אינך ראשי.ת לבצע פעולה זו", category="danger")

            return redirect("home")

        old_user = user_dal.find_user_by_email(user.email)
        match old_user:
            case None:
                personnel_dal.delete(
                    personnel
                )  # delete personnel since it has the same id
                app.logger.info(f"{current_user} successfully deleted {personnel}")

                user_dal.save(user)
                app.logger.info(f"{current_user} successfully registered {user}")
                flash(
                    f"המשתמש.ת {' '.join((user.first_name, user.last_name))} נוסף.ה בהצלחה",
                    category="success",
                )
            case ou if not ou.active:
                old_user.update(user)
                if user_dal.update(old_user):
                    app.logger.info(f"{current_user} successfully updated {old_user}")
                    flash(
                        f"המשתמש.ת {' '.join((user.first_name, user.last_name))} עודכן.ה בהצלחה",
                        category="success",
                    )
                else:
                    app.logger.error(f"{current_user} failed to update {old_user}")
                    flash(
                        f"הפעולה עבור {' '.join((user.first_name, user.last_name))} לא הושלמה",
                        category="success",
                    )
            case _:
                app.logger.error(
                    f"{current_user} tried to register {user} with the same email as {old_user}"
                )
                flash("משתמש.ת עם כתובת מייל זו כבר רשום.ה במערכת", category="danger")
        return redirect(url_for("home"))

    if request.method == "GET":
        form.id.data = personnel.id
        form.first_name.data, form.last_name.data = (
            personnel.first_name,
            personnel.last_name,
        )
        form.company.data = personnel.company
        form.platoon.data = personnel.platoon

        return render_template("users/user_registration.html", form=form)

    return redirect(url_for(generate_urlstr(current_user.role, "register_user"), id=id))


@app.route("/onereport/managers/personnel/<id>/update", methods=["GET", "POST"])
@login_required
def m_update_personnel(id: str) -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect(url_for("home"))

    old_personnel = personnel_dal.find_personnel_by_id(id)
    if old_personnel is None:
        app.logger.error(
            f"{current_user} tried to update non existing personnel with id {id}"
        )
        flash(f"החייל {id} אינו במסד הנתונים", category="danger")

        return redirect(
            url_for(generate_urlstr(current_user.role, "get_all_personnel"))
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

        if (
            personnel.id == current_user.id
            and misc.Active[form.active.data] != current_user.active
        ):
            app.logger.warning(f"{current_user} tried to deactivate themselves")
            flash("אינך רשאי.ת לבצע פעולה זו", category="danger")

            return redirect(
                url_for(generate_urlstr(current_user.role, "get_all_personnel"))
            )

        personnel.active = misc.Active[form.active.data] == misc.Active.ACTIVE

        old_personnel.update(personnel)
        if personnel_dal.update(personnel):
            app.logger.info(f"{current_user} successfully updated {old_personnel}")
            flash(f"החייל.ת {id} עודכן בהצלחה", category="success")
        else:
            app.logger.error(f"{current_user} failed to update {old_personnel}")
            flash(f"הפעולה עבור החייל.ת {id} לא הושלמה", category="danger")

        return redirect(
            url_for(generate_urlstr(current_user.role, "get_all_personnel"))
        )

    if request.method == "GET":
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

        return render_template("personnel/personnel.html", form=form)

    return redirect(url_for(generate_urlstr(current_user.role, "get_all_personnel")))


@app.route("/onereport/managers/users/<email>/update", methods=["GET", "POST"])
@login_required
def m_update_user(email: str) -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect(url_for("home"))

    old_user = user_dal.find_user_by_email(email)
    if old_user is None:
        app.logger.error(
            f"{current_user} tried to update non exisiting user with id {id}"
        )
        flash("המשתמש אינו במסד הנתונים", category="info")

        return redirect(url_for("home"))

    form = forms.UserUpdateForm()
    if form.validate_on_submit():
        # handle demoting user request
        if form.delete.data:
            demote_user(old_user, form)
            return redirect(
                url_for(generate_urlstr(current_user.role, "get_all_users"))
            )

        # handle update user request
        user = model.User(
            old_user.id,
            form.email.data,
            form.first_name.data.strip(),
            form.last_name.data.strip(),
            form.role.data,
            form.company.data,
            form.platoon.data,
        )
        if (
            user.id == current_user.id
            and misc.Active[form.active.data] != current_user.active
        ):
            app.logger.warning(f"{current_user} tried to deactivate themselves")
            flash("אינך רשאי.ת לבצע פעולה זו", category="danger")

            return redirect(
                url_for(generate_urlstr(current_user.role, "get_all_users"))
            )

        user.active = misc.Active[form.active.data] == misc.Active.ACTIVE

        current_user_level = misc.Role.get_level(current_user.role)
        if current_user_level > misc.Role.get_level(form.role.data):
            app.logger.error(
                f"{current_user} with permision level {current_user_level} tried to register a user with permission level {misc.Role.get_level(form.role.data)}"
            )
            flash("אינך ראשי.ת לבצע פעולה זו", category="danger")
            return redirect("home")

        old_user.update(user)
        if user_dal.update(old_user):
            app.logger.info(f"{current_user} successfully updated {old_user}")
            flash(f"המשתמש.ת {old_user.email} עודכן בהצלחה", category="success")
        else:
            app.logger.error(f"{current_user} failed to update {old_user}")
            flash(
                f"הפעולה עבור המשתמש.ת {old_user.email} לא הושלמה", category="success"
            )

        return redirect(url_for(generate_urlstr(current_user.role, "get_all_users")))

    if request.method == "GET":
        form.id.data = old_user.id
        form.email.data = old_user.email
        form.first_name.data, form.last_name.data = (
            old_user.first_name,
            old_user.last_name,
        )
        form.role.data = old_user.role
        form.company.data, form.platoon.data = old_user.company, old_user.platoon
        form.active.data = old_user.active

        return render_template("users/user.html", form=form)

    return redirect(url_for(generate_urlstr(current_user.role, "get_all_users")))


# TODO:
# pagination
@app.route("/onereport/managers/users", methods=["GET", "POST"])
@login_required
def m_get_all_users() -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect(url_for("home"))

    order_by = request.args.get("order_by", default="COMPANY")
    order = request.args.get("order", "ASC")
    app.logger.debug(
        f"query all active non-admin users for {current_user}\nquery params: order by: {order_by}, order: {order}"
    )

    if not order_attr.UserOrderBy.is_valid(order_by):
        app.logger.warning(f"received incorrect query param order by: {order_by}")
        flash(f"אין אפשרות לסדר את העצמים לפי {order_by}", category="info")

        return render_template("users/users.html", users=[])

    if not order_attr.Order.is_valid(order):
        app.logger.warning(f"received incorrect query param order: {order}")
        flash(f"אין אפשרות לסדר את העצמים בסדר {order}", category="info")

        return render_template("users.html", users=[])

    users = user_dal.find_all_active_users(
        order_attr.UserOrderBy[order_by], order_attr.Order(order)
    )

    if not users:
        app.logger.debug(f"there are no visible users for {current_user}")

    app.logger.debug(f"passing {len(users)} personnel to users.html for {current_user}")
    return render_template(
        "users/users.html", users=[user_dto.UserDTO(user) for user in users]
    )


# TODO:
# pagination
@app.route("/onereport/managers/personnel", methods=["GET", "POST"])
@login_required
def m_get_all_personnel() -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect(url_for("home"))

    order_by = request.args.get("order_by", default="LAST_NAME")
    order = request.args.get("order", "ASC")
    app.logger.debug(
        f"query all active personnel for {current_user}\nquery params: order by: {order_by}, order: {order}"
    )

    form = forms.PersonnelListForm()
    if not order_attr.PersonnelOrderBy.is_valid(order_by):
        app.logger.warning(f"received incorrect query param order by: {order_by}")
        flash(f"אין אפשרות לסדר את העצמים לפי {order_by}", category="info")

        return render_template("personnel/personnel_list.html", form=form, personnel=[])

    if not order_attr.Order.is_valid(order):
        app.logger.warning(f"received incorrect query param order: {order}")
        flash(f"אין אפשרות לסדר את העצמים בסדר {order}", category="info")

        return render_template("personnel/personnel_list.html", form=form, personnel=[])

    if form.validate_on_submit():
        order_by = order_attr.PersonnelOrderBy[form.order_by.data]
        order = order_attr.Order[form.order.data]
    elif request.method == "GET":
        order_by = order_attr.PersonnelOrderBy[order_by]
        order = order_attr.Order[order]

    personnel = personnel_dal.find_all_active_personnel(order_by, order)
    if not personnel:
        app.logger.debug(f"there are no visible personnel for {current_user}")

    app.logger.debug(
        f"passing {len(personnel)} personnel to personnel_list.html for {current_user}"
    )
    return render_template(
        "personnel/personnel_list.html",
        form=form,
        personnel=[personnel_dto.PersonnelDTO(p) for p in personnel],
    )


@app.route("/onereport/managers/report", methods=["GET", "POST"])
@login_required
def m_create_report() -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect(url_for("home"))

    if not misc.Company.is_valid(current_user.company):
        app.logger.warning(f"{current_user} 's company is invalid")
        return redirect(url_for("home"))

    company = misc.Company[current_user.company]
    report = report_dal.find_report_by_date_and_company(datetime.date.today(), company)

    # no report for the current date has been opened
    if report is None:
        report = model.Report(company.name)
        report_dal.save(report)

        app.logger.info(f"{current_user} successfully created {report}")

    personnel = personnel_dal.find_all_active_personnel_by_company(
        company, order_attr.PersonnelOrderBy.LAST_NAME, order_attr.Order.ASC
    )

    if not personnel:
        app.logger.debug(f"no visibale users for {current_user}")

    form = forms.UpdateReportForm()

    # there is a report opened for the day
    if form.validate_on_submit():
        report.presence = {p for p in personnel if p.id in request.form}
        if report_dal.update(report):
            app.logger.info(f"{current_user} successfully updated the report {report}")
            flash(f"הדוח ליום {datetime.date.today()} נשלח בהצלחה", category="success")
        else:
            app.logger.error(f"{current_user} failed to update the report {report}")
            flash(f"הדוח ליום {datetime.date.today()} לא נשלח", category="danger")

        return redirect(url_for(generate_urlstr(current_user.role, "create_report")))

    # list specifically to preserve the order
    personnel_presence_list = [
        (personnel_dto.PersonnelDTO(p), p in report.presence) for p in personnel
    ]

    app.logger.debug(
        f"passing {len(personnel_presence_list)} personnel to editable_report.html for {current_user}"
    )
    return render_template(
        "reports/editable_report.html",
        form=form,
        personnel_presence_list=personnel_presence_list,
    )


@app.get("/onereport/managers/reports")
@login_required
def m_get_all_reports() -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect(url_for("home"))

    company = request.args.get("company", default="")
    order = request.args.get("order", "DESC")
    app.logger.debug(
        f"query all reports for {current_user}\nquery params: company: {company}, order: {order}"
    )

    if not order_attr.Order.is_valid(order):
        app.logger.warning(f"received incorrect query param order: {order}")
        flash(f"אין אפשרות לסדר את העצמים בסדר {order}", category="info")

        return redirect(url_for("home"))

    if not misc.Company.is_valid(current_user.company):
        app.logger.warning(f"{current_user} 's company is invalid")
        flash(f"{current_user.company} אינה פלוגה בגדוד", category="info")

        return redirect(url_for("home"))

    company = (
        misc.Company[company]
        if misc.Company.is_valid(company)
        else misc.Company[current_user.company]
    )

    reports = report_dal.find_all_reports_by_company(company, order_attr.Order[order])
    if not reports:
        app.logger.debug(f"no visible reports for {current_user}")

    app.logger.debug(
        f"passing {len(reports)} reports to reports.html for {current_user}"
    )
    return render_template(
        "reports/reports.html",
        reports=reports,
        company=misc.Company,
        current_company=company.value,
    )


@app.get("/onereport/managers/report/<int:id>")
@login_required
def m_get_report(id: int) -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect(url_for("home"))

    company = request.args.get("company", None)

    if not misc.Company.is_valid(current_user.company):
        app.logger.warning(f"{current_user} 's company is invalid")
        flash(f"{current_user.company} אינה פלוגה בגדוד", category="info")

        return redirect(url_for("home"))

    company = company if misc.Company.is_valid(company) else current_user.company
    report = report_dal.find_report_by_id_and_company(id, misc.Company[company])

    if report is None:
        app.logger.error(
            f"{current_user} tried to get a non existing report with id {id} for company {current_user.company}"
        )
        flash(f"הדוח {id} אינו במסד הנתונים", category="danger")

        return redirect(url_for(generate_urlstr(current_user.role, "get_all_reports")))

    app.logger.debug(f"sends {report} to old_report.html for {current_user}")
    return render_template(
        "reports/old_report.html", report=report_dto.ReportDTO(report)
    )
