# Ethereum Mainnet Block Crawler

Python program and SQL script to persist and query Etherium Mainnet blockchain data using SQLite

## Installation

In order to run block_crawler.py, please include the following dependencies

pip install requests
pip install sqlalchemy

To use MySQL for data storage (optional):
pip install mysqlclient

## Usage

- Usage: python block_crawler.py <json_rpc_endpoint> <db_file> <block_range>

- Example: python block_crawler.py https://rpc.quicknode.pro/key db.sqlite3 200-300

- Usage for Top Volume SQL Report: sqlite3 <db_file> < top_volume.sql