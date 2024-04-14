import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", None)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "SQLALCHEMY_DATABASE_URI", "sqlite:///site.db"
    )
    OAUTH2_PROVIDERS = {
        # Google OAuth 2.0 documentation:
        # https://developers.google.com/identity/protocols/oauth2/web-server#httprest
        "google": {
            "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
            "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET"),
            "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
            "token_url": "https://oauth2.googleapis.com/token",
            "userinfo": {
                "url": "https://www.googleapis.com/oauth2/v3/userinfo",
                "email": lambda json: json["email"],
            },
            "scopes": ["https://www.googleapis.com/auth/userinfo.email"],
        }
    }
    SCHEME = os.environ.get("SCHEME", "https")
    PHONE = os.environ.get("PHONE", None)
    EMAIL = os.environ.get("EMAIL", None)
