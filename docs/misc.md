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
  user_dal.get_all_users(order_attr.UserOrderBy.EMAIL, order_attr.Order.ASC)
```
