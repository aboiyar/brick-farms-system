FROM timescale/timescaledb:latest-pg14

# Install PostGIS packages so the container supports both TimescaleDB and PostGIS
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       postgis postgresql-14-postgis-3 \
    && rm -rf /var/lib/apt/lists/*

USER postgres
