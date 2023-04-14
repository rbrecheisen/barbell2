import os
import sqlite3
import logging
import pandas as pd

from datetime import datetime
from barbell2.castor.api import CastorApiClient
from barbell2.utils import current_time_secs, current_time_millis, elapsed_secs, elapsed_millis, duration


logging.basicConfig()
logger = logging.getLogger(__name__)

CASTOR_TO_SQL_TYPES = {
    'string': 'TEXT',
    'textarea': 'TEXT',
    'radio': 'TINYINT',
    'dropdown': 'TINYINT',
    'numeric': 'FLOAT',
    'date': 'DATE',
    'year': 'TINYINT',
}


class CastorToSqlite:

    def __init__(
            self, 
            study_name, 
            client_id, 
            client_secret, 
            output_db_file='castor.db', 
            add_timestamp=False,
            log_level=logging.INFO, 
        ):
        self.study_name = study_name
        self.client_id = client_id
        self.client_secret = client_secret
        self.output_db_file = output_db_file
        if add_timestamp:
            items = os.path.splitext(self.output_db_file)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            self.output_db_file = f'{items[0]}-{timestamp}{items[1]}'
        self.log_level = log_level
        self.castor_to_sql_types = CASTOR_TO_SQL_TYPES

    def get_records_data(self):

        client = CastorApiClient(self.client_id, self.client_secret)
        study = client.get_study(self.study_name)
        study_id = client.get_study_id(study)

        # Get field definitions
        study_structure_url = 'https://data.castoredc.com/api' + '/study/{}/export/structure'.format(study_id)
        response = client.session.get(study_structure_url)
        with open('fields.csv', 'w') as f:
            f.write(response.text)
        field_defs = {}
        for line in response.text.split('\n')[1:]:
            items = line.split(';')
            if len(items) <= 11:
                continue
            field_type = items[11]
            if field_type != 'calculation' and field_type != 'remark':
                field_id = items[8]
                field_variable_name = items[9]
                option_group_id = items[15]
                field_defs[field_id] = [field_variable_name, field_type, option_group_id]
        
        # Get records
        study_data_url = 'https://data.castoredc.com/api' + '/study/{}/export/data'.format(study_id)
        response = client.session.get(study_data_url)
        with open('records.csv', 'w') as f:
            f.write(response.text)
        records = {}
        for line in response.text.split('\n')[1:]:
            items = line.split(';')
            if len(items) == 9:
                record_id = items[1]
                form_type = items[2]
                if form_type == '':
                    records[record_id] = {}
                elif form_type == 'Study':
                    field_id = items[5]
                    field_value = items[6]
                    records[record_id][field_id] = field_value

        # Get option groups
        option_group_url = 'https://data.castoredc.com/api' + '/study/{}/export/optiongroups'.format(study_id)
        response = client.session.get(option_group_url)
        with open('optiongroups.csv', 'w') as f:
            f.write(response.text)
        option_groups = {}
        for line in response.text.split('\n')[1:]:
            items = line.split(';')
            if len(items) == 6:
                option_group_id = items[1]
                if option_group_id not in option_groups.keys():
                    option_groups[option_group_id] = []
                option_groups[option_group_id].append([items[4], items[5]])  # option name, option value

        # Initialize records data columns
        records_data = {}
        for field_id in field_defs.keys():
            field_variable_name = field_defs[field_id][0]
            field_type = field_defs[field_id][1]
            if field_type == 'radio' or field_type == 'checkbox':
                option_group_id = field_defs[field_id][2]
                for option in option_groups[option_group_id]:
                    extended_field_variable_name = field_variable_name + '$' + option[1]
                    records_data[extended_field_variable_name] = []
            else:
                records_data[field_variable_name] = []

        # TODO: Build the records_data table
        for field_id in field_defs.keys():
            field_variable_name = field_defs[field_id][0]
            field_type = field_defs[field_id][1]
        

        # for field_id in field_defs.keys():
        #     field_variable_name = field_defs[field_id][0]
        #     field_type = field_defs[field_id][1]
        #     if field_type == 'radio' or field_type == 'checkbox':
        #         pass
        #     else:
        #         print(field_variable_name)
        #         for record_id in list(records.keys()):
        #             if field_id not in records.keys():
        #                 records_data[field_id] = {'field_variable_name': field_variable_name, 'field_type': field_type, 'field_values': []}
        #             if field_id in records.keys():
        #                 records_data[field_id]['field_values'].append(records[record_id][field_id])
        #             else:
        #                 records_data[field_id]['field_values'].append('')

        return records

    def execute(self):
        self.get_records_data()


if __name__ == '__main__':
    def main():
        extractor = CastorToSqlite(
            study_name='ESPRESSO_v2.0_DPCA',
            client_id=open(os.path.join(os.environ['HOME'], 'castorclientid.txt')).readline().strip(),
            client_secret=open(os.path.join(os.environ['HOME'], 'castorclientsecret.txt')).readline().strip(),
            output_db_file='/Users/Ralph/Desktop/castor.db',
            add_timestamp=False,
            log_level=logging.INFO,
        )
        extractor.execute()
    main()
