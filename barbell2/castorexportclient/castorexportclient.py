import json
import pandas as pd
import numpy as np


class CastorExportClient:

    def __init__(self):

        self.params = {
            'sheet_name_data': 'Study results',             # with spaces
            'sheet_name_data_dict': 'Study variable list',  # ''
            'sheet_name_data_opts': 'Field options',        # ''
            'data_dict_var_name': 'Variable_name',          # without spaces because column names are updated
            'data_dict_field_type': 'Field_type',           # ''
            'data_dict_field_label': 'Field_label',         # ''
            'data_dict_group_name': 'Optiongroup_name',     # ''
            'data_opts_group_name': 'Option_group_name',    # ''
            'data_opts_opt_name': 'Option_name',            # ''
            'data_opts_opt_val': 'Option_value',            # ''
            'data_cols_ignore': [
                'Record_Id',                                # without spaces because column names are updated
                'Institute_Abbreviation',                   # ''
                'Record_Creation_Date',                     # ''
            ],
            'data_miss_float': [999, 9999, 99999, 999.0, 9999.0],
            'data_miss_date': ['09-09-1809'],
            'to_pandas': {
                'dropdown': 'category',
                'radio': 'category',
                'string': 'object',
                'textarea': 'object',
                'remark': 'object',
                'date': 'datetime64[ns]',
                'year': 'Int64',
                'numeric': 'float64',
            }
        }

        print(json.dumps(self.params, indent=4))

    @staticmethod
    def remove_spaces(value):
        return value.replace(' ', '_')

    def load_data(self, file_path):

        # Load data dictionary first and remove spaces from columns
        data_dict = pd.read_excel(file_path, sheet_name=self.params['sheet_name_data_dict'], dtype='object')
        data_dict.columns = map(self.remove_spaces, data_dict.columns)

        # Fill missing values with np.nan
        for column in data_dict.columns:
            data_dict[column] = data_dict[column].fillna(np.nan)

        # Add columns to ignore to data dictionary
        for column in self.params['data_cols_ignore']:
            data_dict[column] = {
                'field_label': '',
                'field_type': 'string',
                'pandas_type': str,
                'option_group': None,
            }

        # Store field definitions in data dictionary
        for idx, row in data_dict.iterrows():
            var_name = row[self.params['data_dict_var_name']]
            if var_name != '':
                data_dict[var_name] = {
                    'field_label': row[self.params['data_dict_field_label']],
                    'field_type': row[self.params['data_dict_field_type']],
                    'pandas_type': self.params['to_pandas'][row[self.params['data_dict_field_type']]],
                    'option_group': row[self.params['data_dict_group_name']],
                }

        # Load data and remove spaces from columns
        data = pd.read_excel(file_path, sheet_name=self.params['sheet_name_data'])
        data.columns = map(self.remove_spaces, data.columns)

        for column in data.columns:

            # Convert column type to Pandas type
            pandas_type = self.params['to_pandas'][data_dict[column]['field_type']]
            data[column] = data[column].fillna(np.nan)
            data[column] = pd.Series(data=data[column], dtype=pandas_type)
            series = data[column]

            # Missing values for floats en dates are specific to Castor data. Let's
            # replace these with either np.nan or pd.NaT
            if pandas_type == 'float64':
                for mv in self.params['data_miss_float']:
                    series[series == mv] = np.nan
            elif pandas_type == 'datetime64[ns]':
                for mv in self.params['data_miss_date']:
                    series[series == mv] = pd.NaT
            else:
                pass

        # Load options and remove spaces from columns
        data_opts = pd.read_excel(file_path, sheet_name=self.params['sheet_name_data_opts'], dtype='object')
        data_opts.columns = map(self.remove_spaces, data_opts.columns)

        # Fill in missing values
        for column in data_opts.columns:
            data_opts[column] = data_opts[column].fillna(np.nan)

        for idx, row in data_opts.iterrows():

            # Store options in option dictionary
            option_group = row[self.params['data_opts_group_name']]
            if option_group not in list(data_opts.keys()):
                data_opts[option_group] = []
            data_opts[option_group].append(
                (int(row[self.params['data_opts_opt_val']]), row[self.params['data_opts_opt_name']]))

        return data, data_dict, data_opts


if __name__ == '__main__':
    CastorExportClient2()
