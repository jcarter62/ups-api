import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

class SystemsDB:
    def __init__(self):
        self.db_name = os.environ.get('SYSTEMSDB', '')
        if self.db_name == '':
            raise ValueError('SYSTEMSDB environment variable not set')

        self.conn = None
        self.cursor = None
        self.connect()
        self.create_table()

    def connect(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS systems (
                IP TEXT PRIMARY KEY,
                Desc1_oid TEXT,
                Desc2_oid TEXT,
                Temp_f_oid TEXT
            )
        ''')
        self.conn.commit()

    def insert_record(self, IP, Desc1_oid, Desc2_oid, Temp_f_oid):
        self.cursor.execute('''
            INSERT INTO systems (IP, Desc1_oid, Desc2_oid, Temp_f_oid)
            VALUES (?, ?, ?, ?)
        ''', (IP, Desc1_oid, Desc2_oid, Temp_f_oid))
        self.conn.commit()

    def update_record(self, IP, Desc1_oid=None, Desc2_oid=None, Temp_f_oid=None):
        query = "UPDATE systems SET "
        params = []
        if Desc1_oid is not None:
            query += "Desc1_oid = ?, "
            params.append(Desc1_oid)
        if Desc2_oid is not None:
            query += "Desc2_oid = ?, "
            params.append(Desc2_oid)
        if Temp_f_oid is not None:
            query += "Temp_f_oid = ?, "
            params.append(Temp_f_oid)

        # Remove the last comma and space
        query = query.rstrip(', ')
        query += " WHERE IP = ?"
        params.append(IP)

        self.cursor.execute(query, tuple(params))
        self.conn.commit()

    def delete_record(self, IP):
        self.cursor.execute('''
            DELETE FROM systems WHERE IP = ?
        ''', (IP,))
        self.conn.commit()

    def query_all_records(self):
        self.cursor.execute('''
            SELECT * FROM systems
        ''')
        return self.cursor.fetchall()

    def query_record_by_ip(self, IP):
        self.cursor.execute('''
            SELECT * FROM systems WHERE IP = ?
        ''', (IP,))
        return self.cursor.fetchone()

    def close(self):
        self.conn.close()

# Usage example
if __name__ == "__main__":
    db = SystemsDB()

    'Addr1=192.168.2.65,OID=.1.3.6.1.2.1.1.5.0,OID=.1.3.6.1.2.1.1.6.0,OID=.1.3.6.1.4.1.318.1.1.25.1.2.1.5.1.1'

    # Insert a record
    db.insert_record('192.168.2.65', '.1.3.6.1.2.1.1.5.0', '.1.3.6.1.2.1.1.6.0', '.1.3.6.1.4.1.318.1.1.25.1.2.1.5.1.1')

    # Query all records
    records = db.query_all_records()
    for record in records:
        print(record)

    # # Update a record
    # db.update_record('192.168.1.1', Desc1_oid='New Description 1')
    #
    # # Query a specific record
    # record = db.query_record_by_ip('192.168.1.1')
    # print(record)
    #

    # Delete a record
    db.delete_record('192.168.1.1')

    # Close the database connection
    db.close()
