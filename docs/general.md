#### Routes
Due to the fact that i have practically 0 knowledge in frontend development (and no real interest in learning it), and due to the fact that, in time of writing, time is a factor - the server talks in _html pages_ rather than JSONs. This means, among other things, that the API itself only consists from `GET` & `POST` endpoints rather than something which actually resemble a sane system.

In order to use this service for bigger frames (i.e. Brigade and above), or to use it as a service for a bigger system - one will need to replace the entire controller layer with a proper RESTful layer (which shouldn't be _that_ complicated considering).

With the above in mind - the routes for this service are divided into 5 'sections', Some with a permission level requirement to them. As an example one with a role of `USER` may only interact with the routes listed under the users subsection. One with the role of `MANAGER` may only interact with the routes listed under the managers subsection and so on.

##### Common
These are the routes everyone have access to
| Description | methods | URL                 |
| ----------- | ------- | ------------------- |
| login       | GET     | `/`                 |
|             |         | `/onereport/login`  |
| logout      | GET     | `/onereport/logout` |
| home page   | GET     | `/onerpeport/home`  |
| about page  | GET     | `/onereport/about`  |

##### Authentication
The routes are used to authenticate the user.
| Description                           | methods | URL                               |
| ------------------------------------- | ------- | --------------------------------- |
| setting up the authentication process | GET     | `/onereport/authorize/<provider>` |
| authenticating against the provider   | GET     | `/onereport/callback/<provider>`  |

##### Users
| Description                           | methods   | URL                                      | Query pamaeters       |
| ------------------------------------- | --------- | ---------------------------------------- | --------------------- |
| get all active personnel in a company | GET, POST | `/onereport/users/personnel`             | order_by, order       |
| update a personnel in a company       | GET, POST | `/onereport/users/personnel/<id>/update` |                       |
| create a report for a company         | GET, POST | `/onereport/users/report`                | order_by, order       |
| get all reports of a company          | GET       | `/onereport/users/reports`               | order, page, per_page |
| get a report                          | GET       | `/onereport/users/report/<id>`           |                       |

##### Managers
| Description                           | methods   | URL                                         | Query pamaeters                 |
| ------------------------------------- | --------- | ------------------------------------------- | ------------------------------- |
| register a personnel                  | GET, POST | `/onereport/managers/personnel/register`    |                                 |
| register a user                       | GET, POST | `/onereport/managers/users/<id>/register`   |                                 |
| update a personnel                    | GET, POST | `/onereport/managers/personnel/<id>/update` |                                 |
| update a user                         | GET, POST | `/onereport/managers/users/<email>/update`  |                                 |
| get all active users                  | GET, POST | `/onereport/managers/users`                 | order_by, order                 |
| get all active personnel of a company | GET, POST | `/onereport/managers/personnel`             | company, order_by, order        |
| create a report for a company         | GET, POST | `/onereport/managers/report`                | order_by, order                 |
| get all reports for a company         | GET       | `/onereport/managers/reports`               | company, order, page, page_page |
| get all unified reports               | GET       | `/onereport/managers/reports/unified`       | order, page, per_page           |
| get a report                          | GET       | `/onereport/managers/report/<id>`           | company                         |
| get a unified report                  | GET       | `/onereport/managers/report/unified/<date>` | order_by, order                 |

##### Admins
| Description                    | methods   | URL                                       | Query pamaeters                |
| ------------------------------ | --------- | ----------------------------------------- | ------------------------------ |
| register a personnel           | GET, POST | `/onereport/admins/personnel/register`    |                                |
| register a user                | GET, POST | `/onereport/admins/users/<id>/register`   |                                |
| update a personnel             | GET, POST | `/onereport/admins/personnel/<id>/update` |                                |
| update a user                  | GET, POST | `/onereport/admins/users/<email>/update`  |                                |
| get all users                  | GET, POST | `/onereport/admins/users`                 | order_by, order                |
| get all personnel of a company | GET, POST | `/onereport/admins/personnel`             | company, order_by, order       |
| create a report for a company  | GET, POST | `/onereport/admins/report`                | order_by, order                |
| get all reports for a company  | GET       | `/onereport/admins/reports`               | company, order, page, per_page |
| get all unified reports        | GET       | `/onereport/admins/reports/unified`       | order, page, per_page          |
| get a report                   | GET       | `/onereport/admins/report/<id>`           | company                        |
| delete a report                | GET       | `/onereport/admins/report/<id>/delete`    |                                |
| get a unified report           | GET       | `/onereport/admins/report/unified/<date>` | order_by, order                |
| delete all reports             | GET       | `/onereport/admins/report/delete`         |                                |
| delete all personnel           | GET       | `/onereport/admins/personnel/delete`      |                                |
| add personnel                  | GET, POST | `/onereport/admins/personnel/upload`      |                                |


##### Known bugs
- [x] due to the way `User` & `Personnel` interact with each other - promoting a `Personnel` / demoting a `User` will erase said person from all previous reports : FIXED
- [x] mail addresses are case sensitve  : FIXED
- [x] non admins can deactivate an admin by deactivating the personnel 'behind' said admin : FIXED