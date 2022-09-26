import argparse
import loaders
import builders


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('castor-export', help='Castor export Excel file')
    parser.add_argument('dica-export', help='DHBA or DPCA export Excel data file')
    parser.add_argument('dica-dd', help='DHBA or DPCA data dictionary')
    parser.add_argument('output-dir', help='Output directory to store generated CSV files')
    args = parser.parse_args()
    cast_loader = loaders.CastorExportFileLoader(args.castor_export)
    cast_data = cast_loader.load()
    dica_loader = loaders.DicaExportFileLoader(args.dica_export, args.dica_dd)
    dica_data = dica_loader.load()
    builder = builders.CastorRecordBuilder(cast_data, dica_data)
    builder.execute()
    builder.save(args.output_dir)


main()
