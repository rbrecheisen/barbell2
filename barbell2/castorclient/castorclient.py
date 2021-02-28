import os
import json

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from barbell2.utils import Logger


class CastorClient:

    def __init__(self, client_id=None, client_secret=None):
        if client_id is None:
            with open('{}/castorclientid.txt'.format(os.environ['HOME']), 'r') as f:
                client_id = f.readline().strip()
        if client_secret is None:
            with open('{}/castorclientsecret.txt'.format(os.environ['HOME']), 'r') as f:
                client_secret = f.readline().strip()
        self.base_url = 'https://data.castoredc.com'
        self.token_url = self.base_url + '/oauth/token'
        self.api_url = self.base_url + '/api'
        self.session = self.create_session(client_id, client_secret, self.token_url)
        self.logger = Logger(prefix='log_castorclient')

    @staticmethod
    def create_session(client_id, client_secret, token_url):
        client = BackendApplicationClient(client_id=client_id)
        client_session = OAuth2Session(client=client)
        client_session.fetch_token(
            token_url=token_url,
            client_id=client_id,
            client_secret=client_secret,
        )
        return client_session

    def get_studies(self):
        response = self.session.get(self.api_url + '/study').json()
        studies = []
        for study in response['_embedded']['study']:
            studies.append(study)
        return studies

    def get_study_id(self, name):
        studies = self.get_studies()
        for study in studies:
            if study['name'] == name:
                return study['study_id']
        return None

    def get_fields(self, study_id, use_cache=True, verbose=False):
        if use_cache and os.path.isfile('cache/fields_{}.json'.format(study_id)):
            self.logger.print('Loading fields from cache/fields_{}'.format(study_id))
            fields = json.load(open('cache/fields_{}.json'.format(study_id), 'r'))
            return fields
        else:
            self.logger.print('Loading fields for study {} from Castor'.format(study_id))
            url = self.api_url + '/study/{}/field'.format(study_id)
            response = self.session.get(url).json()
            page_count = response['page_count']
            fields = []
            for i in range(1, page_count + 1):
                url = self.api_url + '/study/{}/field?page={}'.format(study_id, i)
                response = self.session.get(url).json()
                for field in response['_embedded']['fields']:
                    fields.append(field)
                    if verbose:
                        self.logger.print(field['id'])
            os.makedirs('cache', exist_ok=True)
            json.dump(fields, open('cache/fields_{}.json'.format(study_id), 'w'))
            return fields

    @staticmethod
    def get_field(name, fields):
        for f in fields:
            if f['field_variable_name'] == name:
                return f
        return None

    def get_field_id(self, name, fields):
        f = self.get_field(name, fields)
        return f['id']

    def get_records(self, study_id, use_cache=True, verbose=False):
        if use_cache and os.path.isfile('cache/records_{}.json'.format(study_id)):
            self.logger.print('Loading records from cache/records_{}.json'.format(study_id))
            records = json.load(open('cache/records_{}.json'.format(study_id), 'r'))
            return records
        else:
            self.logger.print('Loading records for study {} from Castor'.format(study_id))
            url = self.api_url + '/study/{}/record'.format(study_id)
            response = self.session.get(url).json()
            page_count = response['page_count']
            records = []
            for i in range(1, page_count + 1):
                url = self.api_url + '/study/{}/record?page={}'.format(study_id, i)
                response = self.session.get(url).json()
                for record in response['_embedded']['records']:
                    if not record['id'].startswith('ARCHIVED'):
                        records.append(record)
                        if verbose:
                            self.logger.print(record['id'])
            os.makedirs('cache', exist_ok=True)
            json.dump(records, open('cache/records_{}.json'.format(study_id), 'w'))
            return records

    def get_field_data(self, study_id, record_id, field_id):
        url = self.api_url + '/study/{}/record/{}/study-data-point/{}'.format(study_id, record_id, field_id)
        field_data = self.session.get(url).json()
        return field_data


if __name__ == '__main__':
    client = CastorClient()
    print(client.get_studies())
