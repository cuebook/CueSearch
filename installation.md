# Installation

## Install via Docker

```
mkdir -p ~/cueobserve
wget https://raw.githubusercontent.com/cuebook/CueObserve/latest_release/docker-compose-prod.yml -q -O ~/cueobserve/docker-compose-prod.yml
wget https://raw.githubusercontent.com/cuebook/CueObserve/latest_release/.env -q -O ~/cueobserve/.env
cd ~/cueobserve
```

```
docker-compose -f docker-compose-prod.yml --env-file .env up -d
```

Now visit [localhost:3000](http://localhost:3000) in your browser.&#x20;

## Use Postgres as the application database

SQLite is the default storage database for CueObserve. However, it might not be suitable for production. To use Postgres instead, do the following:

Uncomment given variable in `.env` file:

```
POSTGRES_DB_SCHEMA=cueobserve
POSTGRES_DB_USERNAME=postgres
POSTGRES_DB_PASSWORD=postgres
POSTGRES_DB_HOST=localhost
POSTGRES_DB_PORT=5432
```

## Authentication

CueObserve comes with built-in authentication (powered by Django). By default authentication is disabled, to enable authentication uncomment given variables.

```
DJANGO_SUPERUSER_USERNAME=<USER_NAME>
DJANGO_SUPERUSER_PASSWORD=<PASSWORD>
DJANGO_SUPERUSER_EMAIL=<YOUR_EMAIL@DOMAIN.COM>
IS_AUTHENTICATION_REQUIRED=True
```

If authentication is enabled you can access the [Django Admin](https://docs.djangoproject.com/en/3.2/ref/contrib/admin/) console to do the database operations with a nice UI. To access Django Admin go to [http://localhost:3000/admin](http://localhost:3000/admin) and enter the username and password provided in the `.env` file.

