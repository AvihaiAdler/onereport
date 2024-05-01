#### Deployment
The dreaded one. Below are some detailed explanation & links to help with deployment. I'm not claiming to know what i'm doing in that area, and there might be better methods out there - these are the steps i've found to work.

##### Dockrizing
The project comes with a `docker-compose` template with sensitive fields omitted, one must fill those up.
The project also comes with an `ngnix.conf` files which, too, has to be filled (mainly switching my personal domain name with yours). 

Dockerizing related link can be found [here](https://testdriven.io/blog/dockerizing-flask-with-postgres-gunicorn-and-nginx/).
Nginx & ssl certificate related link can be found [here](https://mindsers.blog/en/post/https-using-nginx-certbot-docker/).

##### Misc
Setting up the server can be done by following [this](https://www.youtube.com/watch?v=goToXTC96Co).
Attaching the domain name to said server can be done following [this](https://www.youtube.com/watch?v=LUFn-QVcmB8)

The Process of installing docker (on ubuntu) can be found [here](https://docs.docker.com/engine/install/ubuntu/). 
Installing docker-compose can be found [here](https://docs.docker.com/compose/install/linux/), though some modifications might be required:
- `sudo apt update`
- `curl -SL https://github.com/docker/compose/releases/download/v2.26.1/docker-compose-linux-x86_64 -o /usr/local/lib/docker/cli-plugins/docker-compose`

#### In depth guide
deployment:
- `git clone https://github.com/AvihaiAdler/onereport`
- `scp` over your `.env` & `docker-compose.yaml` files
- `cp -r onereport/nginx .` 
- `cd onereport`
 
get an ssl certificate:
- `docker compose -f cert-compose.yaml up --build -d`
- `docker compose run --rm  certbot certonly --webroot --webroot-path /var/www/certbot/ --dry-run -d [domain name]` and ensure a successful completion
- `docker compose run --rm  certbot certonly --webroot --webroot-path /var/www/certbot/ -d [domain name]` and wait for a successful completion
- (to renew a cert `docker compose run --rm certbot renew`)
- `docker compose -f cert-compose.yaml down`
- `mv ../ngnix/conf/nginx.conf ../ngnix/conf/nginx.conf.prev`
- `mv ../ngnix/conf/nginx.conf.final ../ngnix/conf/nginx.conf`
- `sudo docker compose up --build -d`

create db and admin:
- `docker compose exec -it onereport sh`
- `flask --app onereport commands db_create`
- `flask --app onereport commands register_user ...` or `flask --app onereport commands register_users ...`

##### Google Auth links
- [full guide](https://blog.miguelgrinberg.com/post/oauth-authentication-with-flask-in-2023)
- [google oauth2 reference](https://developers.google.com/identity/protocols/oauth2/web-server)
- [credentials management](https://console.cloud.google.com/apis/credentials)