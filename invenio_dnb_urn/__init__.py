# -*- coding: utf-8 -*-
#
# Copyright (C) 2022, 2023 University of Münster.
#
# Invenio-Dnb-Urn is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio Serializer to create xepicur serialization for DNB harvesting."""

from .serialize import InvenioSerializerXMetaDissPlus
from .provider import DnbUrnProvider

__version__ = '0.1.0'

__all__ = (
    '__version__',
    'InvenioSerializerXMetaDissPlus',
    'DnbUrnProvider',
)

