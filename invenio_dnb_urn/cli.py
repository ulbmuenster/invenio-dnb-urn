# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2022 CERN.
# Copyright (C) 2019-2022 Northwestern University.
#
# Invenio-Serializer-Epicur is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Command-line tools for demo module."""

from flask_security.confirmable import confirm_user
from flask_security.utils import hash_password
from invenio_accounts.proxies import current_datastore
from invenio_db import db
from invenio_users_resources.services.users.tasks import reindex_user

COMMUNITY_OWNER_EMAIL = "community@demo.org"
USER_EMAIL = "user@demo.org"
HELP_MSG_USER = "User e-mail of an already existing user."


def _get_or_create_user(email):
    user = current_datastore.get_user(email)
    if not user:
        with db.session.begin_nested():
            user = current_datastore.create_user(
                email=email,
                password=hash_password("123456"),
                active=True,
                preferences=dict(visibility="public", email_visibility="public"),
            )
        confirm_user(user)
        db.session.commit()
        reindex_user(user.id)
    return user
