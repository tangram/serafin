FROM python:3.6

RUN apt-get update && apt-get install -y supervisor

RUN curl -sL https://deb.nodesource.com/setup_6.x | bash - && \
    apt-get install -y nodejs && \
    apt-get install npm -y && \
    npm install -g bower

RUN apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENV PYTHONUNBUFFERED 1
WORKDIR /code
COPY bower.json .bowerrc /code/
RUN bower --allow-root install
COPY requirements.txt /code/
COPY huey-2.3.2/ /code/
RUN pip install -r requirements.txt
RUN pip install ptvsd
RUN pip install https://github.com/darklow/django-suit/tarball/v2
COPY supervisor.conf /etc/supervisor/supervisor.conf
COPY . /code/
RUN     python huey-2.3.2/setup.py install
RUN mkdir -p /vol/web/media
RUN mkdir -p node_modules
RUN mkdir -p /vol/web/static
RUN python manage.py collectstatic --noinput
EXPOSE 8000
ENTRYPOINT ["supervisord", "-c", "/etc/supervisor/supervisor.conf"]
