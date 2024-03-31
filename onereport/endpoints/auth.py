from onereport import app
from onereport.dal import user_dal
import flask
import flask_login
import secrets
import requests
import urllib.parse as urllib_parse


@app.route("/onereport/authorize/<provider>")
def oauth2_authorize(provider: str):
    if not flask_login.current_user.is_anonymous:
        return flask.redirect(flask.url_for("home"))

    provider_data = flask.current_app.config["OAUTH2_PROVIDERS"].get(provider)
    if provider_data is None:
        flask.abort(404)

    # generate a random string for the state parameter
    flask.session["oauth2_state"] = secrets.token_urlsafe(16)

    # create a query string with all the OAuth2 parameters
    query = urllib_parse.urlencode(
        {
            "client_id": provider_data["client_id"],
            "redirect_uri": flask.url_for(
                "oauth2_callback", provider=provider, _external=True
            ),
            "response_type": "code",
            "scope": " ".join(provider_data["scopes"]),
            "state": flask.session["oauth2_state"],
        }
    )

    app.logger.debug(f"{oauth2_authorize.__name__} completed auth setup redirecting")
    # redirect the user to the OAuth2 provider authorization URL
    return flask.redirect(provider_data["authorize_url"] + "?" + query)


@app.route("/onereport/callback/<provider>")
def oauth2_callback(provider: str):
    if not flask_login.current_user.is_anonymous:
        return flask.redirect(flask.url_for("home"))

    provider_data = flask.current_app.config["OAUTH2_PROVIDERS"].get(provider)
    if provider_data is None:
        flask.abort(404)

    # if there was an authentication error, flash the error messages and exit
    if "error" in flask.request.args:
        for key, value in flask.request.args.items():
            if key.startswith("error"):
                app.logger.error(f"{oauth2_callback.__name__} {key} {value}")
                flask.flash(f"{key}: {value}", category="danger")
        return flask.redirect(flask.url_for("login"))
    
    # make sure that the state parameter matches the one we created in the
    # authorization request
    if flask.request.args["state"] != flask.session.get("oauth2_state"):
        app.logger.debug("invalid state")
        flask.abort(401)

    # make sure that the authorization code is present
    if "code" not in flask.request.args:
        app.logger.error(f"{oauth2_callback.__name__} authorization code is not present")
        flask.abort(401)

    # exchange the authorization code for an access token
    body = {
        "client_id": provider_data["client_id"],
        "client_secret": provider_data["client_secret"],
        "code": flask.request.args["code"],
        "grant_type": "authorization_code",
        "redirect_uri": flask.url_for(
            "oauth2_callback", provider=provider, _external=True
        ),
    }
    app.logger.debug(f"{oauth2_callback.__name__} trying to exchange the authorization code for an access token")
    response = requests.post(
        provider_data["token_url"], data=body, headers={"Accept": "application/json"}
    )

    if response.status_code != 200:
        app.logger.error(f"{oauth2_callback.__name__} didn't got an access token. response code {response.status_code}")
        flask.abort(401)

    app.logger.debug(f"{oauth2_callback.__name__} got back {response.status_code} {response.json()}")
    
    oauth2_token = response.json().get("access_token")
    if not oauth2_token:
        app.logger.error(f"{oauth2_callback.__name__} didn't get a token back")
        flask.abort(401)

    # use the access token to get the user's email address
    app.logger.debug(f"{oauth2_callback.__name__} trying to get user's email")
    response = requests.get(
        provider_data["userinfo"]["url"],
        headers={
            "Authorization": "Bearer " + oauth2_token,
            "Accept": "application/json",
        },
    )
    if response.status_code != 200:
        app.logger.debug(f"{oauth2_callback.__name__} didn't success getting user email. response code {response.status_code}")
        flask.abort(401)

    app.logger.debug(f"{oauth2_callback.__name__} got back {response.status_code} {response.json()}")
    
    email = provider_data["userinfo"]["email"](response.json())

    # find the user in the database
    user = user_dal.find_user_by_email(email)
    if user is None or not user.active:
        app.logger.error(f"{oauth2_callback.__name__} failed to find {email} in the database. user doen't exists")
        flask.abort(401)

    # log the user in
    ret = flask_login.login_user(user)
    if ret:
        app.logger.debug(f"{oauth2_callback.__name__} {user} logged in")
    else:
        app.logger.error(f"{oauth2_callback.__name__} something went wrong. login_user failed")
    
    return flask.redirect(flask.url_for("home"))
