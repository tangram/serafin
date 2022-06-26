FROM python:3.10

RUN apt-get update && apt-get install -y supervisor nodejs npm
RUN npm install -g bower
RUN pip install poetry
RUN apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENV PYTHONUNBUFFERED 1
WORKDIR /app

COPY bower.json .bowerrc /app/
RUN bower --allow-root install

COPY pyproject.toml poetry.lock /app/
RUN poetry install --no-dev --no-interaction

COPY . /app/

EXPOSE 8000
ENTRYPOINT ["supervisord", "-c", "supervisor.conf"]
