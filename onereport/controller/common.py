import flask_login
from flask import Blueprint, render_template, url_for, redirect, current_app


common = Blueprint("common", __name__)

@common.get("/")
@common.get("/onereport/login")
def login() -> str:
    return render_template("login.html")


@common.get("/onereport/logout")
@flask_login.login_required
def logout() -> str:
    flask_login.logout_user()
    current_app.logger.info(f"The user: {flask_login.current_user} logged out")
    return redirect(url_for("common.login"))


@common.get("/onereport/home")
@flask_login.login_required
def home() -> str:
    return render_template("home.html")


@common.get("/onereport/about")
@flask_login.login_required
def about() -> str:
    return render_template("about.html")