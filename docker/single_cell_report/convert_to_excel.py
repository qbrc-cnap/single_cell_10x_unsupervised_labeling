#! /usr/bin/python3

import argparse
import pandas as pd


def main():
    '''Converts CSVs to a multi-sheet Excel file.'''
    desc="Converts CSVs to multi-sheet Excel."
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("-o", "--output", metavar="FILENAME", required=True,
                        help="Name of output Excel file")
    parser.add_argument("csv", metavar="CSV", nargs="+",
                        help="Input CSV text files")
    args = parser.parse_args()
    writer = pd.ExcelWriter(args.output)
    for csv in args.csv:
        sheet_name = csv.split('/')[-2]
        df = pd.read_csv(csv)
        df.to_excel(writer, sheet_name=sheet_name)
    writer.save() # closes the object and saves the output


if __name__ == "__main__":
    main()
