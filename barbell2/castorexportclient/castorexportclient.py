import json
import pandas as pd
import numpy as np


class CastorExportClient:

    def __init__(self, show_params=True):
        """
        Constructs instance of this class.
        :param show_params: Whether to print parameters or not (default True)
        """
        self.params = {
            'sheet_name_data': 'Study results',                 # with spaces
            'sheet_name_data_dict': 'Study variable list',      # ''
            'sheet_name_data_options': 'Field options',         # ''
            'data_dict_crf_name': 'Step_name',                  # without spaces because column names are updated
            'data_dict_var_name': 'Variable_name',              # ''
            'data_dict_field_type': 'Field_type',               # ''
            'data_dict_field_label': 'Field_label',             # ''
            'data_dict_option_group_name': 'Optiongroup_name',  # ''
            'data_options_group_name': 'Option_group_name',     # ''
            'data_options_name': 'Option_name',                 # ''
            'data_options_value': 'Option_value',               # ''
            'data_cols_ignore': [
                'Record_Id',                                    # without spaces because column names are updated
                'Institute_Abbreviation',                       # ''
                'Record_Creation_Date',                         # ''
            ],
            'patient_id_field_name': 'dpca_idcode',
            'surgery_date_field_name': 'dpca_datok',
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

        if show_params:
            print(json.dumps(self.params, indent=4))

        self.data = None
        self.data_dict = {}
        self.data_options = {}

    @staticmethod
    def remove_spaces(value):
        """
        Removes spaces from given value and replaces them with underscores.
        :param value: Value to process
        :return: Processed value
        """
        return value.replace(' ', '_')

    def to_pandas_type(self, field_type):
        """
        Lookup Pandas data type for given Castor field type.
        :param field_type: Castor field type name
        :return: Corresponding Pandas data type or None if not found
        """
        if field_type in list(self.params['to_pandas'].keys()):
            return self.params['to_pandas'][field_type]
        return None

    def load_data(self, file_path):
        """
        Loads Castor export Excel file containing the data, data dictionary and field options.
        :param file_path: Path to Excel file
        :return: Tuple of data, data dictionary and options
        """
        # Load data dictionary first and remove spaces from columns
        df_data_dict = pd.read_excel(file_path, sheet_name=self.params['sheet_name_data_dict'], dtype='object')
        df_data_dict.columns = map(self.remove_spaces, df_data_dict.columns)

        # Fill missing values with np.nan
        for column in df_data_dict.columns:
            df_data_dict[column] = df_data_dict[column].fillna(np.nan)

        data_dict = {}

        # Add columns to ignore to data dictionary
        for column in self.params['data_cols_ignore']:
            data_dict[column] = {
                'crf_name': '',
                'field_label': column,
                'field_type': 'string',
                'pandas_type': 'object',
                'option_group_name': None,
            }

        # Store field definitions in data dictionary
        for idx, row in df_data_dict.iterrows():
            var_name = row[self.params['data_dict_var_name']]
            if var_name is None or var_name == '' or pd.isna(var_name):
                continue
            data_dict[var_name] = {
                'crf_name': row[self.params['data_dict_crf_name']],
                'field_label': row[self.params['data_dict_field_label']],
                'field_type': row[self.params['data_dict_field_type']],
                'pandas_type': self.to_pandas_type(row[self.params['data_dict_field_type']]),
                'option_group_name': row[self.params['data_dict_option_group_name']],
            }

        self.data_dict = data_dict

        # Load data and remove spaces from columns
        df_data = pd.read_excel(file_path, sheet_name=self.params['sheet_name_data'])
        df_data.columns = map(self.remove_spaces, df_data.columns)

        for column in df_data.columns:

            if column not in self.data_dict.keys():
                continue

            # Convert column type to Pandas type
            pandas_type = self.to_pandas_type(self.data_dict[column]['field_type'])
            df_data[column] = df_data[column].fillna(np.nan)
            df_data[column] = pd.Series(data=df_data[column], dtype=pandas_type)

            # Missing values for floats en dates are specific to Castor data. Let's
            # replace these with either np.nan or pd.NaT
            if pandas_type == 'float64':
                for mv in self.params['data_miss_float']:
                    df_data.loc[df_data[column] == mv, column] = np.nan
            elif pandas_type == 'datetime64[ns]':
                for mv in self.params['data_miss_date']:
                    df_data.loc[df_data[column] == mv, column] = pd.NaT
            else:
                pass

        self.data = df_data

        # Load options and remove spaces from columns
        df_data_options = pd.read_excel(file_path, sheet_name=self.params['sheet_name_data_options'], dtype='object')
        df_data_options.columns = map(self.remove_spaces, df_data_options.columns)

        # Fill in missing values
        for column in df_data_options.columns:
            df_data_options[column] = df_data_options[column].fillna(np.nan)

        data_options = {}

        for idx, row in df_data_options.iterrows():

            # Store options in option dictionary
            option_group = row[self.params['data_options_group_name']]
            if option_group not in list(data_options.keys()):
                data_options[option_group] = []
            data_options[option_group].append(
                (int(row[self.params['data_options_value']]), row[self.params['data_options_name']]))

        self.data_options = data_options

        return self.data, self.data_dict, self.data_options

    def find_option_group(self, text=''):
        """
        Finds option groups and corresponding option values for the given option name.
        :param text: (Part of) option name or group name (default='' returns all options groups)
        """
        option_groups = {}
        for option_group, options in self.data_options.items():
            if text.lower() in option_group.lower():
                option_groups[option_group] = options
                continue
            for option in options:
                if text.lower() in option[1].lower():
                    option_groups[option_group] = options
        return option_groups

    def find_variable(self, text=''):
        """
        Finds variable definitions that contain <text> in either the name or label. Info returned
        contains: CRF name, field label, field type, Pandas type and option group name (if applicable).
        :param text: (Part of) variable name or label (default='' returns all variable definitions)
        """
        definitions = []
        for name, definition in self.data_dict.items():
            if text.lower() in name.lower():
                definitions.append((name, definition))
        return definitions

    def find_missing(self, in_column, show_columns):
        """
        Finds records with missing values in column <in_column>. Each record is displayed as indicated
        by <show_columns>
        :param in_column: Column that is searched for missing values.
        :param show_columns: List of column names to show when displaying records with missing values.
        :return:
        """
        pass

    def find_duplicate_records(self):
        """
        Finds duplicate records in the export file.
        :return: Dictionary with patient ID, gender, date of birth and surgery date
        """
        duplicates = {}
        for idx, row in self.data.iterrows():
            surgery_date = row[self.params['surgery_date_field_name']]
            surgery_date = '{}-{}-{}'.format(surgery_date.year, surgery_date.month, surgery_date.day)
            key = (row[self.params['patient_id_field_name']], surgery_date)
            if key not in duplicates.keys():
                duplicates[key] = 0
            duplicates[key] += 1
        return duplicates


if __name__ == '__main__':
    CastorExportClient()
