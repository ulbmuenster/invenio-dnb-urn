# -*- coding: utf-8 -*-
#
# Copyright (C) 2022, 2023 University of Münster.
#
# Invenio-Dnb-Urn is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""xMetaDissPlus-based data model for Invenio."""

from invenio_rdm_records.oaiserver.resources.config import OAIPMHServerResourceConfig
from invenio_rdm_records.oaiserver.resources.resources import OAIPMHServerResource
from invenio_rdm_records.oaiserver.services.config import OAIPMHServerServiceConfig
from invenio_rdm_records.oaiserver.services.services import OAIPMHServerService


class InvenioSerializerXMetaDissPlus(object):
    """Invenio-Serializer-xMetaDiss extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.init_config(app)
        self.init_services(app)
        self.init_resource(app)
        app.extensions["invenio_dnb_urn"] = self

    def init_config(self, app):
        """Initialize configuration."""

    def init_config(self, app):
        """Initialize configuration."""

    def service_configs(self, app):
        """Customized service configs."""

        class ServiceConfigs:
            oaipmh_server = OAIPMHServerServiceConfig

        return ServiceConfigs

    def init_services(self, app):
        """Initialize services"""
        service_configs = self.service_configs(app)

        self.oaipmh_server_service = OAIPMHServerService(
            config=service_configs.oaipmh_server,
        )

    def init_resource(self, app):
        """Initialize resources"""

        # OAI-PMH
        self.oaipmh_server_resource = OAIPMHServerResource(
            service=self.oaipmh_server_service,
            config=OAIPMHServerResourceConfig,
        )
