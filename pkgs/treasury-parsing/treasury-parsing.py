#! /usr/bin/env python
"""Cardano Treasury Parsing Tool
Usage:
  treasury-parsing.py --stake ADDR --out FILE_OUT --from DATE --to DATE [--debug]
  treasury-parsing.py --in FILE_IN --out FILE_OUT [--debug]

Options:
  --stake ADDR    Provide a shelley stake address in bech32 format to query on
  --from DATE     Provide a start date to sql query on in format YYYY-MM-DD
  --to DATE       Provide an end date to sql query on in format YYYY-MM-DD
  --in FILE_IN    Provide a CSV file for reading which includes a header
  --out FILE_OUT  Provide a CSV file for writing to
  --debug         Enable debug output.
  -h --help       Show this screen.
  --version       Show version.
"""

from docopt import docopt
import csv
import os
import subprocess

# Main
if __name__ == "__main__":

    arguments = docopt(__doc__, version="treasury-parsing 1.0.0")

    if arguments["--debug"]:
        print(arguments)

    if arguments["--in"] and not os.access(arguments["--in"], os.R_OK):
        print(f"ERROR: The specified \"--in\" file, ‘{arguments['--in']}’, doesn't exist.")
        exit(1)

    if os.path.exists(arguments["--out"]):
        print(f"ERROR: The specified \"--out\" file, ‘{arguments['--out']}’, already exists, please choose another file.")
        exit(1)

    if arguments["--stake"]:
        treasury_query = "SELECT amount / 1E6 as ada, time, tx.hash, epoch_no, epoch_slot_no, block_no " \
                         + "FROM treasury INNER JOIN stake_address ON stake_address.id=treasury.addr_id " \
                         + "INNER JOIN tx on tx_id=tx.id " \
                         + "INNER JOIN block ON block_id=block.id " \
                         + f"WHERE stake_address.view = '{arguments['--stake']}' and " \
                         + f"time >= '{arguments['--from']}' and time <= '{arguments['--to']}'"
        try:
            sql_result = subprocess.run(
                f'psql -U postgres cdbsync -c "COPY ({treasury_query}) TO STDOUT WITH CSV HEADER"',
                shell=True,
                check=False,
                universal_newlines=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except Exception:
            raise Exception(
                "EXCEPTION: Unable to query SQL successfully"
            )
        infile = sql_result.stdout.splitlines()
    else:
        infile = open(arguments["--in"], "r")

    outfile = open(arguments["--out"], "w")
    outwriter = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    header = {}
    rows = csv.reader(infile, delimiter=',', quotechar='"')
    for i, row in enumerate(rows):
        # If the header row, create a dictionary to element index: Dict[field_name: str -> csv_index: int]
        if i == 0:
            for j, element in enumerate(row):
                header[row[j]] = j
            rowout = ["Date", "Action", "Account", "Symbol", "Volume", "Total", "Currency", "Memo"]
        else:
            hash = row[header['hash']].lstrip("\\x")
            rowout = [
                f"{row[header['time']]} Z",
                "income",
                "Shelley",
                "ADA",
                row[header["ada"]],
                "",
                "",
                f"Treasury rewards at epoch {row[header['epoch_no']]} slot {row[header['epoch_slot_no']]} block {row[header['block_no']]} with tx id {hash}"
            ]
        outwriter.writerow(rowout)
    outfile.close()

    if arguments["--in"]:
        infile.close()
exit(0)
