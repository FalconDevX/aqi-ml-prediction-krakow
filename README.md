# AirCast - Krakow Air Quality Forecasting

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-REST_API-brightgreen)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Storage-blueviolet)
![Docker](https://img.shields.io/badge/Docker-Supported-blue)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-lightgrey)
![Docker Compose](https://img.shields.io/badge/Docker%20Compose-Enabled-brightgreen)
![API Docs](https://img.shields.io/badge/OpenAPI-Swagger-1ea7fd)
![Status](https://img.shields.io/badge/Status-Prototype-orange)

AirCast is a project aimed at forecasting air quality (AQI and selected pollutants) for Krakow using historical measurements and near real-time data.

This repository focuses on the backend part:
1. collecting data from external sources (KaggleHub dataset, Airly API),
2. storing configuration and database connectivity (PostgreSQL via SQLAlchemy),
3. exposing a small REST API (FastAPI).

The ML models (LSTM/RNN forecasting) and the full UI dashboard are described in the project materials, but the training/forecasting implementation files are not included in this repository state.

## Table of Contents
1. Goals
2. Milestones
3. Architecture
4. Data Sources
5. API
6. Configuration
7. Data Jobs
8. Docker
9. PostgreSQL Schema (Reference)
10. Known Issues

## Goals

- Train an AI model that predicts changes in air quality in Krakow based on historical measurements and current station context.
- Provide a web interface for visualization (map-based dashboard, station-level views) and future forecasts, planned with Next.js and TypeScript.
- Build an AIoT station concept (Raspberry Pi + sensors) that can send locally measured data to the backend.

## Milestones

The project follows the milestone plan from the course materials:

1. Define project goals, scope, and required resources.
2. Prepare the training dataset (collection, cleaning, normalization/transformations).
3. Choose and implement the AI model and train it.
4. Evaluate results and optimize the model (metrics, hyperparameters, feature quality).
5. Deploy the model and integrate it with the environment (production integration and monitoring).

## Architecture

Backend components in this repo:

- FastAPI app (`app/main.py`)
  - mounts API routers from `app/api/`.
  - registers error handling for external API failures.
- API router layer (`app/api/router.py`, `app/api/stations.py`)
  - exposes endpoints under `/stations`.
- Data ingestion and external API integration
  - KaggleHub dataset downloader and CSV extractor (`app/jobs/get_data_from_dataset.py`).
  - Airly API integration and station data collection (`app/services/airly_service.py` and `app/jobs/airly_data_gather.py`).
- Database connectivity
  - SQLAlchemy engine/session factory (`app/db/session.py`).

## Data Sources

- KaggleHub dataset: `wisekinder/poland-air-quality-monitoring-dataset-2017-2023`
  - Extracted per year and per pollutant into `data/{year}/{year}_{param}.csv`.
  - Implemented in `app/jobs/get_data_from_dataset.py`.
- Airly API
  - Used to fetch current and history data for Airly stations within Krakow.
  - Current station list is generated via `app/jobs/airly_data_gather.py`.
  - Current + history collection is implemented in `app/services/airly_service.py`.

### Legacy utilities (folder `old/`)

The `old/` folder contains experimental or course-provided scripts for alternative data sources, including:
- GIOS station metadata and historical data utilities (see `old/gios_*`).
- AQICN feed client example (see `old/aqi_cn_downloader.py`).

## API

Base application:
- `GET /stations/current/{station_id}`

Note: this endpoint currently imports `get_current_data_from_station` from `app.services.airly_service`, but only `get_current_and_history_data_from_station` is present in the service file.
See the "Known Issues" section below.

## Configuration

### Environment variables

The backend expects a dotenv file at `app/.env`.

Required values (see `app/config.py` and `app/.env`):
- `TOKEN` (for WAQI API base, used by configuration)
- `AIRLY_API_KEY`
- `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`

### Example: where DB connectivity is read from

- SQLAlchemy URL is constructed from `DB_*` variables in `app/config.py`.
- `app/db/session.py` uses that URL to create the engine and session factory.

## Data Jobs

Run from the repository root.

### Kaggle dataset download + extraction

Command:
```bash
python app/jobs/get_data_from_dataset.py
```

What it does:
- Downloads the KaggleHub dataset (caches under `data_from_kaggle/`).
- Extracts CSV files to `data/{year}/{year}_{param}.csv` for:
  - years: `2017..2023`
  - params: `SO2`, `NO2`, `CO`, `O3`, `PM10`, `PM25`

### Airly station list (Krakow)

Command:
```bash
python app/jobs/airly_data_gather.py
```

What it does:
- Queries Airly "nearest installations" around Krakow.
- Filters results to `Krakow`.
- Saves an Airly station list JSON file (see `app/utils.py` helper).

### Airly current + history collection

Command:
```bash
python app/services/airly_service.py
```

What it does:
- Fetches Airly CAQI current and history for all known station IDs.
- Writes JSONL files:
  - `stations_current_data.jsonl`
  - `stations_hisotry_data.jsonl`

Output paths depend on your current working directory.
For consistent results, run from the repository root and keep files under `data/` if you plan DB ingestion.

## Docker

### Build & run (API)

Build image and start the API service:
```bash
docker compose up --build
```

Notes:
- The container runs `uvicorn app.main:app` and uses `--env-file ./app/.env`.
- `docker-compose.yml` expects an external Docker network named `aqi-network`.
- `docker-compose.yml` does not define the PostgreSQL service itself; it assumes a reachable container named `aqi-postgres` (see `DATABASE_URL` in the compose file).

If you do not have the network yet:
```bash
docker network create aqi-network
```

## PostgreSQL Schema (Reference)

The project materials describe two tables:
- `stations`
- `measurements`

Reference schema (adjust types as needed):
```sql
CREATE TABLE stations (
  id INTEGER PRIMARY KEY,
  name TEXT
);

CREATE TABLE measurements (
  id SERIAL PRIMARY KEY,
  station_id INTEGER REFERENCES stations(id),
  date_of TIMESTAMP,
  PM10 DOUBLE PRECISION,
  PM2_5 DOUBLE PRECISION,
  CO DOUBLE PRECISION,
  AQI DOUBLE PRECISION
);
```

This repository state does not include migrations or ORM models for these tables, but `app/db/session.py` provides the database connectivity layer.

## Known Issues

- `GET /stations/current/{station_id}` endpoint:
  - `app/api/stations.py` imports `get_current_data_from_station`, but `app/services/airly_service.py` only defines `get_current_and_history_data_from_station`.
  - Suggested fix: add a thin wrapper function `get_current_data_from_station` that calls `get_current_and_history_data_from_station` and returns only the `current` part.

