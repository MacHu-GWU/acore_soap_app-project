# -*- coding: utf-8 -*-

"""
sdk module public API.

Example:

.. code-block:: python

    >>> from acore_soap_app.sdk.api import canned
    >>> from acore_soap_app.sdk.api import run_soap_command
"""

from .core import run_soap_command
from .canned import api as canned
