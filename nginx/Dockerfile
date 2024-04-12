FROM nginx:stable-alpine
RUN rm /etc/nginx/conf.d/default.conf
COPY ./nginx.conf /etc/nginx/conf.d
# WORKDIR /usr/nginx
# COPY . /usr/nginx/