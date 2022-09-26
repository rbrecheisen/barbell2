import math
import os
import json
import datetime
import shutil

import numpy as np
import pandas as pd


class CastorVariableCoverageTableBuilder:

    def __init__(self, cast_data):
        self.cast_data = cast_data
        self.records = None

    @staticmethod
    def calculate_proportion(values):
        return np.sum(values), len(values)

    @staticmethod
    def calculate_percentage(proportion):
        percentage = proportion[0] / float(proportion[1])
        return int(percentage * 100)

    def execute(self):
        print('Building records...')
        flags = {}
        for column in self.cast_data.df.columns:
            flags[column] = []
            for idx, row in self.cast_data.df.iterrows():
                if row[column] == '' or pd.isna(row[column]):
                    flags[column].append(0)
                else:
                    flags[column].append(1)
        print('Calculating coverage...')
        data = {
            'column': [],
            'proportion': [],
            'percentage': [],
        }
        for column in flags.keys():
            data['column'].append(column)
            proportion = self.calculate_proportion(flags[column])
            data['proportion'].append('{} / {}'.format(proportion[0], proportion[1]))
            data['percentage'].append(self.calculate_percentage(proportion))
        print(json.dumps(data, indent=4))
        self.records = pd.DataFrame(data=data)
        return self.records

    def save(self, file_path):
        self.records.to_csv(file_path, index=False, sep=';')


class CastorRecordBuilder:

    def __init__(self, cast_data, dica_data):
        self.cast_data = cast_data
        self.dica_data = dica_data
        self.records = None

    def execute(self):
        print('Building records...')
        last_surgery_date = self.cast_data.get_last_surgery_date()
        indexes = []
        for idx, row in self.dica_data.df.iterrows():
            surgery_date = row['datok']
            if surgery_date > last_surgery_date:
                indexes.append(idx)
        self.records = self.dica_data.df.loc[indexes]
        # drop columns not occurring in Castor
        columns_to_drop = []
        for c in self.dica_data.df.columns:
            c_cast = self.dica_data.prefix + c
            if c_cast not in self.cast_data.df.columns:
                columns_to_drop.append(c)
        self.records = self.records.drop(columns_to_drop, axis='columns')
        nr_records = len(self.records.index)
        # update date format to dd-mm-yyyy
        for date_column in self.dica_data.get_date_columns():
            if date_column in self.records.columns:
                self.records[date_column] = self.records[date_column].dt.strftime('%d-%m-%Y')
        # rename columns with prefix dpca_
        self.records = self.records.add_prefix(self.dica_data.prefix)
        # add extra columns
        self.records.insert(0, f'{self.dica_data.prefix}idcode', self.records[f'{self.dica_data.prefix}verrichting_upn'])
        self.records.insert(0, 'Participant Creation Date', datetime.datetime.now().strftime('%d-%m-%Y'))
        self.records.insert(0, 'Site Abbreviation', 'MUMC')
        self.records.insert(0, 'Participant Status', 'Not Set')
        # add list of new participant IDs
        participant_ids = []
        next_record_nr = int(self.cast_data.get_last_record_id()[1:]) + 1
        for i in range(nr_records):
            participant_ids.append('T{:04d}'.format(next_record_nr))
            next_record_nr += 1
        self.records.insert(0, 'Participant Id', participant_ids)
        print(f'Added participant IDs: {participant_ids}')

    def save(self, output_dir):
        if os.path.isdir(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir)
        max_nr_cells = 25000
        nr_columns = len(self.records.columns)
        nr_rows = len(self.records.index)
        print(f'Saving {nr_rows} records...')
        nr_cells = nr_rows * nr_columns
        if nr_cells <= max_nr_cells:
            f_path = os.path.join(output_dir, 'new_records.csv')
            self.records.to_csv(f_path, index=False, sep=';')
            print(f'Saved {f_path}')
        else:
            nr_rows_block = int(math.floor(max_nr_cells / nr_columns))
            nr_blocks = int(math.floor(nr_rows / nr_rows_block))
            i1 = 0
            i2 = nr_rows_block
            for i in range(nr_blocks):
                df = self.records.iloc[i1:i2]
                f_path = os.path.join(output_dir, 'new_records_{:02d}.csv'.format(i))
                df.to_csv(f_path, index=False, sep=';')
                print(f'Saved {f_path}')
                i1 = i2
                i2 += nr_rows_block
            df = self.records.iloc[i1:]
            f_path = os.path.join(output_dir, 'new_records_{:02d}.csv'.format(nr_blocks))
            df.to_csv(f_path, index=False, sep=';')
            print(f'Saved {f_path}')
