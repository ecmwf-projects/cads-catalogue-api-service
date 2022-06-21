FROM continuumio/miniconda3

WORKDIR /src/cads-catalogue-api-service

COPY environment.yml /src/cads-catalogue-api-service

RUN conda install -c conda-forge python=3.10 \
    && conda env update -n base -f environment.yml

COPY . /src/cads-catalogue-api-service

RUN pip install --no-deps -e .

ENV PORT=8000
ENV LOGLEVEL=info

CMD uvicorn --host 0.0.0.0 --port ${PORT} --log-level ${LOGLEVEL} cads_catalogue_api_service.main:app
