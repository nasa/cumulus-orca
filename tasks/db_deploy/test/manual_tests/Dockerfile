FROM postgres:13.11 AS mypgbuild

# Build the aws_s3 extension
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    git=1:2.* \
    make=4.* \
    ca-certificates=2023* \
 && git clone https://github.com/chimpler/postgres-aws-s3.git \
 && cd /postgres-aws-s3 \
 && make install \
 && rm -rf /var/lib/apt/lists/*



FROM postgres:13.11

# Add the plpython3u extension
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    postgresql-plpython3-13=13.* \
 && rm -rf /var/lib/apt/lists/*

# Copy the aws_s3 extension
COPY --from=mypgbuild ["/usr/share/postgresql/13/extension/aws_s3.control", "/usr/share/postgresql/13/extension/aws_s3--0.0.1.sql", "/usr/share/postgresql/13/extension/"]

# Copy the init script
COPY init-plpython3u-db.sh /docker-entrypoint-initdb.d/
COPY postgres-healthcheck.sh /

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD /postgres-healthcheck.sh || exit 1