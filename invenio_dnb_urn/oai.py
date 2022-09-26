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
        "xMetaDiss": "http://www.d-nb.de/standards/xmetadissplus/",
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

    return epicur

def xmetadiss_etree(pid, record):
    """OAI Epicur XML format for OAI-PMH.

    It assumes that record is a search result.
    """
    nsmap = {
        "xMetaDiss": "http://www.d-nb.de/standards/xmetadissplus/",
        "dc": "http://purl.org/dc/elements/1.1/",
        "dcterms": "http://purl.org/dc/terms/",
        "ddb": "http://www.d-nb.de/standards/ddb/",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    }

    attribs = {
        f"{{{nsmap['xsi']}}}schemaLocation": (
            "http://www.d-nb.de/standards/xmetadissplus/ "
            "http://www.d-nb.de/standards/xmetadissplus/xmetadissplus.xsd"
        ),
    }

    metadata = record['_source']['metadata']
    # prepare the structure required by the 'xMetaDissPlus' metadataPrefix
    xmetadiss = etree.Element("{http://www.d-nb.de/standards/xmetadissplus/}xMetaDiss", nsmap=nsmap, attrib=attribs)
    lang = metadata['languages'][0]['id']
    if lang == "deu":
        lang = "ger"
    title = etree.SubElement(
        xmetadiss, "{http://purl.org/dc/elements/1.1/}title",
        nsmap=nsmap,
        attrib={'lang': lang, '{http://www.w3.org/2001/XMLSchema-instance}type': 'ddb:titleISO639-2'})
    title.text = metadata['title']
    if 'additional_titles' in metadata:
        for additionaltitle in metadata['additional_titles']:
            lang = additionaltitle['lang']['id']
            if lang == "deu":
                lang = "ger"
            if additionaltitle['type']['id'] == 'translated-title' or additionaltitle['type']['id'] == 'subtitle':
                alternativetitle = etree.SubElement(
                    xmetadiss, "{http://purl.org/dc/terms/}alternative",
                    nsmap=nsmap,
                    attrib={'{http://www.w3.org/2001/XMLSchema-instance}type': 'ddb:talternativeISO639-2',
                            'lang': lang})
                if additionaltitle['type']['id'] == 'translated-title':
                    alternativetitle.attrib['{http://www.d-nb.de/standards/ddb/}type'] = 'translated'
                alternativetitle.text = additionaltitle['title']
    for mcreator in metadata['creators']:
        creator = etree.SubElement(xmetadiss, "{http://purl.org/dc/elements/1.1/}creator",
        nsmap=nsmap,
        attrib={'{http://www.w3.org/2001/XMLSchema-instance}type': 'pc:MetaPers'})
        print(creator)
#        print(a_title['type'])

    return xmetadiss
