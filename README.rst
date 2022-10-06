..
    Copyright (C) 2022 University of Münster.


    Invenio-DNB-Urn is free software; you can redistribute it and/or
    modify it under the terms of the MIT License; see LICENSE file for more
    details.

===============
Invenio-DNB-Urn
===============

DNB support module for InvenioRDM. It offers a URN PIDProvider and additional metadata formats to be included
in the OAI-PMH server. Currently these are epicur and xMetaDissPlus.
In a later step the epicur format will be replaced by extending the URN PIDProvider by accessing the
DNB REST-API's to directly mint new and changed URN's.

Configuration
=============

Add the following to invenio.cfg:

.. code-block:: python

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
      "epicur": {
  	    "serializer": "invenio_dnb_urn.oai:epicur_etree",
    	"schema": "http://nbn-resolving.de/urn:nbn:de:1111-2004033116",
    	"namespace": "urn:nbn:de:1111-2004033116"
      },
      "xMetaDiss": {
  	    "serializer": "invenio_dnb_urn.oai:xmetadiss_etree",
    	"schema": "http://www.d-nb.de/standards/xmetadissplus/xmetadissplus.xsd",
    	"namespace": "http://www.d-nb.de/standards/xmetadissplus/"
      },
    }

    URN_DNB_ID_PREFIX = "de:hbz:6-"
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
            label=_("URN"),
        ),
    ]
    """A list of configured persistent identifier providers.
    ATTENTION: All providers (and clients) takes a name as the first parameter.
    This name is stored in the database and used in the REST API in order to
    identify the given provider and client.
    The name is further used to configure the desired persistent identifiers (see
    ``RDM_PERSISTENT_IDENTIFIERS`` below)
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
