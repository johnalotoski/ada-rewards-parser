#! /usr/bin/env python
"""Cardano Stake Rewards Parsing Tool
Usage:
  stake-parsing.py --stake ADDR --out FILE_OUT --from DATE --to DATE [--debug]
  stake-parsing.py --in FILE_IN --out FILE_OUT [--debug]

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

    arguments = docopt(__doc__, version="stake-parsing 1.0.0")

    if arguments["--debug"]:
        print(arguments)

    if arguments["--in"] and not os.access(arguments["--in"], os.R_OK):
        print(f"ERROR: The specified \"--in\" file, ‘{arguments['--in']}’, doesn't exist.")
        exit(1)

    if os.path.exists(arguments["--out"]):
        print(f"ERROR: The specified \"--out\" file, ‘{arguments['--out']}’, already exists, please choose another file.")
        exit(1)

    if arguments["--stake"]:
        staking_query = "with rewards AS (select reward.epoch_no, pool_hash.view as delegated_pool, " \
                        + "reward.amount / 1E6 as ada, epoch_no + 2 as epoch_paid, epoch.start_time as paid_time " \
                        + "from reward inner join stake_address on reward.addr_id = stake_address.id " \
                        + "inner join pool_hash on reward.pool_id = pool_hash.id " \
                        + "inner join epoch on (reward.epoch_no + 2) = epoch.no " \
                        + f"where stake_address.view = '{arguments['--stake']}' " \
                        + "order by epoch_no asc) select * from rewards " \
                        + f"where paid_time >= '{arguments['--from']}' and paid_time <= '{arguments['--to']}'"
        try:
            sql_result = subprocess.run(
                f'psql -U postgres cdbsync -c "COPY ({staking_query}) TO STDOUT WITH CSV HEADER"',
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
            rowout = [
                f"{row[header['paid_time']]} Z",
                "mining",
                "Shelley",
                "ADA",
                row[header["ada"]],
                "",
                "",
                f"Stake rewards for epoch {row[header['epoch_no']]} to pool {row[header['delegated_pool']]}"
            ]
        outwriter.writerow(rowout)
    outfile.close()

    if arguments["--in"]:
        infile.close()
exit(0)
