# Build Stage
# =============================================================================
FROM python:3.9-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Keep key consistent with value in uvicorn_settings.py
ENV PORT 5000

# Install psycopg2 requirements
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libpq-dev
# Copy external dependencies
COPY shared_libraries shared_libraries
# Install python app requirements
COPY requirements.txt graphql/requirements.txt
WORKDIR graphql
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org


# Final Stage
# =============================================================================
FROM python:3.9-slim

# Set metadata information
ARG VERSION_NUMBER="test"
LABEL application.name="ORCA-GraphQL" \
    application.description="GraphQL server for ORCA application." \
    application.team="ORCA" \
    application.version=${VERSION_NUMBER}

# CREATE Non-Privileged User
RUN groupadd -r appuser \
    && useradd -r -s /bin/false -m -d /app -g appuser appuser

# Install curl for healthcheck
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 curl

# Copy compiled wheels and install the requirements
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Set the work directory for our application
WORKDIR /app

# Copy our application source files
COPY src/ ./src

# Set the User that the app will run as
USER appuser

# Expose the port for our application
EXPOSE $PORT

# Setup our health check
# TODO: This is a dead simple example where we just check for no error
#       ideally we should
HEALTHCHECK --interval=60s --timeout=5s --start-period=30s --retries=3 \
    CMD curl --fail http://localhost:${PORT}/healthz || exit 1

# Set PYTHONPATH to set the working directory to the root folder instead of the location of main.py
ENV PYTHONPATH="/app:$PYTHONPATH"
# Set the entry point for the container
# CMD ["python", "src/adapters/webserver/main.py"]
ENTRYPOINT ["python", "src/adapters/webserver/main.py"]
