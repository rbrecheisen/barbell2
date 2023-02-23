import os
import json
import sqlite3
import logging
import pandas as pd

logging.basicConfig()
logging.root.setLevel(logging.INFO)
logger = logging.getLogger(__name__)


class CastorQuery:

    def __init__(self, db_file):
        self.db = self.load_db(db_file)
        self.queries = self.read_queries_from_cache()
        self.current_query = None
        self.output = None

    def __del__(self):
        if self.db:
            self.db.close()
            self.db = None
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
            self.output.to_csv('query_results.csv', index=False, sep=';')
        return self.output
                    

if __name__ == '__main__':
    def main():
        selector = CastorQuery('/Users/Ralph/Desktop/castor.db')
        # selector.set_current_query(0)
        # selector.add_query('SELECT * FROM data WHERE dpca_datok BETWEEN "2018-05-01" AND "2018-07-01";')
        # selector.add_query('SELECT COUNT(*) FROM data WHERE dpca_datok BETWEEN "2018-05-01" AND "2018-07-01";')
        selector.execute()
    main()
