FROM ubuntu:14.10

MAINTAINER Romain Commandé, commande.romain@gmail.com

RUN apt-get update
RUN apt-get install -y python-pip python-virtualenv build-essential python3-dev libzmq-dev
RUN virtualenv -p /usr/bin/python3 /srv/papaye-venv
RUN /srv/papaye-venv/bin/pip install uwsgi gunicorn
RUN mkdir /srv/papaye
ADD . /srv/papaye
WORKDIR /srv/papaye/
RUN /srv/papaye-venv/bin/pip install -r /srv/papaye/requirements.txt
RUN /srv/papaye-venv/bin/papaye_init --user admin --password admin /srv/papaye/production.ini
RUN /srv/papaye-venv/bin/papaye_evolve /srv/papaye/production.ini
ENTRYPOINT /srv/papaye-venv/bin/uwsgi --http=0.0.0.0:8080 --paste config:/srv/papaye/production.ini --master --processes 4 --enable-threads
