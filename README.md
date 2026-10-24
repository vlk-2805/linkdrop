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

Visit `http://localhost:5000/<short_code>` to redirect to the original URL. The service returns `404` when a code is not found. `GET /health` returns a simple health status. The `/shorten` endpoint is limited to 10 requests per minute per client IP.

## AWS deployment

The learning deployment uses one small EC2 instance to run the existing Flask, PostgreSQL, and Redis Compose services. GitHub Actions builds the Flask image and deploys it through AWS Systems Manager using GitHub OIDC temporary credentials. It does not use RDS, ElastiCache, ECS, a load balancer, a NAT Gateway, SSH access, or permanent AWS keys in GitHub.

Set a zero-spend AWS Budget alert before creating resources and terminate the EC2 instance when finished testing. See the [AWS EC2 deployment guide](docs/DEPLOYMENT_GUIDE.md) for cost controls, Terraform setup, CI/CD configuration, troubleshooting, teardown, and interview notes. The Terraform files do not create resources until you apply them in your AWS account.

## Project layout

- `docker-compose.yaml` — Flask, PostgreSQL, and Redis services.
- `app/app.py` — Flask routes, code generation, database access, caching, and rate limiting.
- `app/templates/index.html` — web interface.
- `app/init.sql` — database table definition, applied when PostgreSQL initializes its data volume.
- `app/Dockerfile` and `app/requirements.txt` — Python container build.
- `infra/terraform/` — one EC2 host, ECR repository, network, instance role, and GitHub OIDC deploy role.
- `.github/workflows/deploy.yml` — build and deploy on pushes to `main`.
