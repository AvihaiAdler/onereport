#### Deployment
The dreaded one. Below are some detail explanation & links to help with deployment. I'm not claining to know what i'm doing in that area, and there might be better methods out there - these are the step i've found to work.

##### Dockrizing
The project comes with a `docker-compose` template with sensitive fields omitted. One must fill those up.
The project also comes with an `nginx_template` file which, too, has to be filled 

Dockerizing related link can be found [here](https://testdriven.io/blog/dockerizing-flask-with-postgres-gunicorn-and-nginx/)
Nginx & certificate related link can be found [here](https://phoenixnap.com/kb/letsencrypt-docker)

##### Misc
Setting up the server can be done by following [this](https://www.youtube.com/watch?v=goToXTC96Co)
Attaching the domain name to said server can be done following [this](https://www.youtube.com/watch?v=LUFn-QVcmB8)

The Process of installing docker (on ubuntu) can be found [here](https://docs.docker.com/engine/install/ubuntu/) 
Installing docker-compose can be found [here](https://docs.docker.com/compose/install/linux/), though some modifications might be required:
- `sudo apt update`
- `curl -SL https://github.com/docker/compose/releases/download/v2.26.1/docker-compose-linux-x86_64 -o /usr/local/lib/docker/cli-plugins/docker-compose`