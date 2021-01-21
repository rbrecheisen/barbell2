import os
import pytest

from barbell2 import CastorExportClient


HOME_DIR = os.environ['HOME']
EXPORT_FILE_DIR = os.path.join(HOME_DIR, 'data/surfdrive/projects/20210120_castorexportclient_test')
EXPORT_FILE_PATH = os.path.join(EXPORT_FILE_DIR, 'ESPRESSO_v2.0_DPCA_excel_export_20210120104629.xlsx')
OUTPUT_FILE_PATH = os.path.join(EXPORT_FILE_DIR, 'saved.csv')

# Requirements specification:
# https://docs.google.com/document/d/1cEtidByu0D2liaHwLqMXwiturqIICiWTa8Ta7NepK_U/edit


@pytest.fixture
def client():
    client = CastorExportClient()
    client.load_export(EXPORT_FILE_PATH)
    return client


def test_query1(client):
    pass


def test_query2(client):
    pass
