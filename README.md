# URL Shortener

A small Flask URL shortener backed by PostgreSQL for persistent storage and Redis for cached redirects and rate limiting. The web interface lets you shorten a URL and copy the result.

## Run with Docker Compose

Requirements: Docker Desktop with Docker Compose.

From this directory, run:

```sh
docker compose up --build
```

Open [http://localhost:5000](http://localhost:5000) to use the web interface. The first startup builds the Flask image and starts PostgreSQL and Redis. The database is kept in the `postgres_data` Docker volume.

To stop the services, press `Ctrl+C` in the terminal, then run:

```sh
docker compose down
```

To also remove the saved database volume, run `docker compose down -v`.

## API

Create a short link by sending a JSON request:

```sh
curl -X POST http://localhost:5000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com/a/long/page"}'
```

A successful response contains the short URL and short code:

```json
{"short_url":"http://localhost:5000/1","short_code":"1"}
```

Visit `http://localhost:5000/<short_code>` to redirect to the original URL. The service returns `404` when a code is not found. `GET /health` returns a simple health status.

The `/shorten` endpoint is limited to 10 requests per minute per client IP.

## Continuous integration

GitHub Actions runs Ruff and pytest on pushes and pull requests targeting `main`. The tests use lightweight fakes for Redis and PostgreSQL, so the CI job does not need Docker or cloud credentials.

To run the same checks locally, install the development dependencies and run:

```sh
python -m pip install -r requirements-dev.txt
ruff check app tests
pytest -q
```

## Project layout

- `docker-compose.yaml` — Flask, PostgreSQL, and Redis services.
- `app/app.py` — Flask routes, code generation, database access, caching, and rate limiting.
- `app/templates/index.html` — web interface.
- `app/init.sql` — database table definition, applied when PostgreSQL initializes its data volume.
- `app/Dockerfile` and `app/requirements.txt` — Python container build and dependencies.

## Configuration

Docker Compose sets the database and Redis connection settings for the app. The current Compose file uses local development credentials and exposes the app on port `5000`; change these values before using the service in a public or production environment.
