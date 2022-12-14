# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 University Münster.
#
# Invenio-Dnb-Urn is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

""" InvenioRDM additional metadata output format for OAI DataProvider. """

from flask import current_app
from lxml import etree

from .utils import get_vocabulary_props


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
        "pc": "http://www.d-nb.de/standards/pc/",
        "cc": "http://www.d-nb.de/standards/cc/",
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
        person = etree.SubElement(creator, "{http://www.d-nb.de/standards/pc/}person", nsmap=nsmap)
        mperson = mcreator['person_or_org']
        if 'identifiers' in mperson:
            for midentifier in mperson['identifiers']:
                mscheme = midentifier['scheme']
                if mscheme == "orcid":
                    id = etree.SubElement(person, "{http://www.d-nb.de/standards/ddb/}ORCID")
                    id.text = midentifier['identifier']
                elif mscheme == "gnd":
                    person.attrib['{http://www.d-nb.de/standards/ddb/}GND-Nr'] = midentifier['identifier']
                elif mscheme == "isni":
                    id = etree.SubElement(person, "{http://www.d-nb.de/standards/ddb/}ISNI")
                    id.text = midentifier['identifier']
                elif mscheme == "ror":
                    id = etree.SubElement(person, "{http://www.d-nb.de/standards/ddb/}OtherId")
                    id.text = "(ror)" + midentifier['identifier']
        name = etree.SubElement(person, "{http://www.d-nb.de/standards/pc/}name", nsmap=nsmap)
        if mperson['type'] == 'personal':
            name.attrib['type'] = "nameUsedByThePerson"
            foreName = etree.SubElement(name, "{http://www.d-nb.de/standards/pc/}foreName", nsmap=nsmap)
            foreName.text = mperson['given_name']
            surName = etree.SubElement(name, "{http://www.d-nb.de/standards/pc/}surName", nsmap=nsmap)
            surName.text = mperson['family_name']
            if 'affiliations' in mcreator:
                maffiliation = mcreator['affiliations'][0]
                affiliation = etree.SubElement(person, "{http://www.d-nb.de/standards/pc/}affiliation", nsmap=nsmap)
                institution = etree.SubElement(affiliation,
                                               "{http://www.d-nb.de/standards/cc/}universityOrInstitution",
                                               nsmap=nsmap)
                ccname = etree.SubElement(institution, "{http://www.d-nb.de/standards/cc/}name", nsmap=nsmap)
                ccname.text = maffiliation['name']
        else:
            name.attrib['type'] = "otherName"
            name.attrib['otherNameType'] = "organisation"
            organisationName = etree.SubElement(name, "{http://www.d-nb.de/standards/pc/}organisationName", nsmap=nsmap)
            organisationName.text = mperson['name']
    if 'subjects' in metadata:
        for msubject in metadata['subjects']:
            subject = etree.SubElement(xmetadiss, "{http://purl.org/dc/elements/1.1/}subject", nsmap=nsmap)
            if 'scheme' in msubject:
                if msubject['scheme'] == 'FOS':
                    subject.attrib['{http://www.w3.org/2001/XMLSchema-instance}type'] = "xMetaDiss:noScheme"
                    subject.text = msubject['subject']
                elif 'DDC' in msubject['scheme']:
                    subject.attrib['{http://www.w3.org/2001/XMLSchema-instance}type'] = "dcterms:DDC"
                    id = msubject['id']
                    reversed_id = "".join(reversed(id))
                    last_slash = len(id) - reversed_id.index("/") - 1
                    subject.text = id[last_slash + 1:]
                else:
                    subject.attrib['{http://www.w3.org/2001/XMLSchema-instance}type'] = "xMetaDiss:noScheme"
                    subject.text = msubject['subject']
    mpublisher = metadata['publisher']
    if '/' in mpublisher:
        reversed_mpublisher = "".join(reversed(mpublisher))
        first_slash = mpublisher.index("/")
        last_slash = len(mpublisher) - reversed_mpublisher.index("/") - 1
        sinstitution = mpublisher[:first_slash].rstrip()
        splace = mpublisher[last_slash + 1:].lstrip()
    else:
        sinstitution = mpublisher
        splace = "..."
    publisher = etree.SubElement(xmetadiss, "{http://purl.org/dc/elements/1.1/}publisher", nsmap=nsmap,
                                 attrib={"{http://www.w3.org/2001/XMLSchema-instance}type": "cc:Publisher"})
    institution = etree.SubElement(publisher,
                                   "{http://www.d-nb.de/standards/cc/}universityOrInstitution",
                                   nsmap=nsmap)
    ccname = etree.SubElement(institution, "{http://www.d-nb.de/standards/cc/}name", nsmap=nsmap)
    ccname.text = sinstitution
    ccplace = etree.SubElement(institution, "{http://www.d-nb.de/standards/cc/}place", nsmap=nsmap)
    ccplace.text = splace
    mdate_issued = None
    if 'dates' in metadata:
        for mdate in metadata['dates']:
            if mdate['type']['id'] == 'issued':
                mdate_issued = mdate['date']
    if mdate_issued == None:
        mdate_issued = metadata['publication_date']
    date_issued = etree.SubElement(xmetadiss, "{http://purl.org/dc/terms/}issued", nsmap=nsmap,
                                   attrib={"{http://www.w3.org/2001/XMLSchema-instance}type": "dcterms:W3CDTF"})
    date_issued.text = mdate_issued
    dini_mapping = current_app.config.get("XMETADISS_TYPE_DINI_PUBLTYPE")
    dcterms_mapping = current_app.config.get("XMETADISS_TYPE_DCTERMS_DCMITYPE")
    xmetadiss = add_dctype(xmetadiss, nsmap, metadata, dini_mapping, 'dini:publType')
    xmetadiss = add_dctype(xmetadiss, nsmap, metadata, dcterms_mapping, 'dcterms:DCMIType')

    pids = record['_source']['pids']
    urn = None
    doi = None
    for mpid in pids:
        if 'urn' in mpid:
            urn = pids['urn']['identifier']
        if 'doi' in mpid:
            doi = pids['doi']['identifier']
    if urn is not None:
        dcidentifier = etree.SubElement(
            xmetadiss, "{http://purl.org/dc/elements/1.1/}identifier",
            nsmap=nsmap,
            attrib={'{http://www.w3.org/2001/XMLSchema-instance}type': 'urn:nbn'})
        dcidentifier.text = urn
    elif doi is not None:
        dcidentifier = etree.SubElement(
            xmetadiss, "{http://purl.org/dc/elements/1.1/}identifier",
            nsmap=nsmap,
            attrib={'{http://www.w3.org/2001/XMLSchema-instance}type': 'doi:doi'})
        dcidentifier.text = doi
    #still missing: dcterms:medium
    language = etree.SubElement(
        xmetadiss, "{http://purl.org/dc/elements/1.1/}language",
        nsmap=nsmap,
        attrib={'{http://www.w3.org/2001/XMLSchema-instance}type': 'ddb:titleISO639-2'})
    language.text = lang
    #still missing: ddb:transfer

    if urn is not None and doi is not None:
        ddbidentifier = etree.SubElement(
            xmetadiss, "{http://www.d-nb.de/standards/ddb/}identifier",
            nsmap=nsmap,
            attrib={'{http://www.d-nb.de/standards/ddb/}type': 'DOI'})
        ddbidentifier.text = doi

    if 'identifiers' in metadata:
        for midentifier in metadata['identifiers']:
            identifier = midentifier['identifier']
            scheme = 'other'
            if midentifier['scheme'] == 'url':
                scheme = 'URL'
            elif midentifier['scheme'] == 'urn':
                scheme = 'URN'
            elif midentifier['scheme'] == 'doi':
                scheme = 'DOI'
            elif midentifier['scheme'] == 'handle':
                scheme = 'handle'
            elif midentifier['scheme'] == 'isbn':
                scheme = 'ISBN'
            ddbidentifier = etree.SubElement(
                xmetadiss, "{http://www.d-nb.de/standards/ddb/}identifier",
                nsmap=nsmap,
                attrib={'{http://www.d-nb.de/standards/ddb/}type': scheme})
            ddbidentifier.text = identifier

    maccess = record['_source']['access']
    kind = 'free'
    if maccess['files'] == 'restricted':
        kind = 'domain'
    ddbrights = etree.SubElement(
        xmetadiss, "{http://www.d-nb.de/standards/ddb/}rights",
        nsmap=nsmap,
        attrib={'{http://www.d-nb.de/standards/ddb/}kind': kind})
    if 'rights' in metadata:
        for mright in metadata['rights']:
            access = etree.SubElement(
                xmetadiss,
                "{http://www.d-nb.de/standards/ddb/}licence",
                nsmap=nsmap,
                attrib={'{http://www.d-nb.de/standards/ddb/}licenceType': 'access'})
            access.text = 'OA'
            if 'cc' in mright['id']:
                cc = etree.SubElement(
                    xmetadiss,
                    "{http://www.d-nb.de/standards/ddb/}licence",
                    nsmap=nsmap,
                    attrib={'{http://www.d-nb.de/standards/ddb/}licenceType': 'cc'})
                cc.text = mright['id']
            else:
                other_scheme = etree.SubElement(
                    xmetadiss,
                    "{http://www.d-nb.de/standards/ddb/}licence",
                    nsmap=nsmap,
                    attrib={'{http://www.d-nb.de/standards/ddb/}licenceType': 'noScheme'})
                if 'de' in mright['title']:
                    other_scheme.text = mright['title']['de']
                else:
                    other_scheme.text = mright['title']['en']
            lic_url = etree.SubElement(
                    xmetadiss,
                    "{http://www.d-nb.de/standards/ddb/}licence",
                    nsmap=nsmap,
                    attrib={'{http://www.d-nb.de/standards/ddb/}licenceType': 'URL'})
            lic_url.text = mright['props']['url']
    else:
        access = etree.SubElement(
            xmetadiss,
            "{http://www.d-nb.de/standards/ddb/}licence",
            nsmap=nsmap,
            attrib={'{http://www.d-nb.de/standards/ddb/}licenceType': 'access'})
        access.text = 'nOA'
        other_scheme = etree.SubElement(
            xmetadiss,
            "{http://www.d-nb.de/standards/ddb/}licence",
            nsmap=nsmap,
            attrib={'{http://www.d-nb.de/standards/ddb/}licenceType': 'otherScheme'})
        other_scheme.text = 'Keine Angabe'
        lic_url = etree.SubElement(
            xmetadiss,
            "{http://www.d-nb.de/standards/ddb/}licence",
            nsmap=nsmap,
            attrib={'{http://www.d-nb.de/standards/ddb/}licenceType': 'URL'})
        lic_url.text = 'Keine Angabe'

    print(record)

    return xmetadiss


def add_dctype(parent, nsmap, metadata, mapping, type):
    props = get_vocabulary_props(
        "resourcetypes",
        [
            "props." + mapping,
        ],
        metadata["resource_type"]["id"],
    )
    dctype = etree.SubElement(
        parent, "{http://purl.org/dc/elements/1.1/}type",
        nsmap=nsmap,
        attrib={'{http://www.w3.org/2001/XMLSchema-instance}type': type})
    mapped_type = props.get(mapping)
    dctype.text = mapped_type
    return parent
