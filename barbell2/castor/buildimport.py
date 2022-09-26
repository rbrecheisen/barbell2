import argparse
from barbell2.castor import loaders
from barbell2.castor import builders


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('castor_export', help='Castor export Excel file')
    parser.add_argument('dica_export', help='DHBA or DPCA export Excel data file')
    parser.add_argument('dica_dd', help='DHBA or DPCA data dictionary')
    parser.add_argument('output_dir', help='Output directory to store generated CSV files')
    args = parser.parse_args()
    cast_loader = loaders.CastorExportFileLoader(args.castor_export)
    cast_data = cast_loader.load()
    dica_loader = loaders.DicaExportFileLoader(args.dica_export, args.dica_dd)
    dica_data = dica_loader.load()
    builder = builders.CastorRecordBuilder(cast_data, dica_data)
    builder.execute()
    builder.save(args.output_dir)


def bla():
    cast_loader = loaders.CastorExportFileLoader('/Users/Ralph/data/surfdrive/documents/hpb/castor/data/exports/castoredc/ESPRESSO_v2.0_DHBA_excel_export_20220926102336.xlsx')
    cast_data = cast_loader.load()
    dica_loader = loaders.DicaExportFileLoader(
        '/Users/Ralph/data/surfdrive/documents/hpb/castor/data/exports/dhba/dhba_2022.academisch-ziekenhuis-maastricht.xlsx',
        '/Users/Ralph/data/surfdrive/documents/hpb/castor/data/data_dicitionaries/dhba/dhba-2022_1.1.0_datadictionary_20211001_122752.xlsx',
    )
    dica_data = dica_loader.load()
    builder = builders.CastorRecordBuilder(cast_data, dica_data)
    builder.execute()
    builder.save('/Users/Ralph/Desktop/buildcastorimport')


if __name__ == '__main__':
    bla()
