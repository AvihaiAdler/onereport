##### Testing
The most annoying thing (for me!) to write. <br>
Since in time of writing - time is a factor, and since learning how to write proper tests for a flask app might take some of that time (and since testing isn't something i personnaly enjoy) - there are currently no automated tests written for the project sadly.
That said - since _some_ tests must be performed - here's a manual test suit the app must pass before deployment:

###### Common
- as a non loged in user try to hit any route (beside `login`) specified [here](https://github.com/AvihaiAdler/onereport/tree/main/docs/routes.md) and make sure to get a 401

###### Users
- as a user login into the system
- as a user try to hit one of the endpoints belonging to the `MANAGERS` / `ADMINS` and make sure you get 401
- as a user update a personnel and see the changes persist
- as a user create a report for your company, send it, switch to some other page - load the report back and make sure it was loaded currectly
- as a user edit a report and send it

###### Managers
- as a manager try to hit one of the endpoints belonging to the `ADMINS` and make sure you get 401
- as a manager update a personnel and see the changes persist
- as a manager try to promote a personnel to a `USER`
- as a manager try to demote a `USER` to a personnel
- as a manager try to promote/demote yourself and make sure you get 403
- as a manager load in the personnel list of every company
- as a manager load in the report list of every company

###### Admins
- as an admin delete all personnel
- as an admin add personnel via `/onereport/admins/personnel/upload`
- as an admin update an active personnel to inactive and see the changes persist
- as an admin update an inactive personnel to active and see the changes persist