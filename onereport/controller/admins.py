from onereport.controller import forms
from onereport.bl import admins_service
from onereport.data import misc
from onereport.controller.util import not_permitted
from flask import (
    abort,
    url_for,
    redirect,
    flash,
    render_template,
    request,
    Blueprint,
    current_app,
)
from flask_login import current_user, login_required
from onereport.exceptions import BadRequestError, InternalServerError, NotFoundError

admins = Blueprint("admins", __name__)


@admins.route("/onereport/admins/personnel/register", methods=["GET", "POST"])
@login_required
def register_personnel() -> str:
    if not_permitted(current_user.role, misc.Role.ADMIN):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        abort(401)

    return redirect(url_for("managers.register_personnel"))


@admins.route("/onereport/admins/users/<id>/register", methods=["GET", "POST"])
@login_required
def register_user(id: str) -> str:
    if not_permitted(current_user.role, misc.Role.ADMIN):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        abort(401)

    return redirect(url_for("managers.register_user", id=id))


@admins.route("/onereport/admins/personnel/<id>/update", methods=["GET", "POST"])
@login_required
def update_personnel(id: str) -> str:
    if not_permitted(current_user.role, misc.Role.ADMIN):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        abort(401)

    return redirect(url_for("managers.update_personnel", id=id))


@admins.route("/onereport/admins/users/<email>/update", methods=["GET", "POST"])
@login_required
def update_user(email: str) -> str:
    if not_permitted(current_user.role, misc.Role.ADMIN):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        abort(401)

    return redirect(url_for("managers.update_user", email=email))


# TODO:
# pagination
@admins.route("/onereport/admins/users", methods=["GET", "POST"])
@login_required
def get_all_users() -> str:
    if not_permitted(current_user.role, misc.Role.ADMIN):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        abort(401)

    order_by = request.args.get("order_by", default="COMPANY")
    order = request.args.get("order", "ASC")

    try:
        users = admins_service.get_all_users(order_by, order)
        return render_template("users/users.html", users=users)
    except BadRequestError as be:
        flash(str(be), category="danger")
    except NotFoundError as ne:
        flash(str(ne), category="info")

    return redirect(url_for("common.home"))


@admins.route("/onereport/admins/personnel", methods=["GET", "POST"])
@login_required
def get_all_personnel() -> str:
    if not_permitted(current_user.role, misc.Role.ADMIN):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        abort(401)

    order_by = request.args.get("order_by", default="LAST_NAME")
    order = request.args.get("order", default="ASC")

    form = forms.PersonnelListForm()
    try:
        personnel = admins_service.get_all_personnel(
            form, current_user.company, order_by, order
        )
        if request.method == "GET":
            form.company.data = current_user.company

        return render_template(
            "personnel/personnel_list.html",
            form=form,
            personnel=personnel,
        )
    except BadRequestError as be:
        flash(str(be), category="danger")
    except NotFoundError as ne:
        flash(str(ne), category="info")

    return redirect(url_for("common.home"))


@admins.route("/onereport/admins/report", methods=["GET", "POST"])
@login_required
def create_report() -> str:
    if not_permitted(current_user.role, misc.Role.ADMIN):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        abort(401)
    return redirect(url_for("managers.create_report"))


@admins.get("/onereport/admins/reports")
@login_required
def get_all_reports() -> str:
    if not_permitted(current_user.role, misc.Role.ADMIN):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        abort(401)

    company = request.args.get("company", default=current_user.company)
    order = request.args.get("order", default="DESC")
    page = request.args.get("page", "1")
    per_page = request.args.get("per_page", "20")

    return redirect(
        url_for(
            "managers.get_all_reports",
            company=company,
            order=order,
            page=page,
            per_page=per_page,
        )
    )


@admins.get("/onereport/admins/report/<int:id>")
@login_required
def get_report(id: int) -> str:
    if not_permitted(current_user.role, misc.Role.ADMIN):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        abort(401)

    company = request.args.get("company", current_user.company)

    return redirect(
        url_for(
            "managers.get_report",
            id=id,
            company=company,
        )
    )


@admins.route("/onereport/admins/personnel/upload", methods=["GET", "POST"])
@login_required
def upload_personnel() -> str:
    if not_permitted(current_user.role, misc.Role.ADMIN):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        abort(401)

    form = forms.UploadPersonnelForm()
    try:
        admins_service.upload_personnel(form)

        return render_template("personnel/upload_personnel.html", form=form)
    except BadRequestError as be:
        flash(f"{be}", category="danger")
    except InternalServerError as ie:
        flash(f"{ie}", category="danger")

    return redirect(url_for("common.home"))


@admins.get("/onereport/admins/report/delete")
@login_required
def delete_all_reports() -> str:
    if not_permitted(current_user.role, misc.Role.ADMIN):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        abort(401)

    if admins_service.delete_all_reports():
        flash("כל הדוחות נמחקו בהצלחה", category="success")
    else:
        flash("שגיאת שרת", category="danger")
    return redirect(url_for("common.home"))


@admins.get("/onereport/admins/personnel/delete")
@login_required
def delete_all_personnel() -> str:
    if not_permitted(current_user.role, misc.Role.ADMIN):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        abort(401)

    if admins_service.delete_all_personnel():
        flash("כל הדוחות נמחקו בהצלחה", category="success")
    else:
        flash("שגיאת שרת", category="danger")
    return redirect(url_for("common.home"))
