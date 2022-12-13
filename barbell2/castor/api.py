from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session


class CastorApiClient:

    base_url = 'https://data.castoredc.com'
    token_url = base_url + '/oauth/token'
    api_url = base_url + '/api'

    def __init__(self, client_id, client_secret):
        self.session = self.create_session(client_id, client_secret)
        self.studies = self.get_studies()

    def create_session(self, client_id, client_secret):
        """ Creates new session to communicate with Castor database REST API
        :param client_id
        :param client_secret
        """
        client = BackendApplicationClient(client_id=client_id)
        client_session = OAuth2Session(client=client)
        client_session.fetch_token(
            token_url=self.token_url,
            client_id=client_id,
            client_secret=client_secret,
        )
        return client_session

    def get_studies(self):
        """ Returns list of study objects
        """
        response = self.session.get(self.api_url + '/study')
        response_data = response.json()
        studies = []
        for study in response_data['_embedded']['study']:
            studies.append(study)
        return studies

    def get_study(self, name):
        """ Returns study object for given name
        :param name Study name
        """
        for study in self.studies:
            if study['name'] == name:
                return study
        return None

    @staticmethod
    def get_study_id(study):
        """ Returns study ID for given study object
        :param study Study object
        """
        study_id = study['study_id']
        return study_id

    def get_records(self, study_id, verbose=False):
        """ Returns list of records
        :param study_id Study ID
        :param verbose
        """
        record_url = self.api_url + '/study/{}/record'.format(study_id)
        response = self.session.get(record_url)
        response_data = response.json()
        page_count = response_data['page_count']
        records = []
        for i in range(1, page_count + 1):
            record_page_url = self.api_url + '/study/{}/record?page={}'.format(study_id, i)
            response = self.session.get(record_page_url)
            response_data = response.json()
            for record in response_data['_embedded']['records']:
                if not record['id'].startswith('ARCHIVED'):
                    records.append(record)
                    if verbose:
                        print(record)
        return records

    @staticmethod
    def get_record_id(record):
        """ Returns record ID for given record object
        :param record Record object
        """
        record_id = record['id']
        return record_id

    def get_fields(self, study_id, verbose=False):
        """ Returns list of field objects defined for the given study
        :param study_id Study ID
        :param verbose
        """
        field_url = self.api_url + '/study/{}/field'.format(study_id)
        response = self.session.get(field_url)
        response_data = response.json()
        page_count = response_data['page_count']
        fields = []
        for i in range(1, page_count + 1):
            field_page_url = self.api_url + '/study/{}/field?page={}'.format(study_id, i)
            response = self.session.get(field_page_url)
            response_data = response.json()
            for field in response_data['_embedded']['fields']:
                fields.append(field)
                if verbose:
                    print(field)
        return fields

    @staticmethod
    def get_field(fields, name):
        """ Returns field object of given name
        :param fields List of field objects to search through
        :param name Field name
        """
        for field in fields:
            if field['field_variable_name'] == name:
                return field
        return None

    @staticmethod
    def get_field_id(field):
        """ Returns field ID for given field object
        :param field Field object
        """
        field_id = field['id']
        return field_id

    def get_field_value(self, study_id, record_id, field_id):
        """ Returns value for given field, record and study
        :param study_id Study ID
        :param record_id Record ID
        :param field_id Field ID for which data is retrieved
        """
        field_data_url = self.api_url + '/study/{}/record/{}/study-data-point/{}'.format(study_id, record_id, field_id)
        response = self.session.get(field_data_url)
        response_data = response.json()
        field_value = response_data['value']
        return field_value
