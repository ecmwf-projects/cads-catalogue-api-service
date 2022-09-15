PROJECT := cads_catalogue_api_service
CONDA := conda
CONDAFLAGS :=
COV_REPORT := html
API_ROOT_PATH := http://localhost:8080/api/catalogue/v1/

default: qa unit-tests type-check

qa:
	pre-commit run --all-files

unit-tests:
	python -m pytest -vv --cov=. --cov-report=$(COV_REPORT)

type-check:
	python -m mypy --strict .

conda-env-update:
	$(CONDA) env update $(CONDAFLAGS) -f environment.yml

docker-build:
	docker build -t $(PROJECT) .

docker-run:
	docker run --rm -ti -v $(PWD):/srv $(PROJECT)

template-update:
	pre-commit run --all-files cruft -c .pre-commit-config-weekly.yaml

docs-build:
	cd docs && rm -fr _api && make clean && make html

# DO NOT EDIT ABOVE THIS LINE, ADD COMMANDS BELOW

start:
	uvicorn --reload cads_catalogue_api_service.main:app

integration-tests:
	API_ROOT_PATH=$(API_ROOT_PATH) pytest -vv tests/integration_*.py
