FROM condaforge/miniforge3:23.11.0-0

ARG MODE=stable
ARG CADS_PAT

WORKDIR /src

COPY ./git-*-repos.py /src/

COPY environment.${MODE} /src/environment
COPY environment-common.yml /src/environment-common.yml
COPY . /src/cads-catalogue-api-service/

RUN conda install -y -n base -c conda-forge gitpython typer conda-merge

SHELL ["/bin/bash", "-c"]

RUN set -a && source environment \
    && python ./git-clone-repos.py --default-branch \
    cads-catalogue \
    cads-common \
    cads-e2e-tests 

# remove CADS_PAT
RUN export CADS_PAT=''

RUN conda run -n base conda-merge \
    /src/environment-common.yml \
    /src/cads-catalogue/environment.yml \
    /src/cads-catalogue-api-service/environment.yml \
    /src/cads-common/environment.yml \
    /src/cads-e2e-tests/environment.yml \
    > /src/combined-environment.yml \
    && conda env update -n base -f /src/combined-environment.yml \
    && conda clean -afy

RUN conda run -n base pip install --no-deps \
    -e /src/cads-catalogue \
    -e /src/cads-catalogue-api-service \
    -e /src/cads-common \
    -e /src/cads-e2e-tests

CMD cads-catalogue init-db && uvicorn cads_catalogue_api_service.main:app --host 0.0.0.0 --proxy-headers
