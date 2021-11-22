FROM python:3.9

RUN pip install uwsgi==2.0.20 --extra-index-url https://www.piwheels.org/simple

EXPOSE 8080
CMD ["uwsgi", "uwsgi.ini"]

RUN mkdir app
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ARG data_path=/app/data

VOLUME ["$data_path"]
ENV USER_DB="sqlite:///$data_path/users.db"

ENV TIMEZONE="Europe/Madrid" LOG_LEVEL="INFO"
ENV INICIO_JORNADA='{"hour":7, "minute":30}'
# Estas variables deben sustituirse para que funcione la app
ENV DOMAIN_NAME=example.com TOKEN=124-ABCD-678-EFGH
ENV INTERNAL_NAME=http://fichabot:8080 SCHEDULER_URL=http://scheduler:8080 FICHAJE=http://openhr:8080

# Se copian los ficheros por frecuencia de modificación: de menos a más
COPY wsgi_app.py .

COPY fichabot ./fichabot/
COPY uwsgi.ini .
