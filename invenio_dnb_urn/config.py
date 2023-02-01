# -*- coding: utf-8 -*-
#
# Copyright (C) 2022, 2023 University of Münster.
#
# Invenio-Dnb-Urn is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Epicur-based data model for Invenio."""

EPICUR_NBN_SCHEME = "urn:nbn:de"

"""URN-PIDStore configuration used by the DnbUrnProvider."""
URN_DNB_ENABLED = False
"""Flag to enable/disable URN registration to DNB."""

URN_DNB_USERNAME = ""
"""DNB username."""

URN_DNB_PASSWORD = ""
"""DNB password."""

URN_DNB_ID_PREFIX = ""
"""Provide a URN prefix here."""

URN_DNB_TEST_MODE = True
"""DNB test mode enabled."""

URN_DNB_FORMAT = "{prefix}-{id}"
"""A string used for formatting the URN."""

XMETADISS_TYPE_DINI_PUBLTYPE = "openaire_type"
XMETADISS_TYPE_DCTERMS_DCMITYPE = "openaire_type"
