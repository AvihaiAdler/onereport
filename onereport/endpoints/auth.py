from onereport import app
from onereport.dal import user_dal
import flask
import flask_login
import secrets
import requests
import urllib.parse as urllib_parse


@app.get("/onereport/authorize/<provider>")
def oauth2_authorize(provider: str):
    if not flask_login.current_user.is_anonymous:
        app.logger.warning(f"authorized access by {flask_login.current_user} - user already logged in")
        return flask.redirect(flask.url_for("home"))

    provider_data = flask.current_app.config["OAUTH2_PROVIDERS"].get(provider)
    if provider_data is None:
        app.logger.error(f"no oauth2 config for provider {provider}")
        flask.abort(404)

    # generate a random string for the state parameter
    flask.session["oauth2_state"] = secrets.token_urlsafe(16)

    # create a query string with all the OAuth2 parameters
    query_params = urllib_parse.urlencode(
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

    app.logger.debug(f"completed auth setup with query prams:\n{query_params}")
    # redirect the user to the OAuth2 provider authorization URL
    return flask.redirect(f"{provider_data['authorize_url']}?{query_params}")


@app.get("/onereport/callback/<provider>")
def oauth2_callback(provider: str):
    if not flask_login.current_user.is_anonymous:
        app.logger.warning(f"authorized access by {flask_login.current_user} - user already logged in")
        return flask.redirect(flask.url_for("home"))

    provider_data = flask.current_app.config["OAUTH2_PROVIDERS"].get(provider)
    if provider_data is None:
        app.logger.error(f"no oauth2 config for provider {provider}")
        flask.abort(404)

    app.logger.info(f"got a request:\n{flask.request.args}")
    
    # if there was an authentication error, flash the error messages and exit
    if "error" in flask.request.args:
        for key, value in flask.request.args.items():
            if key.startswith("error"):
                app.logger.error(f"{key} {value}")
                flask.flash(f"{key}: {value}", category="danger")
        return flask.redirect(flask.url_for("login"))
    
    # make sure that the state parameter matches the one we created in the
    # authorization request
    if flask.request.args["state"] != flask.session.get("oauth2_state"):
        app.logger.error("invalid state - no state in the request")
        flask.abort(401)

    # make sure that the authorization code is present
    if "code" not in flask.request.args:
        app.logger.error("authorization code is not present")
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
    app.logger.debug(f"trying to exchange the authorization code for an access token - request body:\n{body}")
    response = requests.post(
        provider_data["token_url"], data=body, headers={"Accept": "application/json"}
    )
    app.logger.debug(f"got back: {response.status_code}\n{response.json()}")

    if response.status_code != 200:
        app.logger.error(f"didn't got an access token. response code {response.status_code}")
        flask.abort(401)
    
    oauth2_token = response.json().get("access_token")
    if not oauth2_token:
        app.logger.error(f"invalid access token {oauth2_token}")
        flask.abort(401)

    # use the access token to get the user's email address
    app.logger.debug("trying to get user's email")
    response = requests.get(
        provider_data["userinfo"]["url"],
        headers={
            "Authorization": f"Bearer {oauth2_token}",
            "Accept": "application/json",
        },
    )
    app.logger.debug(f"got back: {response.status_code}\n{response.json()}")
    
    if response.status_code != 200:
        app.logger.debug(f"failed to get user email. response code: {response.status_code}")
        flask.abort(401)
    
    email = provider_data["userinfo"]["email"](response.json())

    # find the user in the database
    user = user_dal.find_user_by_email(email)
    if user is None or not user.active:
        app.logger.error(f"failed to find {email} in the database. user doen't exists")
        flask.abort(401)

    # log the user in
    ret = flask_login.login_user(user)
    if ret:
        app.logger.info(f"{user} logged in")
    else:
        app.logger.error(f"something went wrong. login_user failed for {user}")
    
    return flask.redirect(flask.url_for("home"))
