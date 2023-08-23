FROM postgres:13.11 AS mypgbuild

# Build the aws_s3 extension
RUN apt-get update \
 && apt-get install -y git make \
 && git clone https://github.com/chimpler/postgres-aws-s3.git \
 && cd postgres-aws-s3 \
 && make install


FROM postgres:13.11

# Add the plpython3u extension
RUN apt-get update \
 && apt-get install -y postgresql-plpython3-13

# Copy the aws_s3 extension
COPY --from=mypgbuild /usr/share/postgresql/13/extension/aws_s3.control /usr/share/postgresql/13/extension/
COPY --from=mypgbuild /usr/share/postgresql/13/extension/aws_s3--0.0.1.sql /usr/share/postgresql/13/extension/

# Copy the init script
COPY init-plpython3u-db.sh /docker-entrypoint-initdb.d/
