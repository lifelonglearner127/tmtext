#!/usr/bin/env python
import logging
import sqlite3
import os
import datetime
import json

LOG = logging.getLogger(__name__)

COMMAND = 'command'
SPIDER = 'spider'

class DbInterface(object):
    """Class to handle requests persistency

    It is implemented using sqlite3 backend
    """

    def __init__(self, filename, recreate=False):
        """Constructor

        * filename: where the DB will be store. Can be ':memory:' to store
          it on memory.
        * recreate: if True, erase all previous content
        """
        if recreate and filename.lower() != ':memory:':
            self._erase_file(filename)

        self.filename = filename
        self._recreate = recreate
        self._conn = self._open_dbconnection(filename)
        self._create_dbstructure()
        

    def _erase_file(self, filename):
        """Erase a file ignoring if it does not exist"""

        try:
            os.remove(filename)
        except OSError:
            pass

        return


    def _open_dbconnection(self, filename):
        """Open a sqlite3 connection"""

        return sqlite3.connect(filename)


    def _create_dbstructure(self):
        """Create the DB structure

        Returns a boolean with the operation success"""
        
        table1 = '''CREATE TABLE IF NOT EXISTS requests(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name VARCHAR,
          type VARCHAR,
          group_name VARCHAR,
          site VARCHAR,
          params TEXT,
          creation DATETIME
          )'''

        table2 = '''CREATE TABLE IF NOT EXISTS scrapy_jobs(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          request_id INTEGER,
          scrapy_jobid VARCHAR,
          FOREIGN KEY(request_id) REFERENCES requests(id) 
            ON DELETE CASCADE 
            ON UPDATE CASCADE
          )'''

        try:
            cursor = self._conn.cursor()
            cursor.execute(table1)
            cursor.execute(table2)
            self._conn.commit()
            cursor.close()
            ret = True
        except sqlite3.Error as e:
            LOG.error("Error creating the DB tables. Detail=" + str(e))
            ret = False

        return ret


    def _new_request(self, name, command_type, params, jobids):
        """TODO: Add pydoc"""
        
        if not jobids:
            jobids = []
        params_json = json.dumps(params)
        group_name = params.get('group_name')
        site =  params.get('site')
        creation = datetime.datetime.today()
        
        insert_sql = '''INSERT INTO requests(name, type, group_name, site, 
          params, creation) values(?,?,?,?,?,?)'''
        sql_values= (name, command_type, group_name, site, params_json, creation)

        try:        
            import pdb; pdb.set_trace()
            cursor = self._conn.cursor()
            cursor.execute(insert_sql, sql_values)
            self._conn.commit()
            ret = True
        except sqlite3.Error as e:
            LOG.error("Error inserting a new request. Detail= " + str(e))
            ret = False

        return ret


    def new_spider(self, name, params, jobid):
        """TODO: Add pydoc"""
        
        jobids = [jobid] if jobid else None
        return self._new_request(name, SPIDER, params, jobids)

    def new_command(self, name, params, jobids):
        """TODO: Add pydoc"""

        return self._new_request(name, COMMAND, params, jobids)


if __name__ == '__main__':
    dbinterf = DbInterface('/tmp/web_runner.db', recreate=False)

    params = { "group_name": 'gabo_test', 
        "searchterms_str": "laundry detergent", 
        "site": "walmart", 
        "quantity": "100"}
    dbinterf.new_command('gabo name', params, None)
    

# vim: set expandtab ts=4 sw=4:
