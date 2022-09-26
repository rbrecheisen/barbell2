import pandas as pd
from barbell2.castor import data


class CastorExportFileLoader:

    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None

    def load(self):
        print('Loading Castor data...')
        df = pd.read_excel(self.file_path, dtype=str, engine='openpyxl', sheet_name='Study results')
        print('Loading Castor data dictionary...')
        df_dict = pd.read_excel(self.file_path, dtype=str, engine='openpyxl', sheet_name='Study variable list')
        self.data = data.CastorData(df, df_dict)
        return self.data


class DicaExportFileLoader:

    def __init__(self, file_path_data, file_path_dict):
        self.file_path_data = file_path_data
        self.file_path_dict = file_path_dict
        self.audit = None
        if 'dpca' in self.file_path_data:
            self.audit = 'DPCA'
        if 'dhba' in self.file_path_data:
            self.audit = 'DHBA'
        self.data = None

    def load(self):
        if self.file_path_data.endswith('.xls'):
            raise RuntimeError('Data must be recent Excel format (*.xlsx)')
        if self.file_path_dict.endswith('.xls'):
            raise RuntimeError('Data dictionary must be recent format (*.xlsx)')
        print(f'Loading {self.audit} data...')
        df_pat = pd.read_excel(self.file_path_data, dtype=str, sheet_name='patient', engine='openpyxl', index_col='uri')
        df_trt = pd.read_excel(self.file_path_data, dtype=str, sheet_name='verrichting', engine='openpyxl', index_col='uri')
        df_com = pd.read_excel(self.file_path_data, dtype=str, sheet_name='comorbiditeiten', engine='openpyxl', index_col='uri')
        print(f'Loading {self.audit} data dictionary...')
        df_dict_pat = pd.read_excel(self.file_path_dict, dtype=str, sheet_name='patient', engine='openpyxl')
        df_dict_trt = pd.read_excel(self.file_path_dict, dtype=str, sheet_name='verrichting', engine='openpyxl')
        df_dict_com = pd.read_excel(self.file_path_dict, dtype=str, sheet_name='comorbiditeiten', engine='openpyxl')
        if self.audit == 'DPCA':
            self.data = data.DpcaData(df_pat, df_trt, df_com, df_dict_pat, df_dict_trt, df_dict_com)
        if self.audit == 'DHBA':
            self.data = data.DhbaData(df_pat, df_trt, df_com, df_dict_pat, df_dict_trt, df_dict_com)
        return self.data
