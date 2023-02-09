```
    Copyright (C) 2022 University of Münster.


    Invenio-DNB-Urn is free software; you can redistribute it and/or
    modify it under the terms of the MIT License; see LICENSE file for more
    details.
```

# Invenio-DNB-Urn

DNB support module for InvenioRDM. It offers a URN PIDProvider and additional metadata formats to be included
in the OAI-PMH server. Currently these are epicur and xMetaDissPlus.
In a later step the epicur format will be replaced by extending the URN PIDProvider by accessing the
DNB REST-API's to directly mint new and changed URN's.

## Configuration

Add the following to invenio.cfg:

```python
import idutils
from invenio_dnb_urn import provider
from invenio_rdm_records.services.pids import providers

OAISERVER_METADATA_FORMATS = {
  "oai_dc": {
    "serializer": "invenio_rdm_records.oai:dublincore_etree",
    "schema": "http://www.openarchives.org/OAI/2.0/oai_dc.xsd",
    "namespace": "http://www.openarchives.org/OAI/2.0/oai_dc/"
  },
  "datacite": {
    "serializer": "invenio_rdm_records.oai:datacite_etree",
    "schema": "http://schema.datacite.org/meta/nonexistant/nonexistant.xsd",
    "namespace": "http://datacite.org/schema/nonexistant"
  },
  "oai_datacite": {
    "serializer": "invenio_rdm_records.oai:oai_datacite_etree",
    "schema": "http://schema.datacite.org/oai/oai-1.1/oai.xsd",
    "namespace": "http://schema.datacite.org/oai/oai-1.1/"
  },
  "xMetaDiss": {
    "serializer": "invenio_dnb_urn.oai:xmetadiss_etree",
    "schema": "http://www.d-nb.de/standards/xmetadissplus/xmetadissplus.xsd",
    "namespace": "http://www.d-nb.de/standards/xmetadissplus/"
  },
}

URN_DNB_ID_PREFIX = "urn:nbn:de:hbz:6-"
EPICUR_NBN_SCHEME = "urn:nbn:de"
XMETADISS_TYPE_DINI_PUBLTYPE = "openaire_type"
XMETADISS_TYPE_DCTERMS_DCMITYPE = "openaire_type"

#
# Persistent identifiers configuration
#
RDM_PERSISTENT_IDENTIFIER_PROVIDERS = [
  # DataCite DOI provider
  providers.DataCitePIDProvider(
    "datacite",
    client=providers.DataCiteClient("datacite", config_prefix="DATACITE"),
    label=_("DOI"),
  ),
  # DOI provider for externally managed DOIs
  providers.ExternalPIDProvider(
    "external",
    "doi",
    validators=[providers.BlockedPrefixes(config_names=["DATACITE_PREFIX"])],
    label=_("DOI"),
  ),
  # OAI identifier
  providers.OAIPIDProvider(
    "oai",
    label=_("OAI ID"),
  ),
  # URN identifier
  provider.DnbUrnProvider(
    "urn",
    client=provider.DNBUrnClient("dnb"),
    label=_("URN"),
  ),
]
"""A list of configured persistent identifier providers.
ATTENTION: All providers (and clients) takes a name as the first parameter.
This name is stored in the database and used in the REST API in order to
identify the given provider and client.
The name is further used to configure the desired persistent identifiers (see
'RDM_PERSISTENT_IDENTIFIERS' below)
"""

RDM_PERSISTENT_IDENTIFIERS = {
  # DOI automatically removed if DATACITE_ENABLED is False.
  "doi": {
    "providers": ["datacite", "external"],
    "required": True,
    "label": _("DOI"),
    "validator": idutils.is_doi,
    "normalizer": idutils.normalize_doi,
  },
  "oai": {
    "providers": ["oai"],
    "required": True,
    "label": _("OAI"),
  },
  "urn": {
    "providers": ["urn"],
    "required": True,
    "label": _("URN"),
  },
}
```

In order to fully implement xMetaDissPlus with  all mandatory fields, the metadata definition has to be expanded by custom
fields. At first add the file thesis_types.yaml to /app_data/vocabularies, then add

```yaml
thesis:
  pid-type: ths
  data-file: vocabularies/thesis_types.yaml
```

to the vocabularies.yaml. Next, add

```python
from invenio_records_resources.services.custom_fields import TextCF
from invenio_vocabularies.services.custom_fields import VocabularyCF

RDM_NAMESPACES = {
  # DNB Thesis
  "thesis": "https://dnb.de/thesis/",
}

RDM_CUSTOM_FIELDS = {
  VocabularyCF(
    name="thesis:level",
    vocabulary_id="thesis",
    dump_options=True,
    multiple=False,
  ),
  TextCF(
    name="thesis:organisation",
  ),
  TextCF(
    name="thesis:place",
  ),
}

RDM_CUSTOM_FIELDS_UI = [
  {
    "section": _("Hochschulschriftenvermerk"),
    "fields": [
      dict(
        field="thesis:level",
        ui_widget="Dropdown",
        props=dict(
          label="Abschluss",
          placeholder="Grad des Abschlusses",
          icon="pencil",
          description="You should fill this field with the thesis degree",
          search=True,  # True for autocomplete dropdowns with search functionality
          multiple=False,   # True for selecting multiple values
          clearable=True,
          required=False,
        )
      ),
      dict(
        field="thesis:organisation",
        ui_widget="Input",
        props=dict(
          label="Hochschule",
          placeholder="Verleihende Hochschule",
          icon="pencil",
          description="You should fill this field with the institution that awards the degree",
          required=False,
        )
      ),
      dict(
        field="thesis:place",
        ui_widget="Input",
        props=dict(
          label="Ort",
          placeholder="Ort",
          icon="pencil",
          description="Place of the university/institution.",
          required=False,
        )
      ),
    ]
  }
]
```

to your invenio.cfg and execute

```commandline
pipenv run invenio rdm-records custom-fields init
```
