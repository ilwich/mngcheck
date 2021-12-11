FROM python:latest
ENV PYTHONUNBUFFERED 1

RUN pip install -U pip
ADD requirements.txt /mngcheck/
RUN pip install -r /mngcheck/requirements.txt uwsgi gevent

ADD dokku/CHECKS /app/
ADD dokku/* /mngcheck/
WORKDIR /mngcheck
COPY . /mngcheck/
RUN /mngcheck/manage.py