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

    _counter = 0

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


    def close(self):
        """Close DB connection"""
        self._conn.close()


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


    def create_dbstructure(self):
        """Create the DB structure

        Returns a boolean with the operation success"""
        
        table1 = '''CREATE TABLE IF NOT EXISTS requests(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name VARCHAR,
          type VARCHAR,
          group_name VARCHAR,
          site VARCHAR,
          params TEXT,
          creation TIMESTAMP
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
        """Add a new request to the DB:

        Input parameters:
          * name: name of the command or scraper
          * command_type: valid values are COMMAND or SPIDER
          * params: request params
          * jobids: list of scrapyd job associated to the command/spider

        Return: boolean with the operation success
        """
        
        DbInterface._counter += 1
        if not jobids:
            jobids = []
        params_json = json.dumps(params)
        group_name = params.get('group_name')
        site =  params.get('site')
        creation = datetime.datetime.today()
        
        # Insert the main request
        insert_sql = '''INSERT INTO requests(name, type, group_name, site, 
          params, creation) values(?,?,?,?,?,?)'''
        sql_values= (name, command_type, group_name, site, params_json, creation)

        try:        
            cursor = self._conn.cursor()
            cursor.execute(insert_sql, sql_values)
            ret = True
        except sqlite3.Error as e:
            LOG.error("Error inserting a new request. Detail= " + str(e))
            ret = False

        if ret:
            # Add the scrapyd jobids
            request_id = cursor.lastrowid
            jobid_db_rows = [(request_id, jobid) for jobid in jobids]
            insert_jobids = '''INSERT INTO scrapy_jobs(request_id, scrapy_jobid)
              values(?,?)'''
            try:
                if len(jobid_db_rows):
                    cursor.executemany(insert_jobids, jobid_db_rows)
                self._conn.commit()
            except sqlite3.Error as e:
                LOG.error("Error inserting a new request. Detail= " + str(e))
                ret = False


        return ret


    def new_spider(self, name, params, jobid):
        """Insert a new spider into the DB

        Input parameters:
          * name: name of the spider
          * params: request params
          * jobid: scrapyd jobid associated 

        Return: boolean with the operation success
        """
        jobids = [jobid] if jobid else None
        return self._new_request(name, SPIDER, params, jobids)


    def new_command(self, name, params, jobids):
        """Add a new command to the DB:

        Input parameters:
          * name: name of the command 
          * params: request params
          * jobids: list of scrapyd job associated to the command

        Return: boolean with the operation success
        """
        return self._new_request(name, COMMAND, params, jobids)

 
    def get_last_requests(self, size):
        """Returns the last 'size' requests within the DB

        The output is a list of dictionary, each one representing a request.
        The dict keys are:
          * name, type, group_name, site, params(type: json), creation
        """

        cursor = self._conn.cursor()
        sql = '''SELECT id, name, type, group_name, site, params, creation 
          FROM requests 
          ORDER BY creation DESC 
          LIMIT %d''' % size;
        cursor.execute(sql)

        output = []
        for row in cursor.fetchall():
            (id, name, type, group_name, site, params, creation) = row
            row_dict = {
              'name': name,
              'type': type,
              'group_name': group_name,
              'site': site,
              'params': params,
              'creation': creation}
            output.append(row_dict)
        
        return output

if __name__ == '__main__':
    dbinterf = DbInterface('/tmp/web_runner.db', recreate=False)

    params = { "group_name": 'gabo_test', 
        "searchterms_str": "laundry detergent", 
        "site": "walmart", 
        "quantity": "100"}
    #dbinterf.new_command('gabo name', params, None)
    last_reqs = dbinterf.get_last_requests(2)
    print(last_reqs)
    dbinterf.close()
    

# vim: set expandtab ts=4 sw=4:
