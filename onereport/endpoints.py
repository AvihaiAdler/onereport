import flask
from .data.misc import Space
from . import forms, app
from .data import model
import flask_login
import secrets
import requests
from urllib.parse import urlencode 

@app.get("/hello")
def hello() -> str:
  return flask.render_template("home.html", title=Space.A.value)

@app.get("/about")
def about() -> str:
  return "about"

@app.get("/")
@app.get("/onereport/login") 
def login() -> str:
  return flask.render_template("login.html")

@app.get("/onereport/logout")
def logout() -> str:
    flask_login.logout_user()
    return flask.redirect(flask.url_for("login"))

@app.route("/onereport/authorize/<provider>")
def oauth2_authorize(provider: str):
    if not flask_login.current_user.is_anonymous:
        return flask.redirect(flask.url_for("hello"))

    provider_data = flask.current_app.config["OAUTH2_PROVIDERS"].get(provider)
    if provider_data is None:
        flask.abort(404)

    # generate a random string for the state parameter
    flask.session["oauth2_state"] = secrets.token_urlsafe(16)

    # create a query string with all the OAuth2 parameters
    query = urlencode({
        "client_id": provider_data["client_id"],
        "redirect_uri": flask.url_for("oauth2_callback", provider=provider, _external=True),
        "response_type": "code",
        "scope": " ".join(provider_data["scopes"]),
        "state": flask.session["oauth2_state"],
    })

    # redirect the user to the OAuth2 provider authorization URL
    return flask.redirect(provider_data["authorize_url"] + "?" + query)
  
@app.route("/onereport/callback/<provider>")
def oauth2_callback(provider: str):
    if not flask_login.current_user.is_anonymous:
        return flask.redirect(flask.url_for("hello"))

    provider_data = flask.current_app.config["OAUTH2_PROVIDERS"].get(provider)
    if provider_data is None:
        flask.abort(404)

    # if there was an authentication error, flash the error messages and exit
    if "error" in flask.request.args:
        for key, value in flask.request.args.items():
            if key.startswith("error"):
                flask.flash(f"{key}: {value}")
        return flask.redirect(flask.url_for("login"))

    # make sure that the state parameter matches the one we created in the
    # authorization request
    if flask.request.args["state"] != flask.session.get("oauth2_state"):
        flask.abort(401)

    # make sure that the authorization code is present
    if "code" not in flask.request.args:
        flask.abort(401)

    # exchange the authorization code for an access token
    body = {
        "client_id": provider_data["client_id"],
        "client_secret": provider_data["client_secret"],
        "code": flask.request.args["code"],
        "grant_type": "authorization_code",
        "redirect_uri": flask.url_for("oauth2_callback", provider=provider, _external=True),
    }
    response = requests.post(provider_data["token_url"], data=body, headers={"Accept": "application/json"})
    
    if response.status_code != 200:
        flask.abort(401)
        
    oauth2_token = response.json().get("access_token")
    if not oauth2_token:
        flask.abort(401)

    # use the access token to get the user"s email address
    response = requests.get(provider_data["userinfo"]["url"], headers={
        "Authorization": "Bearer " + oauth2_token,
        "Accept": "application/json",
    })
    if response.status_code != 200:
        flask.abort(401)
        
    email = provider_data["userinfo"]["email"](response.json())

    # find or create the user in the database
    # user = model.db.session.scalar(model.db.select(model.User).where(model.User.email == email))
    user = model.db.session.query(model.User).filter(model.User.email==email).scalar()
    print(user)
    if user is None:
        flask.abort(401)

    # log the user in
    flask_login.login_user(user)
    return flask.redirect(flask.url_for("hello"))

@app.route("/onereport/managers/register_personnel", methods=["GET", "POST"])
def register_personnel() -> str:
  form = forms.PersonnelRegistrationFrom()
  
  if form.validate_on_submit():
    personnel = model.Personnel(form.id.data, form.first_name.data, form.last_name.data, form.company.data, "1")
    model.db.session.add(personnel)
    model.db.session.commit()
    
    flask.flash(f"החייל {form.first_name.data} {form.last_name.data} נוסף בהצלחה", "success")
    return flask.redirect(flask.url_for("hello"))
    
  return flask.render_template("personnel_registration.html", form=form)

@app.route("/onereport/managers/register_user", methods=["GET", "POST"])
def register_user() -> str:
  form = forms.UserRegistrationFrom()
  
  if form.validate_on_submit():
    user = model.User(form.email.data, form.username.data, form.role.data, form.company.data)
    model.db.session.add(user)
    model.db.session.commit()
    
    flask.flash(f"הפקיד {form.username.data} נוסף בהצלחה")
    return flask.redirect(flask.url_for("hello"))
  
  return flask.render_template("user_registration.html", form=form)


