import cads_catalogue.database
import sqlalchemy.orm

OMITTABLE_COLUMNS = [
    cads_catalogue.database.Resource.constraints_data,
    cads_catalogue.database.Resource.form_data,
    cads_catalogue.database.Resource.description,
    cads_catalogue.database.Resource.variables,
    cads_catalogue.database.Resource.lineage,
    cads_catalogue.database.Resource.representative_fraction,
    cads_catalogue.database.Resource.responsible_organisation,
    cads_catalogue.database.Resource.responsible_organisation_role,
    cads_catalogue.database.Resource.responsible_organisation_website,
    cads_catalogue.database.Resource.topic,
    cads_catalogue.database.Resource.type,
    cads_catalogue.database.Resource.unit_measure,
    cads_catalogue.database.Resource.use_limitation,
    cads_catalogue.database.Resource.fulltext,
    cads_catalogue.database.Resource.citation,
    cads_catalogue.database.Resource.contactemail,
    cads_catalogue.database.Resource.ds_contactemail,
    cads_catalogue.database.Resource.ds_responsible_organisation,
    cads_catalogue.database.Resource.ds_responsible_organisation_role,
    cads_catalogue.database.Resource.file_format,
    cads_catalogue.database.Resource.format_version,
    cads_catalogue.database.Resource.adaptor,
    cads_catalogue.database.Resource.adaptor_configuration,
    cads_catalogue.database.Resource.sources_hash,
    cads_catalogue.database.Resource.mapping,
    cads_catalogue.database.Resource.related_resources_keywords,
]

deferred_columns = [sqlalchemy.orm.defer(col) for col in OMITTABLE_COLUMNS]
