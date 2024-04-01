from onereport import app, forms, generate_urlstr
from onereport.data import model, misc
from onereport.dal import personnel_dal, report_dal, order_attr
from onereport.dto import personnel_dto, report_dto
from flask import url_for, redirect, flash, render_template, request
from flask_login import current_user, login_required
import datetime


def not_permitted() -> bool:
    if not misc.Role.is_valid(current_user.role):
        return False
    return misc.Role.get_level(current_user.role) > misc.Role.get_level(
        misc.Role.USER.name
    )


@app.route("/onereport/users/personnel", methods=["GET", "POST"])
@login_required
def u_get_all_personnel() -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect(url_for("home"))

    order_by = request.args.get("order_by", default="ID")
    order = request.args.get("order", default="ASC")

    app.logger.debug(
        f"query all personnel for {current_user}\nquery params: order by: {order_by}, order: {order}"
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

    company = misc.Company[current_user.company]
    personnel = personnel_dal.find_all_active_personnel_by_company(
        company, order_by, order
    )

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


@app.route("/onereport/users/personnel/<id>/update", methods=["GET", "POST"])
@login_required
def u_update_personnel(id: str) -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect(url_for("home"))

    old_personnel = personnel_dal.find_personnel_by_id(id)
    if old_personnel is None:
        app.logger.error(
            f"{current_user} tried to update a non exisiting personnel with id {id}"
        )
        flash(f"החייל {id} אינו במסד הנתונים", category="danger")

        return redirect(url_for("u_get_all_active_personnel"))

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

        # to ensure users cannot update Personnel::company
        personnel.company = old_personnel.company

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
        form.company.data = old_personnel.company
        form.active.data = old_personnel.active

        app.logger.debug(f"passing {personnel} personnel.html for {current_user}")
        return render_template(
            "personnel/personnel.html",
            form=form,
            personnel=[personnel_dto.PersonnelDTO(old_personnel)],
        )

    return redirect(url_for(generate_urlstr(current_user.role, "get_all_personnel")))


@app.route("/onereport/users/report", methods=["GET", "POST"])
@login_required
def u_create_report() -> str:
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
    return render_template(
        "reports/editable_report.html",
        form=form,
        personnel_presence_list=personnel_presence_list,
    )


@app.get("/onereport/users/reports")
@login_required
def u_get_all_reports() -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect(url_for("home"))

    order = request.args.get("order", default="DESC")

    if not order_attr.Order.is_valid(order):
        app.logger.warning(f"received incorrect query param order: {order}")
        flash(f"אין אפשרות לסדר את העצמים בסדר {order}", category="info")

        return redirect(url_for("home"))

    if not misc.Company.is_valid(current_user.company):
        app.logger.warning(f"{current_user} 's company is invalid")
        flash(f"{current_user.company} אינה פלוגה בגדוד", category="info")
        return redirect(url_for("home"))

    company = misc.Company[current_user.company]

    reports = report_dal.find_all_reports_by_company(company, order_attr.Order[order])
    if not reports:
        app.logger.debug(f"no visible reports for {current_user}")

    app.logger.debug(
        f"passing {len(reports)} reports to reports.html for {current_user}"
    )
    return render_template("reports/reports.html", reports=reports)


@app.get("/onereport/users/report/<int:id>")
@login_required
def u_get_report(id: int) -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect(url_for("home"))

    if not misc.Company.is_valid(current_user.company):
        app.logger.warning(f"{current_user} 's company is invalid")
        flash(f"{current_user.company} אינה פלוגה בגדוד", category="info")

        return redirect(url_for("home"))

    report = report_dal.find_report_by_id_and_company(
        id, misc.Company[current_user.company]
    )
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
