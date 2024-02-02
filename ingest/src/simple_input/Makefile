PIP ?= pip3
LAMBDA ?= simple_input
PLATFORM ?= manylinux2014_aarch64
PYTHON_VERSION ?= 3.11

target:
	$(info ${HELP_MESSAGE})
	@exit 0

clean: ##=> Deletes current build environment and latest build
	$(info [*] Who needs all that anyway? Destroying environment....)
	rm -rf ./.pytest_cache ./.venv ./.coverage ./dist
	find . -type d -name "__pycache__" -exec rm -rf {} \;

setup: 
	${PIP} install --user poetry
	poetry self add poetry-plugin-export
	poetry install


shell:
	poetry shell

lint:
	poetry run isort --profile black src tests
	poetry run black --line-length 99 src tests
	poetry run flake8 --max-line-length 99 src tests
	poetry run bandit -r src tests

test:
	poetry run coverage run --source=src --omit=tests -m pytest
	poetry run coverage report --fail-under=98

all: clean setup

build-image:
	docker compose up
	docker compose run builder make build
	docker compose down

build-layer-powertools:
	poetry run pip install --platform ${PLATFORM} --target=dist/layer/powertools/python --implementation cp --python-version ${PYTHON_VERSION} --compile --only-binary=:all: --upgrade "aws-lambda-powertools[aws-sdk, tracer, validation]==2.32.0"
	cd dist/layer/powertools; zip -x "*.pyc" -r ../../aws-lambda-powertools.zip .

build-layer-pydantic:
	poetry run pip install --platform ${PLATFORM} --target=dist/layer/pydantic/python --implementation cp  --python-version ${PYTHON_VERSION} --compile --only-binary=:all: --upgrade "pydantic==2.5.3"
	poetry run pip install --platform ${PLATFORM} --target=dist/layer/pydantic/python --implementation cp --python-version ${PYTHON_VERSION} --compile --only-binary=:all: --upgrade "pydantic-settings==2.1.0"
	cd dist/layer/pydantic; zip -x "*.pyc" -r ../../pydantic.zip .

build-lambda:
	poetry run pip install --platform ${PLATFORM} --target=dist/lambda --implementation cp  --python-version ${PYTHON_VERSION} --compile --only-binary=:all: --upgrade .
	cd dist/lambda; zip -x "*.pyc" -r ../${LAMBDA}.zip .

build-iac:
	mkdir -p dist/module
	cp -r iac/* dist/module
	cp dist/${LAMBDA}.zip dist/module/simple_input
	cp dist/pydantic.zip dist/module/simple_input
	cp dist/aws-lambda-powertools.zip dist/module/simple_input

build: clean build-layer-powertools build-layer-pydantic build-lambda build-iac

docker:
	rm -rf dist
	mkdir dist
	poetry export --with lambda-layer-pydantic --with lambda-layer-powertools -f requirements.txt -o dist/requirements.txt
	rm -rf src/__pycache__
	docker build --tag "simple_input:dev" .
	docker run -d --rm --platform linux/arm64/v8 -e DEFAULT_STORAGE_CLASS="GLACIER" -e DEFAULT_ORCA_BUCKET="orca_archive" -e DEFAULT_MULTIPART_CHUNKSIZE_MB=256 -p 9000:8080  --name simple_input simple_input:dev

openapi:
	cd src; poetry run python -m simple_input.adapter