"""Top-level package for Barbell2."""

import os

__author__ = """Ralph Brecheisen"""
__email__ = 'ralph.brecheisen@gmail.com'
__version__ = os.environ['VERSION']

from .dicomexplorer.dicomexplorer import DicomExplorer
from .castorexportclient.castorexportclient import CastorExportClient
