# Build Stage
# =============================================================================
FROM python:3.9-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install python app requirements
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt


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
EXPOSE 5000

# Setup our health check
# TODO: This is a dead simple example where we just check for no error
#       ideally we should
HEALTHCHECK --interval=60s --timeout=5s --start-period=30s --retries=3 \
    CMD curl --fail http://localhost:5000/healthz || exit 1

# Set PYTHONPATH to set the working directory to the root folder instead of the location of main.py
ENV PYTHONPATH="/app:$PYTHONPATH"
# Set the entry point for the container
# CMD ["python", "src/main.py"]
ENTRYPOINT ["python", "src/main.py"]
