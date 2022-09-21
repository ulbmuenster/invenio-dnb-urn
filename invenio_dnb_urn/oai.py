# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 University Münster.
#
# Invenio-Dnb-Urn is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

""" InvenioRDM additional metadata output format for OAI DataProvider. """

from flask import current_app
from lxml import etree


def epicur_etree(pid, record):
    """OAI Epicur XML format for OAI-PMH.

    It assumes that record is a search result.
    """
    nsmap = {
        None: "urn:nbn:de:1111-2004033116",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    }

    attribs = {
        f"{{{nsmap['xsi']}}}schemaLocation": (
            "urn:nbn:de:1111-2004033116 "
            "http://nbn-resolving.de/urn:nbn:de:1111-2004033116"
        ),
    }

    urnscheme = {
        "scheme": "irrelevant"
    }

    urlscheme = {
        "scheme": "url",
        "role": "primary"
    }

    # prepare the structure required by the 'epicur' metadataPrefix
    epicur = etree.Element("epicur", nsmap=nsmap, attrib=attribs)
    admindata = etree.SubElement(epicur, "administrative_data", nsmap=nsmap, attrib=None)
    delivery = etree.SubElement(admindata, "delivery", nsmap=nsmap, attrib=None)
    update_status = etree.SubElement(delivery, "update_status", nsmap=nsmap, attrib={'type': 'urn_new'})
    epicur_record = etree.SubElement(epicur, "record", nsmap=nsmap, attrib=None)
    urnscheme['scheme'] = current_app.config.get("EPICUR_NBN_SCHEME")
    identifier_urn = etree.SubElement(epicur_record, "identifier", nsmap=nsmap, attrib=urnscheme)
    identifier_urn.text = "Test"
    resource = etree.SubElement(epicur_record, "resource", nsmap=nsmap, attrib=None)
    identifier_url = etree.SubElement(resource, "identifier", nsmap=nsmap, attrib=urlscheme)
    url_format = etree.SubElement(resource, "format", nsmap=nsmap, attrib={'scheme': 'imt'})
    url_format.text = "text/html"
    identifier_url.text = current_app.config.get("SITE_UI_URL") + "/records/" + record['_source']['id']

    # print(record['_source']['metadata']['identifiers'])
    return epicur
