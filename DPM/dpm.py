#!/usr/bin/env python
# -*- coding: utf-8 -*-

import struct
import socket
from SocketServer import UDPServer, DatagramRequestHandler
from threading import RLock, Thread
from time import sleep, time
import json

ROUTE_MES_TYPE = 0x11
DPM_PORT = 10234
WCM_PORT = 10235
PAM_PORT = 10236

dataDict = {}
lock = RLock()

def mac_to_str(mac):
    """
        transform MAC address into string
        :param mac:
        :return: the string of MAC address
    """
    return ':'.join(['%02x' % ord(x) for x in mac])

class DPM:
    """
        DPM is Data Processing Module
        DPM is used to receive data from routes
        and preprocesses the data and then sends it to WCM and PAM
    """
    def __init__(self, interval):
        """
            init the DPM
            :param interval: the time interval of sending data (ms)
            :return:
        """
        self.__interval = interval / 1000.0
        self.__ip = socket.gethostbyname(socket.gethostname())
        self.__udpServer = UDPServer(('0.0.0.0', DPM_PORT), DataRecvServer)

    def start(self):
        """
            start running the DPM
            :return:
        """
        thSend = Thread(target=self.runSend)
        self.__needQuit = False
        thSend.daemon = True
        thSend.start()
        self.__udpServer.serve_forever()

        try:
            thSend.join()
        except KeyboardInterrupt:
            self.quit()

    def runSend(self):
        """
            Send data to the WCM and PAM
            :return:
        """
        while not self.__needQuit:
            sleep(self.__interval)
            with lock:
                print time(), dataDict

                body = json.dumps(dataDict)
                header = struct.pack('>BIxxxxI', 0x22, time(), len(body))

                """
                    send data to WCM
                """
                try:
                    WCMSender = TcpClient('0.0.0.0', WCM_PORT)
                    WCMSender.connect()
                    WCMSender.write(header)
                    WCMSender.write(body.encode('utf-8'))
                    WCMSender.flush()
                except:
                    print 'conncect WCM failed'
                finally:
                    WCMSender.close()

                """
                    send data to PAM
                """
                try:
                    PAMSender = TcpClient('0.0.0.0', PAM_PORT)
                    PAMSender.connect()
                    PAMSender.write(header)
                    PAMSender.write(body.encode('utf-8'))
                    PAMSender.flush()
                except:
                    print 'conncect PAM failed'
                finally:
                    PAMSender.close()

                dataDict.clear()

    def quit(self):
        """
            quit the deamon
            :return:
        """
        self.__needQuit = True
        self.__udpServer.shutdown()

class TcpClient:
    """
        TcpClient is encapsulation for the socket in python
    """
    def __init__(self, host, port):
        """
            init tcp client
            :param host: the host ip
            :param port: the host port
            :return:
        """
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.rfile = self.sock.makefile('rb')
        self.wfile = self.sock.makefile('wb')

    def recv(self, size):
        """
            receive the data for the given size
            :param size: the length of data you want to receive
            :return: data
        """
        data = self.rfile.read(size)
        if len(data) < size:
            raise socket.error
        return data

    def connect(self):
        """
            connect to the (host, port)
            :return:
        """
        self.sock.connect((self.host, self.port))

    def write(self, data):
        """
            send data to the (host, port)
            :param data: data you want to send
            :return:
        """
        self.wfile.write(data)

    def flush(self):
        """
            flush the buffer
            :return:
        """
        self.wfile.flush()

    def close(self):
        """
            close the tcp conncetion
            :return:
        """
        self.sock.close()

class DataRecvServer(DatagramRequestHandler):
    """
        DataRecvServer is a UDP Server to receive data from routes
    """
    HEAD_PATTERN = '>B6sIxxxxB'
    HEAD_SIZE = struct.calcsize(HEAD_PATTERN)
    ITEM_PATTERN = '>6sb'
    ITEM_SIZE = struct.calcsize(ITEM_PATTERN)

    def handle(self):
        """
            handle the message from routes
            :return:
        """
        data, clientSock = self.request
        type, apMac, time, count = struct.unpack_from(self.HEAD_PATTERN, data)
        if type == ROUTE_MES_TYPE:
            apMac = mac_to_str(apMac)
            with lock:
                for offset in xrange(self.HEAD_SIZE, len(data), self.ITEM_SIZE):
                    clientMac, rssi = struct.unpack_from(self.ITEM_PATTERN, data, offset)
                    clientMac = mac_to_str(clientMac)
                    if clientMac not in dataDict.keys():
                        dataDict[clientMac] = {}
                    if apMac not in dataDict[clientMac].keys():
                        dataDict[clientMac][apMac] = rssi
                    dataDict[clientMac][apMac] = int((dataDict[clientMac][apMac] + rssi) / 2)

if __name__ == '__main__':
    print "DPM Server start ......"
    try:
        DPM(1000).start()
    except KeyboardInterrupt:
        print 'DPM Server stop ......'

