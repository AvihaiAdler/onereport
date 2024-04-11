##### Running
When testing locally one need to follow the following steps:
- Create a `.env` file. Said file need to contain all the fields [this](https://github.com/AvihaiAdler/onereport/tree/main/resources/env_template) file has. 
- Create the DB by invoing: `flask --app onereport commands db_create`
- Register (an) admin/s with either: 
  - `flask --app onereport commands register_user "admin as json string"`
  - `flask --app onereport commands register_users "path/to/users.json`
- launch the app with `python manage.py run --debug`

##### Building
Build a docker image is as simple as typing `docker build .`


##### docker-compose
Building and launching with docker compose is slightly trickier:
- Go to [here](https://github.com/AvihaiAdler/onereport/tree/main/docker-compose-template.yaml) and fill out the blacked lines
- Run `docker-compose -f path/to/your/docker-compose-file.yaml up --build` (add `-d` to launch in the background)
- Run `docker-compose -f path/to/your/docker-compose-file.yaml exec -it onereport sh` to get a shell into your `onereport` container
- To create the db repeat the steps listed above
- To ensure the tables were created do:
  - `docker-compose -f path/to/your/docker-compose-file.yaml exec -it db sh`
  - `psql --username=your_db_username_as_written_in_onereport-compose.yaml --dbname=your_dbname_as_written_in_onereport-compose.yaml`
  - `\l` (to list all dbs)
  - `\c your_desired_db` (to list the tables in said db)
  - `\q` to quit
- Use `docker-compose -f path/to/your/docker-compose-file.yaml down` to terminate your containers when you're done
If the above does work, please use `docker-compose -f path/to/your/docker-compose-file.yaml down -v` (to remove the containers alongside their attached volumes) and redo the process above

  