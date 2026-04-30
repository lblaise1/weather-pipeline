# Weather Data Pipeline

An end-to-end ELT pipeline that ingests live weather data from the Weatherstack API, stores it in Postgres, transforms it with dbt, and visualizes it in Superset — all orchestrated by Apache Airflow and packaged as Docker containers.

## What this project demonstrates

This is a working data engineering project that touches every layer of a modern data stack: ingestion, orchestration, transformation, and visualization. The whole pipeline runs locally with a single `docker compose up` command and mirrors the same architectural patterns used by production data teams.

## Architecture

```
┌──────────────────┐     ┌─────────────┐     ┌──────────┐     ┌──────────┐
│  Weatherstack    │────▶│   Airflow   │────▶│ Postgres │────▶│ Superset │
│      API         │     │     DAG     │     │          │     │          │
└──────────────────┘     └─────────────┘     └──────────┘     └──────────┘
                              │                    ▲
                              │                    │
                              │              ┌─────┴─────┐
                              └─────────────▶│    dbt    │
                                             └───────────┘
```

The pipeline runs hourly:
1. **Airflow** triggers an ingestion task that hits the Weatherstack API and writes raw observations to `dev.raw_weather_data` in Postgres.
2. **Airflow** then spawns a fresh dbt container via `DockerOperator` to rebuild the staging and marts models.
3. **Superset** reads from the transformed tables to power the dashboard.

## Tech stack

| Layer | Tool | Why |
|---|---|---|
| Orchestration | Apache Airflow 3.0 | Industry standard for data pipeline scheduling |
| Storage | Postgres 14 | Stores both raw API data and Airflow's metadata |
| Transformation | dbt 1.9 | SQL-based, version-controlled data modeling |
| Visualization | Apache Superset 4.0 | Open-source BI tool with a clean UI |
| Packaging | Docker Compose | Single-command local setup |

## Project structure

```
weather/
├── airflow/
│   └── dags/
│       └── orchestrator.py          # Main DAG: ingestion + dbt
├── api-request/
│   ├── api_request.py               # Weatherstack API client
│   └── insert_records.py            # Postgres ingestion logic
├── dbt/
│   ├── my_project/
│   │   ├── dbt_project.yml
│   │   └── models/
│   │       ├── sources/staging/     # stg_weather_data (cleaned raw)
│   │       └── sources/mart/        # daily_average, weather_report
│   └── profiles.yml                 # dbt connection config
├── postgres/
│   ├── airflow_init.sql             # Creates Airflow's metadata DB
│   └── data/                        # Persistent Postgres volume (gitignored)
├── docker-compose.yml               # Defines all 4 services
├── .env.example                     # Template for environment variables
├── .env                             # Real secrets (gitignored)
└── README.md
```

## Getting started

### Prerequisites
- Docker & Docker Compose
- A free Weatherstack API key — sign up at https://weatherstack.com
- Around 4 GB of free RAM for all four containers

### Setup

1. **Clone the repo**
   ```bash
   git clone https://github.com/<your-username>/weather-pipeline.git
   cd weather-pipeline
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and fill in your Weatherstack API key.

3. **Start the stack**
   ```bash
   docker compose up -d
   ```
   First run pulls about 2 GB of images and takes a few minutes. Subsequent starts are fast.

4. **Wait for services to initialize** (~60 seconds)
   ```bash
   docker compose ps
   ```
   All four services (`db`, `af`, `dbt`, `superset`) should show `Up`.

5. **Initialize Superset (one-time)**
   ```bash
   docker compose exec superset superset db upgrade
   docker compose exec superset superset fab create-admin \
       --username admin --firstname Admin --lastname User \
       --email admin@example.com --password admin
   docker compose exec superset superset init
   ```

### Accessing the services

| Service | URL | Login |
|---|---|---|
| Airflow | http://localhost:8000 | `admin` / see note below |
| Superset | http://localhost:8088 | `admin` / `admin` |
| Postgres | `localhost:5000` | `db_user` / `db_password` |

> **Airflow admin password** is auto-generated on first run. Read it with:
> ```bash
> docker compose exec af cat /opt/airflow/simple_auth_manager_passwords.json.generated
> ```

## Configuration

All configuration lives in `.env`. See `.env.example` for the full list. The most important variables:

| Variable | Description |
|---|---|
| `WEATHERSTACK_API_KEY` | Your API key from weatherstack.com |
| `POSTGRES_PASSWORD` | Postgres user password |
| `SUPERSET_SECRET_KEY` | Random string used for session encryption (generate with `openssl rand -base64 42`) |

## Operating the pipeline

### Running the DAG manually
1. Open Airflow at http://localhost:8000
2. Click `weather-api-dbt-orchestrator`
3. Click the play button (▶) → Trigger DAG

### Inspecting the data
```bash
# Raw API responses
docker compose exec db psql -U db_user -d db -c "SELECT * FROM dev.raw_weather_data ORDER BY id DESC LIMIT 5;"

# Cleaned staging table
docker compose exec db psql -U db_user -d db -c "SELECT * FROM dev.stg_weather_data ORDER BY id DESC LIMIT 5;"

# Daily aggregates
docker compose exec db psql -U db_user -d db -c "SELECT * FROM dev.daily_average ORDER BY date DESC;"
```

### Running dbt directly
```bash
docker compose run --rm dbt run        # build all models
docker compose run --rm dbt test       # run tests
docker compose run --rm dbt debug      # check connection
```

### Tearing it down
```bash
docker compose down              # stop services, keep data
docker compose down -v           # also wipe volumes (fresh start)
```

## Troubleshooting

**"Could not translate host name 'db'"**
The container isn't on the right Docker network. Run `docker compose down && docker compose up -d`.

**"relation 'X__dbt_backup' already exists"**
A previous dbt run was interrupted mid-flight. Drop the backup table:
```bash
docker compose exec db psql -U db_user -d db -c "DROP TABLE IF EXISTS dev.<model_name>__dbt_backup;"
```

**Airflow DAG processor stuck / DAGs not appearing**
Check logs for parse errors: `docker compose logs af | grep ERROR`. Often a missing import in a DAG file.

**Hit Weatherstack rate limit**
Free tier allows 100 calls/month. The DAG runs hourly (~720/month). Either increase the schedule interval in `airflow/dags/orchestrator.py` or upgrade your API plan.

## What's next

This project is a learning prototype. Production deployment would require:
- Custom Docker images (no `_PIP_ADDITIONAL_REQUIREMENTS`)
- Secrets manager (AWS Secrets Manager / HashiCorp Vault)
- Separate metadata DB from analytics DB
- Airflow split into webserver/scheduler/workers (no `standalone`)
- Data quality tests (`dbt test` integrated into the DAG)
- Monitoring & alerting (Datadog / Prometheus + Slack)
- CI/CD pipeline (GitHub Actions)

See `ROADMAP.md` for a more detailed write-up.

## License

MIT — see [LICENSE](./LICENSE).

## Acknowledgments

This project was built following the architecture from [Calvin Yoon's data pipeline tutorial](https://www.youtube.com/watch?v=vMgFadPxOLk) with modifications to use Airflow 3.0 and Superset.