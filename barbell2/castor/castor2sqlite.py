import os
import json
import sqlite3
import logging
import pandas as pd

from datetime import datetime
from barbell2.castor.api import CastorApiClient
from barbell2.utils import current_time_secs, elapsed_secs, duration

logging.basicConfig()
logger = logging.getLogger(__name__)


#####################################################################################################################################
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

    def check_output_db_file(output_db_file):
        if os.path.isfile(output_db_file):
            file_base = os.path.splitext(output_db_file)[0]
            for i in range(100):
                file_path = file_base + '-{}.db'.format(i)
                if not os.path.isfile(file_path):
                    return file_path
            raise RuntimeError('Output file {} already exists'.format(file_path))
        return output_db_file

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
        except sqlite3.Error as e:
            logger.error(e)
        finally:
            if conn:
                conn.close()

    def execute(self):
        records_data = self.get_records_data()
        self.create_sql_database(records_data)
        return self.output_db_file
    

#####################################################################################################################################
class CastorExcelToSqlite:

    CASTOR_TO_SQL_TYPES = {
        'string': 'TEXT',
        'textarea': 'TEXT',
        'radio': 'TINYINT',
        'dropdown': 'TINYINT',
        'numeric': 'FLOAT',
        'date': 'DATE',
        'year': 'TINYINT',
    }

    FIELDS_TO_SKIP = [
        'Participant Id',
        'Participant Status',
        'Site Abbreviation',
        'Participant Creation Date',
    ]

    def __init__(self, export_excel_file, db_prefix, output_db_file='castor.db', record_offset=0, max_nr_records=-1, log_level=logging.INFO):
        self.export_excel_file = export_excel_file
        self.db_prefix = db_prefix
        if not self.db_prefix.endswith('_'):
            self.db_prefix += '_'
        self.output_db_file = output_db_file
        self.record_offset = record_offset
        self.max_nr_records = max_nr_records
        self.log_level = log_level
        self.castor_to_sql_types = CastorExcelToSqlite.CASTOR_TO_SQL_TYPES

    def set_castor_to_sql_types(self, castor_to_sql_types):
        self.castor_to_sql_types = castor_to_sql_types

    @staticmethod
    def get_field_types(field_definitions):
        field_types = {}
        for _, row in field_definitions.iterrows():
            variable_name = row['Variable name']
            field_type = row['Original field type']
            if pd.isna(field_type) or field_type == 'calculation' or field_type == 'remark' or pd.isna(variable_name):
                continue
            field_types[variable_name] = field_type
        return field_types
    
    def get_records_data(self, field_data, field_types):
        records_data = {}
        count = 0
        for _, row in field_data.iterrows():
            if count < self.record_offset:
                continue
            if count == self.max_nr_records:
                break
            for field_variable_name in field_types.keys():
                if field_variable_name in CastorExcelToSqlite.FIELDS_TO_SKIP:
                    continue
                field_value = row[field_variable_name]
                if pd.isna(field_value):
                    field_value = ''
                if field_variable_name not in records_data.keys():
                    field_type = field_types[field_variable_name]
                    records_data[field_variable_name] = {'field_type': field_type, 'field_values': []}
                records_data[field_variable_name]['field_values'].append(field_value)
            count += 1
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
        try:            
            if (field_data['field_type'] == 'radio' or field_data['field_type'] == 'dropdown' or field_data['field_type'] == 'year') and value != '':
                return int(value)
            if field_data['field_type'] == 'numeric' and value != '':
                return float(value)
            if field_data['field_type'] == 'date' and value != '':
                return datetime.strptime(value, '%d-%m-%Y').date()
        except ValueError:
            logger.info('[ERROR] could not parse value "{}" for field type "{}". Forcing string format...'.format(value, field_data['field_type']))
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
        except sqlite3.Error as e:
            logger.error(e)
        finally:
            if conn:
                conn.close()

    def execute(self):
        logger.info('Loading field definitions...')
        field_definitions = pd.read_excel(self.export_excel_file, sheet_name='Study variable list', engine='openpyxl', dtype=str)
        field_types = self.get_field_types(field_definitions)
        logger.info('Loading field data...')
        field_data = pd.read_excel(self.export_excel_file, sheet_name='Study results', engine='openpyxl', dtype=str)
        logger.info('Building records data...')
        records_data = self.get_records_data(field_data, field_types)
        logger.info('Creating SQL database...')
        self.create_sql_database(records_data)
        return self.output_db_file


#####################################################################################################################################
class CastorQuery:

    def __init__(self, db_file, cache=True):
        self.db = self.load_db(db_file)
        self.cache = cache
        if self.cache:
            self.queries = self.read_queries_from_cache()
        else:
            self.queries = []
        self.current_query = None
        self.output = None

    def __del__(self):
        if self.db:
            self.db.close()
            self.db = None
        if self.cache:
            self.write_queries_to_cache(self.queries)

    def load_db(self, db_file):
        try:
            db = sqlite3.connect(db_file)
            return db
        except sqlite3.Error as e:
            logger.error(e)
        return None

    def read_queries_from_cache(self):
        if os.path.isfile('queries.json'):
            logger.info('Reading queries from cache...')
            with open('queries.json', 'r') as f:
                return json.load(f)
        return []

    def write_queries_to_cache(self, queries):
        logger.info('Writing queries to cache...')
        with open('queries.json', 'w') as f:
            json.dump(queries, f)

    def add_query(self, query):
        if query not in self.queries:
            self.queries.append(query)
            self.set_current_query(len(self.queries)-1)
        else:
            self.set_current_query(self.queries.index(query))

    def remove_query(self, idx):        
        self.queries.remove(self.queries[idx])
        if len(self.queries) == 0:
            self.set_current_query(None)
        else:
            self.set_current_query(0)

    def remove_all_queries(self):
        self.queries = []
        if self.cache:
            self.write_queries_to_cache(self.queries)

    def set_current_query(self, idx):
        self.current_query = self.queries[idx]

    @staticmethod
    def get_column_names(data):
        column_names = []
        for column in data.description:
            column_names.append(column[0])
        return column_names

    def execute(self):
        if self.current_query is not None and self.db is not None:
            self.output = None
            cursor = self.db.cursor()
            data = cursor.execute(self.current_query)
            df_data = []
            for result in data:
                df_data.append(result)
            self.output = pd.DataFrame(df_data, columns=self.get_column_names(data))
        return self.output

    def to_csv(self, df):
        self.output.to_csv(df, index=False, sep=';')

    def to_excel(self, df):
        self.output.to_excel(df, index=False)


#####################################################################################################################################
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
        # selector = CastorQuery('/Users/Ralph/Desktop/castor.db')
        # selector.set_current_query(0)
        # selector.add_query('SELECT * FROM data WHERE dpca_datok BETWEEN "2018-05-01" AND "2018-07-01";')
        # selector.execute()
        # selector.to_csv('query_results.csv')
        # selector.to_excel('query_results.xlsx')
    main()
