from onereport import app
import flask
import flask_login


@app.get("/")
@app.get("/onereport/login")
def login() -> str:
    return flask.render_template("login.html")


@app.get("/onereport/logout")
@flask_login.login_required
def logout() -> str:
    flask_login.logout_user()
    app.logger.info(f"The user: {flask_login.current_user} logged out")
    return flask.redirect(flask.url_for("login"))


@app.get("/onereport/home")
@flask_login.login_required
def home() -> str:
    return flask.render_template("home.html")


@app.get("/onereport/about")
@flask_login.login_required
def about() -> str:
    return flask.render_template("about.html")