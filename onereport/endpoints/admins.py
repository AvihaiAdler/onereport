from onereport import app, forms, generate_urlstr
from onereport.bl import admins_service
from onereport.data import misc
from flask import url_for, redirect, flash, render_template, request
from flask_login import current_user, login_required

from onereport.exceptions.exceptions import BadRequestError, NotFoundError


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

    try:
        users = admins_service.get_all_users(order_by, order)
        return render_template("users/users.html", users=users)
    except BadRequestError as be:
        flash(str(be), category="danger")
    except NotFoundError as ne:
        flash(str(ne), category="info")

    return redirect(url_for("home"))


@app.route("/onereport/admins/personnel", methods=["GET", "POST"])
@login_required
def a_get_all_personnel() -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect(url_for("home"))

    order_by = request.args.get("order_by", default="LAST_NAME")
    order = request.args.get("order", "ASC")

    form = forms.PersonnelListForm()
    try:
        personnel = admins_service.get_all_personnel(form, order_by, order)
        return render_template(
            "personnel/personnel_list.html",
            form=form,
            personnel=personnel,
        )
    except BadRequestError as be:
        flash(str(be), category="danger")
    except NotFoundError as ne:
        flash(str(ne), category="info")

    return redirect(url_for("home"))


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
