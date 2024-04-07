#### Routes
Due to the fact that i have pracitaclly 0 knowledge in frontend development (and no real intereset in learning it), and due to the fact that, in time of writing, time is a factor - the server talks in _html pages_ rather than JSONs.

Baring that in mind - the routes are divided into 3. Each 'section' correspond to a permission level, i.e. One with a role of `USER` may only interact with the routes listed under the users subsection. One with the role of `MANAGER` may only interact with the routes listed under the managers subsection and so on.

##### Common
These are the routes everyone have access to
| Description | methods | URL                 |
| ----------- | ------- | ------------------- |
| login       | GET     | "/"                 |
|             |         | "/onereport/login"  |
| logout      | GET     | "/onereport/logout" |
| home page   | GET     | "/onerpeport/home"  |
| about page  | GET     | "/onereport/about"  |

##### Authentication
The routes are used to authenticate the user.
| Description                           | methods | URL                               |
| ------------------------------------- | ------- | --------------------------------- |
| setting up the authentication process | GET     | "/onereport/authorize/<provider>" |
| authenticating against the provider   | GET     | "/onereport/callback/<provider>"  |

##### Users
| Description                           | methods   | URL                                      | Query pamaeters |
| ------------------------------------- | --------- | ---------------------------------------- | --------------- |
| get all active personnel in a company | GET, POST | "/onereport/users/personnel"             | order_by, order |
| update a personnel in a company       | GET, POST | "/onereport/users/personnel/<id>/update" |                 |
| create a report for a company         | GET, POST | "/onereport/users/report"                | order_by, order |
| get all reports of a company          | GET       | "/onereport/users/reports"               | order           |
| get a report                          | GET       | "/onereport/users/report/<id>"           |                 |

##### Managers
| Description                           | methods   | URL                                         | Query pamaeters |
| ------------------------------------- | --------- | ------------------------------------------- | --------------- |
| register a personnel                  | GET, POST | "/onereport/managers/personnel/register"    |                 |
| register a user                       | GET, POST | "/onereport/managers/users/<id>/register"   |                 |
| update a personnel                    | GET, POST | "/onereport/managers/personnel/<id>/update" |                 |
| update a user                         | GET, POST | "/onereport/managers/users/<email>/update"  |                 |
| get all active users                  | GET, POST | "/onereport/managers/users"                 | order_by, order |
| get all active personnel of a company | GET, POST | "/onereport/managers/personnel"             | order_by, order |
| create a report for a company         | GET, POST | "/onereport/managers/report"                | order_by, order |
| get all reports for a company         | GET       | "/onereport/managers/reports"               | company, order  |
| get a report                          | GET       | "/onereport/managers/report/<id>"           | company         |

##### Admins
| Description                    | methods   | URL                                       | Query pamaeters |
| ------------------------------ | --------- | ----------------------------------------- | --------------- |
| register a personnel           | GET, POST | "/onereport/admins/personnel/register"    |                 |
| register a user                | GET, POST | "/onereport/admins/users/<id>/register"   |                 |
| update a personnel             | GET, POST | "/onereport/admins/personnel/<id>/update" |                 |
| update a user                  | GET, POST | "/onereport/admins/users/<email>/update"  |                 |
| get all users                  | GET, POST | "/onereport/admins/users"                 | order_by, order |
| get all personnel of a company | GET, POST | "/onereport/admins/personnel"             | order_by, order |
| create a report for a company  | GET, POST | "/onereport/admins/report"                | order_by, order |
| get all reports for a company  | GET       | "/onereport/admins/reports"               | company, order  |
| get a report                   | GET       | "/onereport/admins/report/<id>"           | company         |
| delete all reports             | GET       | "/onereport/admins/report/delete          |                 |
| delete all personnel           | GET       | "/onereport/admins/personnel/delete       |                 |
| add personnel                  | GET, POST | "/onereport/admins/personnel/upload"      |                 |