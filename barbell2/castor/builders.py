import math
import os
import json
import loaders
import datetime
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
        # What needs to happen here? What's the end result? A table with two columns.
        # Column 1 = Variable name
        # Column 2 = %
        # Column 3 = N/M
        print('Calculating flags...')
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

    @staticmethod
    def test():
        loader = loaders.CastorExportFileLoader('/Users/Ralph/Desktop/ESPRESSO_v2.0_DHBA_excel_export_20220919120129.xlsx')
        data = loader.load()
        builder = CastorVariableCoverageTableBuilder(data)
        builder.execute()
        builder.save('/Users/Ralph/Desktop/coverage_lever.csv')


class CastorRecordBuilder:

    def __init__(self, cast_data, dpca_data):
        self.cast_data = cast_data
        self.dpca_data = dpca_data
        self.records = None

    def execute(self):
        print('Building records...')
        last_surgery_date = self.cast_data.get_last_surgery_date()
        indexes = []
        for idx, row in self.dpca_data.df.iterrows():
            surgery_date = row['datok']
            if surgery_date > last_surgery_date:
                print(surgery_date)
                indexes.append(idx)
        self.records = self.dpca_data.df.loc[indexes]
        # drop columns not occurring in Castor
        columns_to_drop = []
        for c in self.dpca_data.df.columns:
            c_cast = 'dpca_' + c
            if c_cast not in self.cast_data.df.columns:
                columns_to_drop.append(c)
        self.records = self.records.drop(columns_to_drop, axis='columns')
        nr_records = len(self.records.index)
        # update date format to dd-mm-yyyy
        for date_column in self.dpca_data.get_date_columns():
            if date_column in self.records.columns:
                self.records[date_column] = self.records[date_column].dt.strftime('%d-%m-%Y')
        # rename columns with prefix dpca_
        self.records = self.records.add_prefix('dpca_')
        # add extra columns
        self.records['dpca_idcode'] = self.records['dpca_verrichting_upn']
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
        max_nr_cells = 25000
        nr_columns = len(self.records.columns)
        nr_rows = len(self.records.index)
        nr_cells = nr_rows * nr_columns
        if nr_cells <= max_nr_cells:
            self.records.to_csv(os.path.join(output_dir, 'new_records.csv'), index=False, sep=';')
        else:
            nr_rows_block = int(math.floor(max_nr_cells / nr_columns))
            nr_blocks = int(math.floor(nr_rows / nr_rows_block))
            i1 = 0
            i2 = nr_rows_block - 1
            for i in range(nr_blocks):
                df = self.records.loc[i1:i2]
                df.to_csv(os.path.join(output_dir, 'new_records_{:02d}.csv'.format(i)), index=False, sep=';')
                i1 = i2 + 1
                i2 += nr_rows_block
            df = self.records.loc[i1:]
            df.to_csv(os.path.join(output_dir, 'new_records_{:02d}.csv'.format(nr_blocks-1)), index=False, sep=';')

    @staticmethod
    def test():
        cast_loader = loaders.CastorExportFileLoader('/Users/Ralph/Desktop/ESPRESSO_v2.0_DPCA_excel_export_20220902120319.xlsx')
        cast_data = cast_loader.load()
        print(cast_data.get_last_surgery_date())
        dpca_loader = loaders.DicaExportFileLoader(
            '/Users/Ralph/Desktop/dpca_2021.academisch-ziekenhuis-maastricht-april.xlsx',
            '/Users/Ralph/Desktop/dpca-2022_1.0.1_datadictionary_20220128_103452.xlsx',
        )
        dpca_data = dpca_loader.load()
        builder = CastorRecordBuilder(cast_data, dpca_data)
        builder.execute()
        builder.save()


# CastorRecordBuilder.test()
# CastorVariableCoverageTableBuilder.test()
