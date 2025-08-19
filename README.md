# cads-catalogue-api-service

STAC based API service for the Climate & Atmosphere Data Store

## Running the API

```bash
catalogue_db_password=… \
    uvicorn cads_catalogue_api_service.main:app --host 0.0.0.0 --proxy-headers --forwarded-allow-ips "*" --log-level info --reload
```

## REST API description

Let say that WSGI service root is configured to serve the API at `http://localhost:8080/api/catalogue`.

The Swagger/OpenAPI documentation can be accessed at <http://localhost:8080/api/catalogue/api.html>.

To access the list of all datasets (STAC collections index):

```bash
curl http://localhost:8080/api/catalogue/collections | jq
```

To access a dataset by id (STAC collection):

```bash
curl http://localhost:8080/api/catalogue/collections/reanalysis-era5-land-monthly-means | jq
```

To obtain the thumbnail image of a dataset:

```bash
curl http://localhost:8080/api/catalogue/collections/reanalysis-era5-land-monthly-means | jq -r .assets.thumbnail.href
```

### Links

Many related information are obtained using hypermedia-like resources (as defined by the OGC standard itself). \
Every dataset provides a `links` array.

**Licenses** are provided using links with `rel="license"` (the first license is also found in the `license` field), as defined by the STAC Collection.

**Documentation** are provided using links with `rel=describedby"`. \
Only title and URL are provided for now.

**Form** is a single link with `rel=form"`.

**Constraints** is a single link with `rel=constraints"`.

## Workflow for developers/contributors

For best experience create a new conda environment (e.g. DEVELOP) with Python 3.12:

```bash
conda create -n DEVELOP -c conda-forge python=3.12
conda activate DEVELOP
```

Before pushing to GitHub, run the following commands:

1. Update conda environment: `make conda-env-update`
1. Install this package: `pip install -e . --no-deps`
1. Sync with the latest [template](https://github.com/ecmwf-projects/cookiecutter-conda-package) (optional): `make template-update`
1. Run quality assurance checks: `make qa`
1. Run tests: `make unit-tests`
1. Run the static type checker: `make type-check`
1. Build the documentation (see [Sphinx tutorial](https://www.sphinx-doc.org/en/master/tutorial/)): `make docs-build`

## License

```plain
Copyright 2022, European Union.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
