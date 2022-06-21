FROM continuumio/miniconda3

COPY . /src/cads-catalogue-api-service
COPY ../cads-catalogue /src/cads-catalogue

WORKDIR /src/cads-catalogue-api-service

RUN conda install -c conda-forge make gcc python=3.10 \
    && make conda-env-update CONDAFLAGS="-n base"

RUN pip install --no-deps -e ../cads-catalogue \
    && pip install --no-deps -e .

ENV APP_HOST=0.0.0.0
ENV APP_PORT=8082

CMD uvicorn cads_catalogue_api_service.main:app --host ${APP_HOST} --port ${APP_PORT} --log-level info
