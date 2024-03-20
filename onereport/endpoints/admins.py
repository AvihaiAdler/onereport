from onereport import app
from onereport.data import misc
from onereport.dto import user_dto
from onereport.dal import user_dal
from onereport.dal import order_attr
import flask
import flask_login

# TODO:
# pagination
@app.route("/onereport/admins/users", methods=["GET", "POST"])
@flask_login.login_required
def get_all_users(order_by: str, order: str = "ASC") -> str:
  if misc.Role[flask_login.current_user.role] != misc.Role.ADMIN:
    return flask.redirect(flask.url_for("home"))
  
  if not order_attr.UserOrderBy.is_valid_order(order_by):
    flask.flash(f"אין אפשרות לסדר את העצמים לפי {order_by}", category="info")
    return flask.render_template("users.html", users=[])

  if not order_attr.Order.is_valid_order(order):
    flask.flash(f"אין אפשרות לסדר את העצמים בסדר {order}", category="info")
    return flask.render_template("users.html", users=[])
  
  # SELECT * from users
  users = user_dal.get_all_users(order_attr.UserOrderBy[order_by], order_attr.Order[order])
  return flask.render_template("users.html", users=[user_dto.UserDTO(user) for user in users])