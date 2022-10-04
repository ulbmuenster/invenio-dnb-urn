# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 University of Münster.
#
# Invenio-Dnb-Urn is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

from flask import current_app
from invenio_pidstore.models import PIDStatus
from invenio_rdm_records.services.pids.providers import PIDProvider


class DnbUrnProvider(PIDProvider):
    """URN provider."""

    name = "urn"

    def __init__(self, name, **kwargs):
        """Constructor."""
        super().__init__(
            name,
            pid_type="urn",
            default_status=PIDStatus.REGISTERED,
            managed=True,
            **kwargs,
        )

    def generate_id(self, record, **kwargs):
        """Generates an identifier value."""
        prefix = current_app.config.get("URN_DNB_ID_PREFIX", "")
        return f"urn:nbn:{prefix}{record.pid.pid_value}"

    def reserve(self, pid, record, **kwargs):
        """Constant True.

        PID default status is registered.
        NBN registration is passive by harvesting OAI with metadataPrefix=epicur.
        """
        return True
