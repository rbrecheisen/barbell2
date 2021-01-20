import pandas as pd
import numpy as np


SHEET_NAME_STUDY_RESULTS = 'Study results'
SHEET_NAME_STUDY_VARS = 'Study variable list'
SHEET_NAME_STUDY_OPTS = 'Field options'

DATA_DICT_VARIABLE_NAME = 'Variable_name'
DATA_DICT_FIELD_TYPE = 'Field_type'
DATA_DICT_FIELD_LABEL = 'Field_label'
DATA_DICT_OPTION_GROUP_NAME = 'Optiongroup_name'

OPTIONS_OPTION_GROUP_NAME = 'Option_group_name'
OPTIONS_OPTION_NAME = 'Option_name'
OPTIONS_OPTION_VALUE = 'Option_value'

FIELD_TO_PANDAS_TYPES = {
    'dropdown': 'category',
    'string': 'object',
    'radio': 'category',
    'date': 'datetime64[ns]',
    'year': 'Int64',
    'textarea': 'object',
    'numeric': 'float64',
    'remark': 'object',
}

MISSING_VALUES_FLOAT64 = [999, 9999, 999.0, 9999.0]
MISSING_VALUES_DATETIME64 = []

EXTRA_COLUMNS = ['Record_Id', 'Institute_Abbreviation', 'Record_Creation_Date']


class CastorExportClient:

    def __init__(self):
        self.export = None
        self.data_dict = {}
        self.options = {}

    def load_export(self,
                    file_path,
                    study_results=SHEET_NAME_STUDY_RESULTS,
                    study_vars=SHEET_NAME_STUDY_VARS,
                    study_opts=SHEET_NAME_STUDY_OPTS
                    ):

        def rename_col(col):
            return col.replace(' ', '_')

        def pandas_type(field_type):
            if field_type in list(FIELD_TO_PANDAS_TYPES.keys()):
                return FIELD_TO_PANDAS_TYPES[field_type]
            return None

        # Load data dictionary as Python dict
        data_dict = pd.read_excel(file_path, sheet_name=study_vars, dtype='object')
        data_dict.columns = map(rename_col, data_dict.columns)
        for column in data_dict.columns:
            data_dict[column] = data_dict[column].fillna(np.nan)
        for column in EXTRA_COLUMNS:
            self.data_dict[column] = {
                'field_label': '',
                'field_type': 'string',
                'pandas_type': str,
                'option_group': None,
            }
        for idx, row in data_dict.iterrows():
            var_name = row[DATA_DICT_VARIABLE_NAME]
            if var_name != '':
                self.data_dict[var_name] = {
                    'field_label': row[DATA_DICT_FIELD_LABEL],
                    'field_type': row[DATA_DICT_FIELD_TYPE],
                    'pandas_type': pandas_type(row[DATA_DICT_FIELD_TYPE]),
                    'option_group': row[DATA_DICT_OPTION_GROUP_NAME],
                }

        # Load data as Pandas data frame and set column type according to data dictionary
        self.export = pd.read_excel(file_path, sheet_name=study_results)
        self.export.columns = map(rename_col, self.export.columns)
        for column in self.export.columns:
            pt = pandas_type(self.data_dict[column]['field_type'])
            self.export[column] = self.export[column].fillna(np.nan)
            self.export[column] = pd.Series(data=self.export[column], dtype=pt)
            series = self.export[column]
            if pt == 'float64':
                for mv in MISSING_VALUES_FLOAT64:
                    series[series == mv] = np.nan
            elif pt == 'datetime64[ns]':
                for mv in MISSING_VALUES_DATETIME64:
                    series[series == mv] = pd.NaT

        # Load options as Python dict
        options = pd.read_excel(file_path, sheet_name=study_opts, dtype='object')
        options.columns = map(rename_col, options.columns)
        for column in options.columns:
            options[column] = options[column].fillna(np.nan)
        for idx, row in options.iterrows():
            option_group = row[OPTIONS_OPTION_GROUP_NAME]
            if option_group not in list(self.options.keys()):
                self.options[option_group] = []
            self.options[option_group].append((int(row[OPTIONS_OPTION_VALUE]), row[OPTIONS_OPTION_NAME]))

    def save(self, output_file):
        self.export.to_csv(output_file, index=False)
