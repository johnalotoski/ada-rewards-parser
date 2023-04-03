#! /usr/bin/env python
"""Cardano Stake Rewards Parsing Tool via BlockFrost
Usage:
  bf-stake-parsing.py --stake ADDR --count COUNT --out FILE_OUT [--debug]

Options:
  --stake ADDR    Provide a shelley stake address in bech32 format to query on
  --count COUNT   The number of staking rewards epochs to return starting with the most recent
  --out FILE_OUT  The filename to output the processed data to, in CSV format
  --debug         Enable debug output.
  -h --help       Show this screen.
  --version       Show version.

Other Requirements:
  BF_API_KEY      An environment variable holding the blockfrost API key you wish to use
"""

from docopt import docopt
import csv
import datetime
import os
import requests

count = 0
key = ""

# Main
if __name__ == "__main__":

    arguments = docopt(__doc__, version="bf-stake-parsing 1.0.0")

    if arguments["--debug"]:
        print(arguments)

    if arguments["--count"]:
        try:
            count = int(arguments["--count"])
            if count < 1:
                raise ValueError
        except ValueError:
            print(f"ERROR: The specified \"--count\", ‘{arguments['--count']}’, must be a positive integer.")
            exit(1)

    key = os.environ.get("BF_API_KEY")
    if key is None:
        print("Environment variable BF_API_KEY must be set to query blockfrost API endpoints")
        exit(1)

    # Obtain rewards info
    url = f"https://cardano-mainnet.blockfrost.io/api/v0/accounts/{arguments['--stake']}/rewards"
    headers = {"project_id": key}
    params = {"order": "desc", "count": count}
    r = requests.get(url=url, params=params, headers=headers)

    # data format: [
    #   {
    #     'epoch': $EPOCH,
    #     'amount': '$LOVELACE',
    #     'pool_id': '$POOL_ID',
    #     'type': 'member'
    #   }
    # ]
    rewards = r.json()

    # Sort the rewards info by oldest rewards first
    rewards.sort(key=lambda x: x.get("epoch"))
    # The rewards data returned is actually paid out two epochs later
    oldest_epoch = rewards[0]["epoch"] + 2

    # Obtain epoch history info
    url2 = f"https://cardano-mainnet.blockfrost.io/api/v0/epochs/{oldest_epoch - 1}/next"
    params2 = {"count": count}
    r2 = requests.get(url=url2, params=params2, headers=headers)

    # epochs format: [
    #   {
    #     'epoch': $EPOCH,
    #     'start_time': $START_TS,
    #     'end_time': $END_TS,
    #     'first_block_time': $FIRST_BLOCK_TS,
    #     'last_block_time': $LAST_BLOCK_TS,
    #     'block_count': $BLOCK_COUNT,
    #     'tx_count': $TX_COUNT,
    #     'output': $OUTPUT,
    #     'fees': $FEES,
    #     'active_stake': $ACTIVE_STAKE
    #   }
    # ]
    epochs = r2.json()
    epochsDict = {epoch["epoch"]: datetime.datetime.fromtimestamp(epoch["first_block_time"], tz=datetime.timezone.utc) for epoch in epochs}

    outfile = open(arguments["--out"], "w")
    outwriter = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    for i in range(count + 1):
        if i == 0:
            rowout = ["Date", "Action", "Account", "Symbol", "Volume", "Total", "Currency", "Memo"]
        else:
            rowout = [
                epochsDict[rewards[i - 1]['epoch'] + 2],
                "mining",
                "Shelley",
                "ADA",
                int(rewards[i - 1]["amount"]) / 1000000,
                "",
                "",
                f"Stake rewards for epoch {rewards[i - 1]['epoch']} to pool {rewards[i - 1]['pool_id']}"
            ]
        outwriter.writerow(rowout)
    outfile.close()
exit(0)
