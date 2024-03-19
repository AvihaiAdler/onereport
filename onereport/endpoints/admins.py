from onereport import app
from onereport.data import model
from onereport.data import misc
from onereport.data import user_dto
import flask
import flask_login

# TODO:
# pagination
@app.route("/onereport/admins/users", methods=["GET", "POST"])
@flask_login.login_required
def get_all_users() -> str:
  if misc.Role[flask_login.current_user.role] == misc.Role.USER:
    return flask.redirect(flask.url_for("home"))
  
  users = model.db.session.query(model.User).all()
  return flask.render_template("users.html", users=[user_dto.UserDto(user) for user in users])