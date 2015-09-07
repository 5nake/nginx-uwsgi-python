Hello there! 

This is my own project of the website blog, bulit on the chain:
- Nginx
- uwsgi
- WSGI python app
- Postgresql database.


Project required following packages:

BACKEND:
- nginx/1.4.6
- uwsgi/2.0.11.1
- python/2.7.6
- postgresql/9.3.9
- psycopg2/2.6.1

FRONTEND:
- Jinja2 (Backend also required)
- Bootstrap
- jQuery
- CKEditor


List of required tables in Postgresql database:
- CREATE TABLE users (id SERIAL PRIMARY KEY, name VARCHAR(64), login VARCHAR(64), password BYTEA);
- CREATE TABLE articles (article_id SERIAL PRIMARY KEY, article_title VARCHAR(64), article_author VARCHAR(64), article_text VARCHAR(12000), article_date TIMESTAMP);
- CREATE TABLE comments (comment_id SERIAL PRIMARY KEY, article_idc INTEGER, comment_author VARCHAR(64), comment_text VARCHAR(800), comment_date TIMESTAMP);
- CREATE TABLE sessions (user_id INTEGER, session_id VARCHAR(32), ident_id BYTEA, date TIMESTAMP);
- CREATE TABLE images (img_id SERIAL PRIMARY KEY);


UPSTART FILE to Manage the App (on Ubuntu /etc/init/myapp.conf)

description "uWSGI instance to serve myapp"

start on runlevel [2345]
stop on runlevel [!2345]

setuid demo
setgid www-data

script
    cd /home/demo/myapp
    . myappenv/bin/activate
    uwsgi --ini myapp.ini
end script

After this you can reload web-application with "sudo restart myapp"
