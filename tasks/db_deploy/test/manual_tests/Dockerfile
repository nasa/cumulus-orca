FROM postgres:10.14 AS mypgbuild

# Build the aws_s3 extension
RUN apt-get update \
 && apt-get install -y git make \
 && git clone https://github.com/chimpler/postgres-aws-s3.git \
 && cd postgres-aws-s3 \
 && make install


FROM postgres:10.14

# Add the plpython3u extension
RUN apt-get update \
 && apt-get install -y postgresql-plpython3-10

# Copy the aws_s3 extension
COPY --from=mypgbuild /usr/share/postgresql/10/extension/aws_s3.control /usr/share/postgresql/10/extension/
COPY --from=mypgbuild /usr/share/postgresql/10/extension/aws_s3--0.0.1.sql /usr/share/postgresql/10/extension/

# Copy the init script
COPY init-plpython3u-db.sh /docker-entrypoint-initdb.d/
