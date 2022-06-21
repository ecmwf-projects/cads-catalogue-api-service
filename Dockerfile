FROM continuumio/miniconda3


WORKDIR /src/cads-catalogue-api-service

COPY environment.yml /src/cads-catalogue-api-service

RUN conda install -c conda-forge python=3.10 \
    && conda env update -n base -f environment.yml

COPY . /src/cads-catalogue-api-service

RUN pip install --no-deps -e .

ENV APP_HOST=0.0.0.0
ENV APP_PORT=8082

CMD uvicorn cads_catalogue_api_service.main:app --host ${APP_HOST} --port ${APP_PORT} --log-level info
