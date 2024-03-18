##### running
python -m flask --app onereport run --debug

##### create db:
```py
python
from onereport import app
from onereport.data import model

with app.app_context():
  model.db.create_all()
```

##### query data:
```py
with app.app_context():
  model.User.query.all()
```
