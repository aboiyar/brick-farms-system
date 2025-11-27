FROM postgis/postgis:14-3.4

# Build on top of the PostGIS image and install TimescaleDB packages so the
# resulting image supports both PostGIS and TimescaleDB extensions required by
# the migrations.
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl gnupg lsb-release ca-certificates \
    && curl -sSL https://packagecloud.io/install/repositories/timescale/timescaledb/script.deb.sh | bash \
    && apt-get update \
    && apt-get install -y --no-install-recommends timescaledb-postgresql-14 \
    && rm -rf /var/lib/apt/lists/*

USER postgres
