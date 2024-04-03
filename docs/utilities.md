##### running
python -m flask --app onereport run --debug

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

#### loading dummy data in bulk
When testing - instead of doing the steps above manually, one can use the script located in `script/db_utils.py` instead.
The script requires a path to a file where all the desired data is placed. Said file can be created using the template `script/template.json`. As an example, A User might look like this:
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

One can add as many personnel as they want, or as many users as thye want.
One can omit all personnel entirely (by deleting the "Personnel" and everything follows it up until and including the closing `]`).
One can omit all users entirely (by deleting the "Users" and everything follows it up until and including the closing `]`), though it is recommended one can have at least _one_ user with the role of `ADMIN` saved into the database.