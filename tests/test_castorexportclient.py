import os
import pytest

from barbell2 import CastorExportClient


HOME_DIR = os.environ['HOME']
EXPORT_FILE_DIR = os.path.join(HOME_DIR, 'data/surfdrive/projects/20210120_castorexportclient_test')
EXPORT_FILE_PATH = os.path.join(EXPORT_FILE_DIR, 'ESPRESSO_v2.0_DPCA_excel_export_20210120104629.xlsx')
OUTPUT_FILE_PATH = os.path.join(EXPORT_FILE_DIR, 'saved.csv')


@pytest.fixture
def client():
    client = CastorExportClient()
    client.load_export(EXPORT_FILE_PATH)
    return client


def test_data_saved(client):
    client.save(OUTPUT_FILE_PATH)


def show_dd(client):
    dd = client.data_dict
    for k, v in dd.items():
        print('{}: {}'.format(k , v))


def show_options(client):
    options = client.options
    for k, v in options.items():
        print('{}:'.format(k))
        for option in v:
            print('   {}'.format(option))
