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

    def get_data(self, days=1):
        timestamp = datetime.datetime.now() - datetime.timedelta(days=days)
        timestamp = timestamp.isoformat()
        self.cursor.execute('SELECT * FROM data WHERE timestamp > ? ', (timestamp,))
        return self.cursor.fetchall()

    def get_24hrs_data(self):
        data = self.get_data(days=1)
        return data

    def get_7days_data(self):
        data = self.get_data(days=7)
        return data

    def get_most_recent_data(self):
        sqlcmd = 'SELECT * FROM data ORDER BY timestamp DESC LIMIT 1'
        self.cursor.execute(sqlcmd)
        rslt = self.cursor.fetchone()
        return rslt


    def get_average_hourly(self, days: int = 1):
        timestamp = datetime.datetime.now() - datetime.timedelta(days=days)
        timestamp = timestamp.isoformat()

        self.cursor.execute('''
            SELECT strftime('%Y-%m-%d %H', timestamp) as hour, 
                   AVG(temp_f) as avg_temp, 
                   MAX(temp_f) as max_temp, 
                   MIN(temp_f) as min_temp
            FROM data 
            WHERE timestamp > ? 
            GROUP BY hour
            ORDER BY hour
        ''', (timestamp,))

        rslts = []
        for row in self.cursor.fetchall():
            rslts.append({
                'hour': row[0],
                'avg_temp': f"{row[1]:.2f}",
                'max_temp': f"{row[2]:.2f}",
                'min_temp': f"{row[3]:.2f}"
            })

        return rslts
