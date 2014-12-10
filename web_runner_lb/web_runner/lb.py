#!/usr/bin/env python
import logging
import sqlite3
import os
import datetime

LOG = logging.getLogger(__name__)

LB_ROUND_ROBIN = 'ROUND_ROBIN'

'''
TODO:
. Write all pydocs
. documentation
. There's a memory leak
. persistence
'''

def getLB(method, **kwargs):
    if method == LB_ROUND_ROBIN:
        return LBRoundRobin(kwargs)

class LBServer(object):
    def __init__(self, host, port=None):
        self.host = host
        self.port = port


class LBInterface(object):
    '''TODO: Write PyDoc'''
    
    def __init__(self, method, servers):
        self.lbMethod = method
        self.servers = servers
        self.ids = {}
        self.ids_date = {}
        
    def get_new_server(self, request):
        raise NotImplementedError

    def set_id(self, id, server):
        self.ids[id] = server
        self.ids_date = { id: (datetime.date.today(), None) }

    def get_id(self, id):
        try:
            server = self.ids[id]
        except KeyError:
            server = None

        return server


class LBRoundRobin(LBInterface):

    def __init__(self, servers):
        LBInterface.__init__(self, 'RoundRobin', **servers)
        self.counter = 0

    def get_new_server(self, request):

        if not self.servers:
            return None

        ret_server = self.servers[self.counter]
        self.counter += 1

        if self.counter >= len(self.servers):
            self.counter = 0
        
        return ret_server

        
        


if __name__ == '__main__':
    servers = [LBServer('127.0.0.1', 65431),
        LBServer('127.0.0.1', 65432),
        LBServer('127.0.0.1', 65433),
        LBServer('127.0.0.1', None),
        ]

    lb = getLB(LB_ROUND_ROBIN, servers= servers)
    for index in range(10):
        serv = lb.get_new_server(None)
        print("server%d: %s:%s" % (index, serv.host, serv.port))
        print("Seting server %s:%s as id=%d" % (serv.host, serv.port, index))
        lb.set_id(index, serv)
    
    for index in range(11):
        serv = lb.get_id(index)
        if serv :
            print("Server for id=%d is %s:%s" % (index, serv.host, serv.port))
        else:
            print("No Server for id=%d " % (index))

# vim: set expandtab ts=4 sw=4:
