Endpoints:

Users:

| description | method | URL                                      | input | output        |
| ----------- | ------ | ---------------------------------------- | ----- | ------------- |
| login user  | POST   | /onereport/api/v1/users/login/{username} | -     | user boundary |


<br>
Items:

| description                      | method | URL                                          | input         | output                  |
| -------------------------------- | ------ | -------------------------------------------- | ------------- | ----------------------- |
| update item (sets presence only) | PUT    | /onereport/api/v1/items/{username}/{item_id} | item boundary | -                       |
| retrieve item                    | GET    | /onereport/api/v1/items/{username}/{item_id} | -             | item boundary           |
| get all items                    | GET    | /onereport/api/v1/items/{username}           | -             | list of item boundaries |

<br>
Managers:

| description       | method | URL                                                  | input         | output        |
| ----------------- | ------ | ---------------------------------------------------- | ------------- | ------------- |
| create a new user | POST   | /onereport/api/v1/manager/users/{username}           | user boundray | user boundary |
| update user       | PUT    | /onereport/api/v1/manager/users/{username}           | user boundary | -             |
| create a new item | POST   | /onereport/api/v1/manager/items/{username}           | item boundary | item boundary |
| update item       | PUT    | /onereport/api/v1/manager/items/{username}/{item_id} | item boundary | -             |
| delete user       | DELETE | /onereport/api/v1/manager/users/{username}           | -             | -             |
| delete item       | DELETE | /onereport/api/v1/manager/items/{item_id}            | -             | -             |


<br>
Boundaries:
user_boundary:
 
```json
{
  "username": String,
  "role": String,
  "space": String,
}
```

item_boundary:
```json
{
  "item_id": {
    "id": UUID,
    "space": String,
  },
  "type": String,
  "created_timestamp": Date,
  "created_by": String,
  "active": Bool,
  "attributes": {
    key: value,
    key: value,
    ...
  },
}
```


