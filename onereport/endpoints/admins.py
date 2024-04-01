from onereport import app, forms, generate_urlstr
from onereport.data import misc
from onereport.dto import user_dto, personnel_dto
from onereport.dal import user_dal, personnel_dal, order_attr
from flask import url_for, redirect, flash, render_template, request
from flask_login import current_user, login_required


def not_permitted() -> bool:
    if not misc.Role.is_valid(current_user.role):
        return False
    return misc.Role.get_level(current_user.role) > misc.Role.get_level(
        misc.Role.ADMIN.name
    )


@app.route("/onereport/admins/personnel/register", methods=["GET", "POST"])
@login_required
def a_register_personnel() -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect("home")

    return redirect(
        url_for(generate_urlstr(misc.Role.MANAGER.name, "register_personnel"))
    )


@app.route("/onereport/admins/users/<id>/register", methods=["GET", "POST"])
@login_required
def a_register_user(id: str) -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect("home")

    return redirect(
        url_for(generate_urlstr(misc.Role.MANAGER.name, "register_user"), id=id)
    )


@app.route("/onereport/admins/personnel/<id>/update", methods=["GET", "POST"])
@login_required
def a_update_personnel(id: str) -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect("home")

    return redirect(
        url_for(generate_urlstr(misc.Role.MANAGER.name, "update_personnel"), id=id)
    )


@app.route("/onereport/admins/users/<email>/update", methods=["GET", "POST"])
@login_required
def a_update_user(email: str) -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect("home")

    return redirect(
        url_for(generate_urlstr(misc.Role.MANAGER.name, "update_user"), email=email)
    )


# TODO:
# pagination
@app.route("/onereport/admins/users", methods=["GET", "POST"])
@login_required
def a_get_all_users() -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect(url_for("home"))

    order_by = request.args.get("order_by", default="COMPANY")
    order = request.args.get("order", "ASC")
    app.logger.debug(
        f"query all users for {current_user}\nquery params: order by: {order_by}, order: {order}"
    )

    if not order_attr.UserOrderBy.is_valid(order_by):
        app.logger.warning(f"received incorrect query param order by: {order_by}")
        flash(f"אין אפשרות לסדר את העצמים לפי {order_by}", category="info")

        return render_template("users/users.html", users=[])

    if not order_attr.Order.is_valid(order):
        app.logger.warning(f"received incorrect query param order: {order}")
        flash(f"אין אפשרות לסדר את העצמים בסדר {order}", category="info")

        return render_template("users.html", users=[])

    users = user_dal.find_all_users(
        order_attr.UserOrderBy[order_by], order_attr.Order[order]
    )

    if not users:
        app.logger.warning("users table is empty")

    app.logger.debug(f"passing {len(users)} users to users.html for {current_user}")
    return render_template(
        "users/users.html", users=[user_dto.UserDTO(user) for user in users]
    )


@app.route("/onereport/admins/personnel", methods=["GET", "POST"])
@login_required
def a_get_all_personnel() -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect(url_for("home"))

    order_by = request.args.get("order_by", default="LAST_NAME")
    order = request.args.get("order", "ASC")
    app.logger.debug(
        f"query all users for {current_user}\nquery params: order by: {order_by}, order: {order}"
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

    personnel = personnel_dal.find_all_personnel(order_by, order)
    if not personnel:
        app.logger.warning("personnel table is empty")

    app.logger.debug(
        f"passing {len(personnel)} personnel to personnel_list.html for {current_user}"
    )
    return render_template(
        "personnel/personnel_list.html",
        form=form,
        personnel=[personnel_dto.PersonnelDTO(p) for p in personnel],
    )


@app.route("/onereport/admins/report", methods=["GET", "POST"])
@login_required
def a_create_report() -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect("home")

    return redirect(url_for(generate_urlstr(misc.Role.MANAGER.name, "create_report")))


@app.get("/onereport/admins/reports")
@login_required
def a_get_all_reports() -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect("home")

    company = request.args.get("company", default="")
    order = request.args.get("order", default="DESC")
    app.logger.debug(
        f"query all reports for {current_user}\nquery params: company: {company}, order: {order}"
    )

    return redirect(
        url_for(
            generate_urlstr(misc.Role.MANAGER.name, "get_all_reports"),
            company=company,
            order=order,
        )
    )


@app.get("/onereport/admins/report/<int:id>")
@login_required
def a_get_report(id: int) -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect("home")

    return redirect(
        url_for(generate_urlstr(misc.Role.MANAGER.name, "get_report"), id=id)
    )
