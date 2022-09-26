import pandas as pd


class CastorData:
    """ Class representing Castor data (liver or pancreas). The Excel also contains the
    data dictionary so date columns can be inferred from that.
    """
    def __init__(self, df, df_dict):
        self.df = df
        self.df_dict = df_dict
        self.date_columns = []
        for date_column in self.get_date_columns():
            self.df[date_column] = pd.to_datetime(
                self.df[date_column], errors='coerce', infer_datetime_format=True)
        self.prefix = self.infer_prefix()

    def infer_prefix(self):
        for c_name in self.df.columns:
            if c_name.startswith('dpca_'):
                return 'dpca_'
            if c_name.startswith('dhba_'):
                return 'dhba_'
        return None

    def get_column_names(self, remove_prefix='', add_prefix=''):
        if remove_prefix == '' and add_prefix == '':
            return self.df.columns
        if remove_prefix != '' and add_prefix != '':
            raise RuntimeError('Arguments remove_prefix and add_prefix cannot both be non-empty')
        column_names = []
        for c in self.df.columns:
            if remove_prefix != '':
                column_names.append(c.replace(remove_prefix, ''))
            else:
                column_names.append(add_prefix + c)
        return column_names

    def get_date_columns(self):
        if len(self.date_columns) > 0:
            return self.date_columns
        else:
            for idx, row in self.df_dict.iterrows():
                if row['Field type'] == 'date':
                    self.date_columns.append(row['Variable name'])
            return self.date_columns

    def get_last_surgery_date(self):
        self.df.sort_values(by=f'{self.prefix}datok')
        return self.df.iloc[-1, :][f'{self.prefix}datok']

    def get_last_record_id(self):
        return self.df.iloc[-1, 0]


class DicaData:
    """ Class representing DICA data. The new format Excel contains three tabs: patient,
    treatment and comorbidities. The patient and comorbidities data is merged with the
    treatment data to obtain a single data frame.
    """
    def __init__(self, df_pat, df_trt, df_com, df_dict_pat, df_dict_trt, df_dict_com):
        self.df_pat = df_pat
        self.df_trt = df_trt
        self.df_com = df_com
        self.prefix = None
        self.df_dict_pat = df_dict_pat
        self.df_dict_trt = df_dict_trt
        self.df_dict_com = df_dict_com
        self.date_columns = []
        for date_column in self.get_date_columns():
            if date_column in self.df_pat.columns:
                self.df_pat[date_column] = pd.to_datetime(self.df_pat[date_column], errors='coerce')
            if date_column in self.df_trt.columns:
                self.df_trt[date_column] = pd.to_datetime(self.df_trt[date_column], errors='coerce')
            if date_column in self.df_com.columns:
                self.df_com[date_column] = pd.to_datetime(self.df_com[date_column], errors='coerce')
        self.df_pat = self.df_pat.dropna(subset=['upn'])
        self.df_pat = self.df_pat.assign(gebjaar=self.df_pat['gebdat'].dt.year)
        self.df_trt = self.df_trt.dropna(subset=['verrichting_upn'])
        self.df_trt = self.df_trt.dropna(subset=['datok'])

    @staticmethod
    def get_patient_uri(patient_id, df):
        for idx, row in df.iterrows():
            if patient_id in row['upn']:
                return idx
        return None

    @staticmethod
    def get_comorbidities_uri(patient_uri, df):
        for idx, row in df.iterrows():
            if patient_uri == row['patient_uri']:
                return idx
        return None

    def get_date_columns(self):
        if len(self.date_columns) > 0:
            return self.date_columns
        else:
            for idx, row in self.df_dict_pat.iterrows():
                if row['TYPE'] == 'datum':
                    self.date_columns.append(row['VARIABELE NAAM'])
            for idx, row in self.df_dict_trt.iterrows():
                if row['TYPE'] == 'datum':
                    self.date_columns.append(row['VARIABELE NAAM'])
            for idx, row in self.df_dict_com.iterrows():
                if row['TYPE'] == 'datum':
                    self.date_columns.append(row['VARIABELE NAAM'])
            return self.date_columns

    def get_last_surgery_date(self):
        self.df.sort_values(by='datok')
        return self.df.iloc[-1, :]['datok']

    @property
    def df(self):
        return self.df_trt


class DpcaData(DicaData):

    def __init__(self, df_pat, df_trt, df_com, df_dict_pat, df_dict_trt, df_dict_com):
        super().__init__(df_pat, df_trt, df_com, df_dict_pat, df_dict_trt, df_dict_com)
        self.prefix = 'dpca_'
        data = {
            'treathosp': [],
            'geslacht': [],
            'gebdat': [],
            'gebjaar': [],
            'overl': [],
            'datovl': [],
            'datcom': [],
            'comlong': [],
            'commyo': [],
            'comhartfaal': [],
            'comperif': [],
            'comcva': [],
            'comparalys': [],
            'comdem': [],
            'comdiam': [],
            'comdiaminsu': [],
            'comgiulcus': [],
            'comlever': [],
            'compancr': [],
            'comnier': [],
            'combind': [],
            'comhiv': [],
            'commalig': [],
            'commal1': [],
            'commal2': [],
            'commal3': [],
            'commal4': [],
        }
        for idx, row in self.df_trt.iterrows():
            patient_id = row['verrichting_upn'].strip()
            patient_uri = self.get_patient_uri(patient_id, self.df_pat)
            if patient_uri is None:
                print(f'Could not find patient URI associated with ID {patient_id}')
                for c_name in data.keys():
                    if c_name == 'gebdat' or c_name == 'datovl' or c_name == 'datcom':
                        data[c_name].append(pd.NaT)
                    else:
                        data[c_name].append('')
                continue
            data['treathosp'].append('1')
            data['geslacht'].append(self.df_pat.loc[patient_uri]['geslacht'])
            data['gebdat'].append(self.df_pat.loc[patient_uri]['gebdat'])
            data['gebjaar'].append(self.df_pat.loc[patient_uri]['gebjaar'])
            datovl = self.df_pat.loc[patient_uri]['datovl']
            data['datovl'].append(datovl)
            if pd.isna(datovl):
                data['overl'].append('0')
            else:
                data['overl'].append('1')
            comorbiditeiten_uri = self.get_comorbidities_uri(patient_uri, self.df_com)
            if comorbiditeiten_uri is not None:
                data['datcom'].append(self.df_com.loc[comorbiditeiten_uri]['datcom'])
                for c_name in data.keys():
                    if c_name.startswith('com'):
                        data[c_name].append(self.df_com.loc[comorbiditeiten_uri][c_name])
            else:
                data['datcom'].append(pd.NaT)
                for c_name in data.keys():
                    if c_name.startswith('com'):
                        data[c_name].append('0')
        for k in data.keys():
            self.df_trt[k] = data[k]


class DhbaData(DicaData):

    def __init__(self, df_pat, df_trt, df_com, df_dict_pat, df_dict_trt, df_dict_com):
        super().__init__(df_pat, df_trt, df_com, df_dict_pat, df_dict_trt, df_dict_com)
        self.prefix = 'dhba_'
        data = {
            'treathosp': [],
            'geslacht': [],
            'gebdat': [],
            'gebjaar': [],
            'overl': [],
            'datovl': [],
            'datcom': [],
            'commyo': [],
            'comhartfaal': [],
            'comlong': [],
            'comperif': [],
            'comcva': [],
            'comdem': [],
            'comparalys': [],
            'combind': [],
            'comgiulcus': [],
            'comlever': [],
            'comcirrose': [],
            'comgalsteen': [],
            'compsc': [],
            'comdiam': [],
            'comnier': [],
            'comhiv': [],
            'commalig': [],
        }
        for idx, row in self.df_trt.iterrows():
            patient_id = row['verrichting_upn'].strip()
            patient_uri = self.get_patient_uri(patient_id, self.df_pat)
            if patient_uri is None:
                print(f'Could not find patient URI associated with ID {patient_id}')
                for c_name in data.keys():
                    if c_name == 'gebdat' or c_name == 'datovl' or c_name == 'datcom':
                        data[c_name].append(pd.NaT)
                    else:
                        data[c_name].append('')
                continue
            data['treathosp'].append('1')
            data['geslacht'].append(self.df_pat.loc[patient_uri]['geslacht'])
            data['gebdat'].append(self.df_pat.loc[patient_uri]['gebdat'])
            data['gebjaar'].append(self.df_pat.loc[patient_uri]['gebjaar'])
            datovl = self.df_pat.loc[patient_uri]['datovl']
            data['datovl'].append(datovl)
            if pd.isna(datovl):
                data['overl'].append('0')
            else:
                data['overl'].append('1')
            comorbiditeiten_uri = self.get_comorbidities_uri(patient_uri, self.df_com)
            if comorbiditeiten_uri is not None:
                data['datcom'].append(self.df_com.loc[comorbiditeiten_uri]['datcom'])
                for c_name in data.keys():
                    if c_name.startswith('com'):
                        data[c_name].append(self.df_com.loc[comorbiditeiten_uri][c_name])
            else:
                data['datcom'].append(pd.NaT)
                for c_name in data.keys():
                    if c_name.startswith('com'):
                        data[c_name].append('0')
        for k in data.keys():
            try:
                self.df_trt[k] = data[k]
            except ValueError as e:
                print(f'{k}: {str(e)}')
