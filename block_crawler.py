import sys
import json
import requests
import datetime
from datetime import timezone
import sqlite3
#import MySQLdb #Uncomment to use with MySQL
from sqlalchemy import create_engine

def read_blocks(json_rpc_endpoint, block_range):
    try:
        start_block, end_block = map(int, block_range.split('-'))
    except ValueError:
        raise ValueError("Invalid block range format. Please provide a range in the format 'start-end'.")
    
    transactions = {}

    for block_number in range(start_block, end_block + 1):
        payload = {
            "method": "eth_getBlockByNumber",
            "params": [hex(block_number), True],
            "id": 1,
            "jsonrpc": "2.0"
        }

        # HTTP POST request
        try:
            response = requests.post(json_rpc_endpoint, json=payload)
            response.raise_for_status()
            data = response.json()
            transactions[hex(block_number)] = (data['result']['timestamp'], data['result']['transactions'])
        except requests.exceptions.HTTPError as err:
            print("HTTP Error:", err)
            sys.exit(1)
        except json.decoder.JSONDecodeError as json_err:
            print(f"JSON parsing error on {block_number}:", json_err)
  
    return transactions

def load_transactions(transactions, db_file):
    try:
        if db_file.startswith("postgresql://") or db_file.startswith("mysql://"): # connection URI
                engine = create_engine(db_file)
                connection = engine.connect()
        else: # sqlite file
            connection = sqlite3.connect(db_file)
    except Exception as e:
        print("DB Connection Error:", e)
        sys.exit(1)
    connection.execute('''DROP TABLE IF EXISTS blocks''')
    connection.execute('''CREATE TABLE IF NOT EXISTS blocks (
                    block_hex TEXT PRIMARY KEY,
                    block_timestamp TEXT
                )''')
    connection.execute('''DROP TABLE IF EXISTS transactions''')
    connection.execute('''CREATE TABLE IF NOT EXISTS transactions (
                    block_hex TEXT,
                    transaction_data TEXT,
                    transaction_value INTEGER
                )''')
    # iterate dict and insert entries
    for block_hex, (block_epoch, transaction_data) in transactions.items():
        block_timestamp = datetime.datetime.fromtimestamp(int(block_epoch, 16), timezone.utc)
        connection.execute('''INSERT INTO blocks (block_hex, block_timestamp)
                            VALUES (?, ?)''', (block_hex, block_timestamp))
        for transaction in transaction_data:
            connection.execute('''INSERT INTO transactions (block_hex, transaction_data, transaction_value)
                            VALUES (?, ?, ?)''', (block_hex, str(transaction), float(int(transaction['value'], 16)) / 10**18))
    connection.commit()
    connection.close()

if __name__ == "__main__":

    # Command line arguments
    if len(sys.argv) != 4:
        print("Usage: python block_crawler.py <json_rpc_endpoint> <db_file> <block_range>")
        sys.exit(1)

    json_rpc_endpoint = sys.argv[1]
    db_file = sys.argv[2]
    block_range = sys.argv[3]
    try:
        transactions = read_blocks(json_rpc_endpoint, block_range)
        load_transactions(transactions, db_file)
        print(f"All transactions from block range {block_range} have been loaded")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
