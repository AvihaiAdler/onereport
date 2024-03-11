import uuid
import flask

app = flask.Flask(__name__)

# users
app.post("/onereport/api/v1/users/login/<username>")
def user_login(username: str) -> str:
  """login a user using OAuth

  Args:
      username (str): email of the user who wish to log in

  Returns:
      str: user boundry as a JSON
  """
  pass

#items
app.put("/onereport/api/v1/items/<username>/<uuid:item_id>")
def item_set_presence(username: str, item_id: uuid) -> None:
  """modifies item::presence

  Args:
      username (str): the username of the user wishing too set item::presence
      item_id (str): the id of the item
  """
  pass

app.get("/onereport/api/v1/items/<username>/<uuid:item_id>")
def item_get(username: str, item_id: uuid) -> str:
  """gets one item

  Args:
      username (str): the username requesting the item
      item_id (str): the desired item id

  Returns:
      str: item boundary as a JSON
  """
  pass

# pagination required
app.get("/onereport/api/v1/items/<username>")
def items_get_all(username: str) -> str:
  """get all items in the user space

  Args:
      username (str): the user requesting the items

  Returns:
      str: a list of all items in the user space as JSON
  """
  pass

# managers
app.post("/onereport/api/v1/managers/users/<username>")
def user_create(username: str) -> str:
  """creates a new user

  Args:
      username (str): the username who wish to create the user

  Returns:
      str: a user boundary
  """
  pass

app.put("/onereport/api/v1/managers/users/<username>")
def user_update(username: str) -> None:
  pass

app.delete("/onereport/api/v1/managers/users/<username>")
def user_delete(username: str) -> None:
  pass

app.post("/onereport/api/v1/managers/items/<username>")
def item_create(username: str) -> str:
  pass

app.put("/onereport/api/v1/managers/items/<username>/<uuid:item_id>")
def item_update(username: str, item_id: uuid) -> str:
  pass

app.delete("/onereport/api/v1/managers/items/<uuid:item_id>")
def item_delete(item_id: uuid) -> None:
  pass
