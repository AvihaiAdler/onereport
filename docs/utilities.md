##### running
manually one can do `python -m flask --app onereport run --debug`.
otherwise just launch `manage.py`. i.e. `python manage.py run` the `debug` flag can be passed to it as well.

##### util
The app comes with a some commands to help start the app, these commands can be used to:
- initialize the db
- register a user
- register a personnel
- register users / personnel (plural)
  
##### using the commands
The commands above can be accessed by invoking `flask --app onereport commands [command_name] [command_arguments]. As an example:
`flask --app onereport commands init_db` since `init_db` accept no arguments - no arguments were given. for a list to all of the (custom) commands one can go to [here](https://github.com/AvihaiAdler/onereport/tree/main/onereport/controller/commands.py)

#### loading dummy data in bulk
When testing - instead of doing the steps above manually, one can use the the various utils offered by the app.
The app provides a method which requires a path to a file where all the desired data is placed. Said file can be created using the template `resources/template.json`. As an example, A User might look like this:
```json
  {
    "id": "0000001",
    "email": "John.Doe@demo.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "ADMIN",  // possible values are "USER", "MANAGER", "ADMIN" as shown in `data/misc.py::Role`. one _should_ have at least one ADMIN 
    "company": "A",   // possible values are "A", "B", "C", "SUPPORT", "HEADQUARTERS" as shown in `data/misc.py::Company`
    "platoon": "_4"   // possible valuse are "UNCATEGORIZED", "_1", "_2", "_3", "_4", "_5", "_6", "_7", "_8", "_9" as shown in `data/misc.py::Platoon`
  }
```

A Personnel might look like this:
```json
  {
    "id": "0000002",
    "first_name": "Jane",
    "last_name": "Doe",
    "company": "HEADQUARTERS", // possible values are "A", "B", "C", "SUPPORT", "HEADQUARTERS" as shown in `data/misc.py::Company`
    "platoon": "_3"            // possible valuse are "UNCATEGORIZED", "_1", "_2", "_3", "_4", "_5", "_6", "_7", "_8", "_9" as shown in `data/misc.py::Platoon`
  } 
```

One can add as many personnel as they want, or as many users as they want.
One can omit all personnel entirely (by deleting the "Personnel" and everything follows it up until and including the closing `]`).
One can omit all users entirely (by deleting the "Users" and everything follows it up until and including the closing `]`), though it is recommended one have at least _one_ user with the role of `ADMIN` saved into the database.

To use it one can simply type `flask --app onereport commands register_users "path/to/users_and_personnel.json"`.

That said - one can do all the above manually as detailed below:

##### drop db:
```py
python
import onereport
onereport.drop_all()
```

##### create db:
```py
python
import onereport
onereport.create_all()
```

##### register user:
```py
python
import onereport
from onereport.data.model import User
user = User("email.goes.here@demo.com", "first.name.goes.here", "last.name.goes.here", "role.name", "company.name")
# for example: user = User("john.doe@demo.com", "John", "Doe", "USER", "SUPPORT")
onereport.register_user(user)
```

##### query data:
```py
from onereport import app
from onereport.dal import user_dal, order_attr
with app.app_context():
  user_dal.find_all_users(order_attr.UserOrderBy.EMAIL, order_attr.Order.ASC)
```