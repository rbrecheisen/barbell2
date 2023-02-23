import os
import json
import sqlite3
import logging

from datetime import datetime
from barbell2.castor.api import CastorApiClient
from barbell2.utils import current_time_secs, elapsed_secs, duration

logging.basicConfig()
logger = logging.getLogger(__name__)


class CastorToSqlite:

    CASTOR_TO_SQL_TYPES = {
        'string': 'TEXT',
        'textarea': 'TEXT',
        'radio': 'TINYINT',
        'dropdown': 'TINYINT',
        'numeric': 'FLOAT',
        'date': 'DATE',
        'year': 'TINYINT',
    }

    def __init__(self, study_name, client_id, client_secret, output_db_file='castor.db', cache=True, record_offset=0, max_nr_records=-1, log_level=logging.INFO):
        self.study_name = study_name
        self.client_id = client_id
        self.client_secret = client_secret
        self.output_db_file = output_db_file
        self.cache = cache
        self.record_offset = record_offset
        self.max_nr_records = max_nr_records
        self.log_level = log_level
        self.castor_to_sql_types = CastorToSqlite.CASTOR_TO_SQL_TYPES
        self.executed = False
        self.time_elapsed = 0
        logging.root.setLevel(self.log_level)

    def set_castor_to_sql_types(self, castor_to_sql_types):
        self.castor_to_sql_types = castor_to_sql_types

    def get_records_data_from_cache(self):
        if os.path.isfile('records_data.json'):
            logger.info('loading records data from cache...')
            with open('records_data.json', 'r') as f:
                return json.load(f)
        return None

    def write_records_data_to_cache(self, records_data):
        logger.info('writing records data to cache...')
        with open('records_data.json', 'w') as f:
            json.dump(records_data, f, indent=4)

    def get_records_data(self):
        start_secs_total = current_time_secs()
        fields = None
        records_data = None
        if self.cache:
            records_data = self.get_records_data_from_cache()
        client = CastorApiClient(self.client_id, self.client_secret)
        study = client.get_study(self.study_name)
        assert study is not None, 'Castor API client could not find study {}'.format(self.study_name)
        study_id = client.get_study_id(study)
        if records_data is None:
            logger.info('getting field definitions...')
            fields = client.get_fields(study_id)
            fields_ok = []
            for field in fields:
                if field['field_variable_name'] is None or field['field_type'] is None:
                    continue
                if field['field_type'] == 'calculation' or field['field_type'] == 'remark':
                    continue
                fields_ok.append(field)
            fields = fields_ok
        if records_data is None:
            logger.info('getting records data...')
            records_data = {}
            count = 0
            records = client.get_records(study_id)
            logger.info('Found {} records to process'.format(len(records)))
            for record in records:
                if count < self.record_offset:
                    continue
                if count == self.max_nr_records:
                    break
                start_secs = current_time_secs()
                record_id = client.get_record_id(record)
                for field in fields:
                    field_variable_name = field['field_variable_name']
                    field_value = client.get_field_value(study_id, record_id, field['id'])
                    if field_value is None:
                        field_value = ''
                    if field_variable_name not in records_data.keys():
                        records_data[field_variable_name] = {'field_type': field['field_type'], 'field_values': []}
                    records_data[field_variable_name]['field_values'].append(field_value)
                elapsed_time = duration(elapsed_secs(start_secs))                
                logger.info('processed record {} in {}'.format(record_id, elapsed_time))
                count += 1
        if self.cache:
            self.write_records_data_to_cache(records_data)
        elapsed_time_total = duration(elapsed_secs(start_secs_total))
        logger.info('total time elapsed: {}'.format(elapsed_time_total))
        return records_data

    def generate_sql_field_from_field_type_and_field_variable_name(self, field_type, field_variable_name):
        return '{} {}'.format(field_variable_name, self.castor_to_sql_types[field_type])

    def generate_sql_for_creating_table(self, records_data):
        sql = 'CREATE TABLE data (id INTEGER PRIMARY KEY, '
        for field_variable_name in records_data.keys():
            field_type = records_data[field_variable_name]['field_type']
            field_type_sql = self.generate_sql_field_from_field_type_and_field_variable_name(field_type, field_variable_name)
            if field_type_sql is not None:
                sql += field_type_sql + ', '
        sql = sql[:-2] + ');'
        return sql

    @staticmethod
    def generate_sql_for_dropping_table():
        return 'DROP TABLE IF EXISTS data;'

    def get_sql_object_for_field_data(self, field_data, i):
        value = field_data['field_values'][i]
        if (field_data['field_type'] == 'radio' or field_data['field_type'] == 'dropdown' or field_data['field_type'] == 'year') and value != '':
            return int(value)
        if field_data['field_type'] == 'numeric' and value != '':
            return float(value)
        if field_data['field_type'] == 'date' and value != '':
            return datetime.strptime(value, '%d-%m-%Y').date()
        return str(field_data['field_values'][i])

    def generate_list_of_sql_statements_for_inserting_records(self, records_data):
        nr_records = len(records_data[list(records_data.keys())[0]]['field_values'])
        placeholders = []
        values = []
        for i in range(nr_records):
            placeholder = 'INSERT INTO data ('
            value = []
            for field_variable_name in records_data.keys():
                placeholder += field_variable_name + ', '
            placeholder = placeholder[:-2] + ') VALUES ('
            for field_variable_name in records_data.keys():
                value.append(self.get_sql_object_for_field_data(records_data[field_variable_name], i))
                placeholder += '?, '
            placeholder = placeholder[:-2] + ');'
            placeholders.append(placeholder)
            values.append(value)
        return placeholders, values

    @staticmethod
    def test_search_queries(cursor):
            cursor.execute('SELECT * FROM data WHERE dpca_gebjaar > 1965;')
            assert len(cursor.fetchall()) == 0
            cursor.execute('SELECT * FROM data WHERE dpca_gebjaar < 1965;')
            assert len(cursor.fetchall()) == 1
            cursor.execute('SELECT * FROM data WHERE dpca_gebjaar = 1963;')
            assert len(cursor.fetchall()) == 1
            cursor.execute('SELECT * FROM data WHERE dpca_datok BETWEEN "2018-05-01" AND "2018-07-01";')  # Note the yyyy-mm-dd format!
            assert len(cursor.fetchall()) == 1

    def create_sql_database(self, records_data):
        conn = None
        try:
            conn = sqlite3.connect(self.output_db_file)
            cursor = conn.cursor()
            cursor.execute(self.generate_sql_for_dropping_table())
            cursor.execute(self.generate_sql_for_creating_table(records_data))
            placeholders, values = self.generate_list_of_sql_statements_for_inserting_records(records_data)
            for i in range(len(placeholders)):
                cursor.execute(placeholders[i], values[i])
            conn.commit()
            self.test_search_queries(cursor)
        except sqlite3.Error as e:
            print(e)
        finally:
            if conn:
                conn.close()

    def execute(self):
        records_data = self.get_records_data()
        self.create_sql_database(records_data)


if __name__ == '__main__':
    def main():
        converter = CastorToSqlite(
            study_name='ESPRESSO_v2.0_DPCA',
            client_id=open(os.path.join(os.environ['HOME'], 'castorclientid.txt')).readline().strip(),
            client_secret=open(os.path.join(os.environ['HOME'], 'castorclientsecret.txt')).readline().strip(),
            output_db_file='castor.db',
            cache=True,
            record_offset=0,
            max_nr_records=1,
            log_level=logging.INFO,
        )
        converter.execute()
    main()
