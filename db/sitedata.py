import os
import sqlite3
from dotenv import load_dotenv
import datetime

load_dotenv()

class SiteData:

    def __init__(self, host):
        self.db_folder = os.environ.get('DATA_FOLDER', '')
        if self.db_folder == '':
            raise ValueError('DATA_FOLDER environment variable not set')

        self.host = host
        self.db_name = os.path.join(self.db_folder, f'{host}.db')
        self.connect()
        self.create_table()

    def connect(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    def create_table(self):
        cmd = 'CREATE TABLE IF NOT EXISTS data ( ' + \
               ' ip_timestamp TEXT PRIMARY KEY, ' + \
               ' IP TEXT, ' + \
               ' timestamp TEXT, ' + \
               ' desc TEXT, ' + \
               ' temp_f REAL ' + \
               ' ) '
        self.cursor.execute(cmd)
        self.conn.commit()

    def insert_record(self, host, temp_f, desc = None):
        if desc is None:
            desc = ''
        timestamp = datetime.datetime.now().isoformat()
        ip_timestamp = f'{host}-{timestamp}'

        self.cursor.execute('''
            INSERT INTO data (ip_timestamp, IP, timestamp, desc, temp_f)
            VALUES (?, ?, ?, ?, ?)
        ''', (ip_timestamp, host, timestamp, desc, temp_f))
        self.conn.commit()

    def remove_older_than(self, days=365):
        timestamp = datetime.datetime.now() - datetime.timedelta(days=days)
        timestamp = timestamp.isoformat()
        self.cursor.execute('DELETE FROM data WHERE timestamp < ? ', (timestamp,))
        self.conn.commit()

    def get_data(self, host, days=1):
        timestamp = datetime.datetime.now() - datetime.timedelta(days=days)
        timestamp = timestamp.isoformat()
        self.cursor.execute('SELECT * FROM data WHERE IP = ? AND timestamp > ? ', (host, timestamp,))
        return self.cursor.fetchall()

    def get_24hrs_data(self, host):
        data = self.get_data(host, days=1)
        return data

    def get_7days_data(self, host):
        data = self.get_data(host, days=7)
        return data

    def get_most_recent_data(self, host):
        self.cursor.execute('SELECT * FROM data WHERE IP = ? ORDER BY timestamp DESC LIMIT 1', (host,))
        return self.cursor.fetchone()

