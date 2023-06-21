# -*- coding: utf-8 -*-

"""
agent module public API.

Example:

.. code-block:: python

    >>> from acore_soap_app.agent.api import DEFAULT_USERNAME
    >>> from acore_soap_app.agent.api import DEFAULT_PASSWORD
    >>> from acore_soap_app.agent.api import DEFAULT_HOST
    >>> from acore_soap_app.agent.api import DEFAULT_PORT
    >>> from acore_soap_app.agent.api import SOAPRequest
    >>> from acore_soap_app.agent.api import SOAPResponse
    >>> from acore_soap_app.agent.api import get_boto_ses
"""

from .impl import DEFAULT_USERNAME
from .impl import DEFAULT_PASSWORD
from .impl import DEFAULT_HOST
from .impl import DEFAULT_PORT
from .impl import SOAPRequest
from .impl import SOAPResponse
from .impl import get_boto_ses
