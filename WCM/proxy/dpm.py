#!/usr/bin/env python
# -*- coding: utf-8 -*-

import struct
import time
import json
from tornado import tcpserver, gen

from WCM.utils import Queue

DPM_MES_TYPE = 0x22

class DPMProxy(tcpserver.TCPServer):
    """
        DPM Proxy receive data from DPM
    """

    HEAD_PATTERN = '>BIxxxxI'
    HEAD_SIZE = struct.calcsize(HEAD_PATTERN)

    def __init__(self, interval = 1):
        """
            init DPM proxy
            :param interval: the time interval to remove data from queue
            :return:
        """
        super(DPMProxy, self).__init__()
        self.__que = Queue()
        self.__interval = interval

    @gen.engine
    def handle_stream(self, stream, address):
        """
            handle the coming data stream
            :param stream: the iostream
            :param address: the (ip, port)
            :return:
        """
        while True:
            header = yield gen.Task(stream.read_bytes, self.HEAD_SIZE)
            type, timestamp, length = struct.unpack_from(self.HEAD_PATTERN, header)
            if type == DPM_MES_TYPE:
                body = yield gen.Task(stream.read_bytes, length)
                body = json.loads(body.decode('utf-8'))
                # print timestamp, body
                self.__que.put({timestamp : body})

    def query(self):
        """
            query the data
            :return: the route data
        """
        self.__que_sync()
        if not self.__que.empty():
            return self.__que.head()
        else:
            return {str(int(time.time())) : ''}

    def __que_sync(self):
        """
            remove the expire data
            :return:
        """
        if not self.__que.empty():
            while True and not self.__que.empty():
                head = self.__que.head()
                timestamp = head.keys()[0]
                curtime = int(time.time())
                if timestamp + self.__interval < curtime:
                    self.__que.pop()
                else:
                    break



