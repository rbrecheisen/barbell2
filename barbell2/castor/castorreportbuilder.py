import pandas as pd


class CastorReportBuilder:

    HTML = 0

    def __init__(self, df, output_format=HTML):
        self.df = df
        self.output_format = output_format

    def execute(self):
        pass


if __name__ == '__main__':
    def main():
        builder = CastorReportBuilder()
        builder.execute()
    main()
