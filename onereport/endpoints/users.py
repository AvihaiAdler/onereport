from onereport import app
from onereport.data import misc
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
    return flask.redirect(flask.url_for("login"))

@app.get("/onereport/home")
@flask_login.login_required
def home() -> str:
  title = misc.Company[flask_login.current_user.company].value
  return flask.render_template("home.html", title=title)

@app.get("/onereport/about")
@flask_login.login_required
def about() -> str:
  return "about"