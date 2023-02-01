# -*- coding: utf-8 -*-
#
# Copyright (C) 2022, 2023 University of Münster.
#
# Invenio-Dnb-Urn is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Views."""

from flask import Blueprint

blueprint = Blueprint("invenio_dnb_urn_ext", __name__)


@blueprint.record_once
def init(state):
    """Init app."""
    app = state.app
    # Register services - cannot be done in extension because
    # Invenio-Records-Resources might not have been initialized.
    sregistry = app.extensions["invenio-records-resources"].registry
    ext = app.extensions["invenio-dnb-urn"]
    sregistry.register(ext.oaipmh_server_service, service_id="oaipmh-server")
    # Register indexers
    iregistry = app.extensions["invenio-indexer"].registry
    iregistry.register(ext.records_service.indexer, indexer_id="records")


def create_oaipmh_server_blueprint_from_app(app):
    """Create app blueprint."""
    return app.extensions["invenio-dnb-urn"].oaipmh_server_resource.as_blueprint()
