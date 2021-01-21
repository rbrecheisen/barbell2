import os
import pytest

from barbell2 import CastorExportClient


HOME_DIR = os.environ['HOME']
EXPORT_FILE_DIR = os.path.join(HOME_DIR, 'data/surfdrive/projects/20210120_castorexportclient_test')
EXPORT_FILE_PATH = os.path.join(EXPORT_FILE_DIR, 'ESPRESSO_v2.0_DPCA_excel_export_20210120104629.xlsx')
OUTPUT_FILE_PATH = os.path.join(EXPORT_FILE_DIR, 'saved.csv')

# Requirements specification:
# https://docs.google.com/document/d/1cEtidByu0D2liaHwLqMXwiturqIICiWTa8Ta7NepK_U/edit


@pytest.fixture(scope="session", autouse=True)
def client():
    print('Creating client instance and loading data...')
    client = CastorExportClient(show_params=False)
    client.load_data(EXPORT_FILE_PATH)
    return client


def test_find_option_values(client):
    option_values = client.find_option_values('Chemoradio')
    key = 'dpca_adjuvant'
    assert len(option_values.keys()) == 1
    assert key in option_values.keys()
    assert option_values[key] == [
        (0, 'No'),
        (1, 'Chemoradiotherapy'),
        (2, 'Chemotherapy'),
        (3, 'Radiotherapy'),
        (7, 'Other'),
        (9, 'Unknown')
    ]

def test_info(client):
    client.info()
