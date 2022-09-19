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
        self.df.sort_values(by='dpca_datok')
        return self.df.iloc[-1, :]['dpca_datok']

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
            comorbiditeiten_uri = self.get_comorbidities_uri(patient_uri, self.df_com)
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
            if comorbiditeiten_uri is not None:
                data['datcom'].append(self.df_com.loc[comorbiditeiten_uri]['datcom'])
                data['comlong'].append(self.df_com.loc[comorbiditeiten_uri]['comlong'])
                data['commyo'].append(self.df_com.loc[comorbiditeiten_uri]['commyo'])
                data['comhartfaal'].append(self.df_com.loc[comorbiditeiten_uri]['comhartfaal'])
                data['comperif'].append(self.df_com.loc[comorbiditeiten_uri]['comperif'])
                data['comcva'].append(self.df_com.loc[comorbiditeiten_uri]['comcva'])
                data['comparalys'].append(self.df_com.loc[comorbiditeiten_uri]['comparalys'])
                data['comdem'].append(self.df_com.loc[comorbiditeiten_uri]['comdem'])
                data['comdiam'].append(self.df_com.loc[comorbiditeiten_uri]['comdiam'])
                data['comdiaminsu'].append(self.df_com.loc[comorbiditeiten_uri]['comdiaminsu'])
                data['comgiulcus'].append(self.df_com.loc[comorbiditeiten_uri]['comgiulcus'])
                data['comlever'].append(self.df_com.loc[comorbiditeiten_uri]['comlever'])
                data['compancr'].append(self.df_com.loc[comorbiditeiten_uri]['compancr'])
                data['comnier'].append(self.df_com.loc[comorbiditeiten_uri]['comnier'])
                data['combind'].append(self.df_com.loc[comorbiditeiten_uri]['combind'])
                data['comhiv'].append(self.df_com.loc[comorbiditeiten_uri]['comhiv'])
                data['commalig'].append(self.df_com.loc[comorbiditeiten_uri]['commalig'])
                data['commal1'].append(self.df_com.loc[comorbiditeiten_uri]['commal1'])
                data['commal2'].append(self.df_com.loc[comorbiditeiten_uri]['commal2'])
                data['commal3'].append(self.df_com.loc[comorbiditeiten_uri]['commal3'])
                data['commal4'].append(self.df_com.loc[comorbiditeiten_uri]['commal4'])
            else:
                data['datcom'].append(pd.NaT)
                data['comlong'].append('0')
                data['commyo'].append('0')
                data['comhartfaal'].append('0')
                data['comperif'].append('0')
                data['comcva'].append('0')
                data['comparalys'].append('0')
                data['comdem'].append('0')
                data['comdiam'].append('0')
                data['comdiaminsu'].append('0')
                data['comgiulcus'].append('0')
                data['comlever'].append('0')
                data['compancr'].append('0')
                data['comnier'].append('0')
                data['combind'].append('0')
                data['comhiv'].append('0')
                data['commalig'].append('0')
                data['commal1'].append('0')
                data['commal2'].append('0')
                data['commal3'].append('0')
                data['commal4'].append('0')
        for k in data.keys():
            self.df_trt[k] = data[k]
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
