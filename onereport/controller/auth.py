from onereport.dal import user_dal
from flask import (
    Blueprint,
    current_app,
    redirect,
    url_for,
    request,
    abort,
    flash,
    session,
)
import flask_login
import secrets
import requests
import urllib.parse as urllib_parse


auth = Blueprint("auth", __name__)


# https://blog.miguelgrinberg.com/post/oauth-authentication-with-flask-in-2023
@auth.get("/onereport/authorize/<provider>")
def oauth2_authorize(provider: str):
    if not flask_login.current_user.is_anonymous:
        current_app.logger.warning(
            f"authorized access by {flask_login.current_user} - user already logged in"
        )
        return redirect(url_for("common.home"))

    provider_data = current_app.config["OAUTH2_PROVIDERS"].get(provider)
    if provider_data is None:
        current_app.logger.error(f"no oauth2 config for provider {provider}")
        abort(404)

    # generate a random string for the state parameter
    session["oauth2_state"] = secrets.token_urlsafe(16)

    # create a query string with all the OAuth2 parameters
    query_params = urllib_parse.urlencode(
        {
            "client_id": provider_data["client_id"],
            "redirect_uri": url_for(
                "auth.oauth2_callback",
                _scheme=current_app.config["SCHEME"],
                provider=provider,
                _external=True,
            ),
            "response_type": "code",
            "scope": " ".join(provider_data["scopes"]),
            "state": session["oauth2_state"],
        }
    )

    current_app.logger.debug(f"completed auth setup with query prams:\n{query_params}")
    # redirect the user to the OAuth2 provider authorization URL
    return redirect(f"{provider_data['authorize_url']}?{query_params}")


@auth.get("/onereport/callback/<provider>")
def oauth2_callback(provider: str):
    if not flask_login.current_user.is_anonymous:
        current_app.logger.warning(
            f"authorized access by {flask_login.current_user} - user already logged in"
        )
        return redirect(url_for("common.home"))

    provider_data = current_app.config["OAUTH2_PROVIDERS"].get(provider)
    if provider_data is None:
        current_app.logger.error(f"no oauth2 config for provider {provider}")
        abort(404)

    current_app.logger.debug(f"got a request:\n{request.args}")

    # if there was an authentication error, flash the error messages and exit
    if "error" in request.args:
        for key, value in request.args.items():
            if key.startswith("error"):
                current_app.logger.error(f"{key} {value}")
                flash(f"{key}: {value}", category="danger")
        return redirect(url_for("common.login"))

    # make sure that the state parameter matches the one we created in the
    # authorization request
    if request.args["state"] != session.get("oauth2_state"):
        current_app.logger.error("invalid state - no state in the request")
        abort(401)

    # make sure that the authorization code is present
    if "code" not in request.args:
        current_app.logger.error("authorization code is not present")
        abort(401)

    # exchange the authorization code for an access token
    body = {
        "client_id": provider_data["client_id"],
        "client_secret": provider_data["client_secret"],
        "code": request.args["code"],
        "grant_type": "authorization_code",
        "redirect_uri": url_for(
            "auth.oauth2_callback",
            _scheme=current_app.config["SCHEME"],
            provider=provider,
            _external=True,
        ),
    }
    current_app.logger.debug(
        f"trying to exchange the authorization code for an access token - request body:\n{body}"
    )
    response = requests.post(
        provider_data["token_url"],
        data=body,
        headers={"Accept": "current_application/json"},
    )
    current_app.logger.debug(f"got back: {response.status_code}\n{response.json()}")

    if response.status_code != 200:
        current_app.logger.error(
            f"didn't got an access token. response code {response.status_code}"
        )
        abort(401)

    oauth2_token = response.json().get("access_token")
    if not oauth2_token:
        current_app.logger.error(f"invalid access token {oauth2_token}")
        abort(401)

    # use the access token to get the user's email address
    current_app.logger.debug("trying to get user's email")
    response = requests.get(
        provider_data["userinfo"]["url"],
        headers={
            "Authorization": f"Bearer {oauth2_token}",
            "Accept": "current_application/json",
        },
    )
    current_app.logger.debug(f"got back: {response.status_code}\n{response.json()}")

    if response.status_code != 200:
        current_app.logger.debug(
            f"failed to get user email. response code: {response.status_code}"
        )
        abort(401)

    email = provider_data["userinfo"]["email"](response.json()).lower()

    # find the user in the database
    user = user_dal.find_user_by_email(email)
    if user is None or not user.active:
        current_app.logger.error(
            f"failed to find {email} in the database. user doen't exists"
        )
        abort(401)

    # log the user in
    ret = flask_login.login_user(user)
    if ret:
        current_app.logger.info(f"{user} logged in")
    else:
        current_app.logger.error(f"something went wrong. login_user failed for {user}")

    return redirect(url_for("common.home"))
