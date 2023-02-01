# -*- coding: utf-8 -*-
#
# Copyright (C) 2022, 2023 University of Münster.
#
# Invenio-Dnb-Urn is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

import json
import warnings

from dnb_urn_service import DNBUrnServiceRESTClient
from dnb_urn_service.errors import DNBURNServiceError
from flask import current_app
from invenio_pidstore.models import PIDStatus
from invenio_rdm_records.services.pids.providers import PIDProvider


class DNBUrnClient:
    """DNB Urn Client."""

    def __init__(self, name, config_prefix=None, **kwargs):
        """Constructor."""
        self.name = name
        self._config_prefix = config_prefix or "URN_DNB"
        self._api = None

    def cfgkey(self, key):
        """Generate a configuration key."""
        return f"{self._config_prefix}_{key.upper()}"

    def cfg(self, key, default=None):
        """Get a application config value."""
        return current_app.config.get(self.cfgkey(key), default)

    def generate_urn(self, record):
        """Generate a URN."""
        self.check_credentials()
        prefix = self.cfg("id_prefix")
        if not prefix:
            raise RuntimeError("Invalid URN prefix configured.")
        urn_format = self.cfg("format", "{prefix}-{id}")
        return urn_format.format(prefix=prefix, id=record.pid.pid_value)

    def check_credentials(self, **kwargs):
        """Returns if the client has the credentials properly set up.
        If the client is running on test mode the credentials are required, too.
        """
        if not (self.cfg("username") and self.cfg("password") and self.cfg("id_prefix")):
            warnings.warn(
                f"The {self.__class__.__name__} is misconfigured. Please "
                f"set {self.cfgkey('username')}, {self.cfgkey('password')}"
                f" and {self.cfgkey('id_prefix')} in your configuration.",
                UserWarning,
            )

    @property
    def api(self):
        """DNB URN Service API client instance."""
        if self._api is None:
            self.check_credentials()
            self._api = DNBUrnServiceRESTClient(
                self.cfg("username"),
                self.cfg("password"),
                self.cfg("id_prefix"),
                self.cfg("test_mode", True),
            )
        return self._api


class DnbUrnProvider(PIDProvider):
    """URN provider."""

    name = "urn"

    def __init__(
        self,
        id_,
        client=None,
        pid_type="urn",
        **kwargs):
        """Constructor."""
        super().__init__(
            id_,
            client=(client or DNBUrnClient("dnb", config_prefix="URN_DNB")),
            pid_type=pid_type,
            default_status=PIDStatus.NEW,
            managed=True,
            **kwargs,
        )

    @staticmethod
    def _log_errors(errors):
        """Log errors from DNBURNServiceError class."""
        # DNBURNServiceError is a tuple with the errors on the first
        errors = json.loads(errors.args[0])["errors"]
        for error in errors:
            field = error["source"]
            reason = error["title"]
            current_app.logger.warning(f"Error in {field}: {reason}")

    def generate_id(self, record, **kwargs):
        """Generate a unique URN."""
        # Delegate to client
        return self.client.generate_urn(record)

    def can_modify(self, pid, **kwargs):
        """Checks if the PID can be modified."""
        return not pid.is_registered() and not pid.is_reserved()

    def register(self, pid, record, url=None, **kwargs):
        """Register a URN via the DNB URN service API.

        :param pid: the PID to register.
        :param record: the record metadata for the URN.
        :returns: `True` if is registered successfully.
        """
        # This is what is called when the record is published
        # and the URN needs to be minted
        local_success = super().register(pid)
        if not local_success:
            return False

        try:
            self.client.api.create_urn(url=url, urn=pid.pid_value)
            return True
        except DNBURNServiceError as e:
            current_app.logger.warning(
                "DNBURN provider error when " f"registering URN for {pid.pid_value}"
            )
            self._log_errors(e)
            return False

    def update(self, pid, url=None, **kwargs):
        """Update url associated with a URN.

        This can be called after a URN is registered.
        :param pid: the PID to register.
        :returns: `True` if is updated successfully.
        """
        try:
            self.client.api.modify_urn(urn=pid.pid_value, url=url)
        except DNBURNServiceError as e:
            current_app.logger.warning(
                "DNBURN provider error when " f"updating URL for {pid.pid_value}"
            )
            self._log_errors(e)

            return False

        if pid.is_deleted():
            return pid.sync_status(PIDStatus.REGISTERED)

        return True

    def delete(self, pid, **kwargs):
        """Delete/unregister a registered URN.

        If the PID has not been reserved then it's deleted only locally.
        Otherwise, there is a problem: a URN can't be deleted remotely.
        :returns: `True` if is deleted successfully.
        """

        return super().delete(pid, **kwargs)

    def validate(self, record, identifier=None, provider=None, **kwargs):
        """Validate the attributes of the identifier.

        :returns: A tuple (success, errors). The first specifies if the
                  validation was passed successfully. The second one is an
                  array of error messages.
        """
        success, errors = super().validate(record, identifier, provider, **kwargs)

        # Format check
        if identifier is not None:
            try:
                self.client.api.check_urn(identifier)
            except ValueError as e:
                errors.append(str(e))

        return not bool(errors), errors
