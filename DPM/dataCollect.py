#!/usr/bin/env python2
from __future__ import print_function
import struct
from collections import defaultdict
from SocketServer import UDPServer, DatagramRequestHandler
from threading import RLock, Thread
from time import sleep

# ap_mac ----> [{client_mac : [(timestamp, rssi),...]}, {}...]
data_dict = defaultdict(dict)
lock = RLock()

def mac_to_str(mac):
    return ':'.join(['%02x' % ord(x) for x in mac])

class Daemon:
    def __init__(self, area_type):
        self.need_quit = False
        #self.csv_file = open('data.csv', 'w')
        #self.csv_file.close()
        self.area_type = area_type

    def start(self):
        th_write_csv = Thread(target=self.run)
        self.need_quit = False
        th_write_csv.setDaemon(True)
        th_write_csv.start()
        UDPServer((host, port), Handler).serve_forever()

        try:
            th_write_csv.join()
        except KeyboardInterrupt:
            self.need_quit = True

    def run(self):
        while not self.need_quit:
            sleep(0.5)
            with lock:
                self.csv_file = open('data.csv', 'a')
                to_del = []
                flag = 0
                """
                for ap_mac, client_mac_que in data_dict.iteritems():
                    print (mac_to_str(ap_mac))
                    to_del.append(ap_mac)
                    for client_mac, que in client_mac_que.iteritems():
                        print ('\t' + mac_to_str(client_mac) + ' : ' + str(sum([rssi for _,rssi in que]) / len(que)))
                """
                for ap_mac, client_mac_que in data_dict.iteritems():
                    print (mac_to_str(ap_mac))
                    to_del.append(ap_mac)
                    for client_mac, que in client_mac_que.iteritems():
                        if mac_to_str(client_mac) == '98:fa:e3:42:bc:2b':
                            rssi = sum([rssi for _,rssi in que]) / len(que)
                            print ('\t' + mac_to_str(client_mac) + ' : ' + str(rssi))
                            self.csv_file.write(mac_to_str(ap_mac) + ':' + str(rssi) + ',')
                            flag = 1
                            break
                if flag:
                    self.csv_file.write(str(self.area_type)+'\r\n')
                for ap_mac in to_del:
                    del data_dict[ap_mac]
                self.csv_file.close()


class Handler(DatagramRequestHandler):
    HEAD_PATTERN = '<BBB6sQBB'
    HEAD_SIZE = struct.calcsize(HEAD_PATTERN)
    ITEM_PATTERN = '<6sBHbBBBBH'
    ITEM_SIZE = struct.calcsize(ITEM_PATTERN)

    def handle(self):
        data, client_sock = self.request
        _, _, _, ap_mac, time, _, count = struct.unpack_from(self.HEAD_PATTERN, data)
        csvFile = open('data.csv', 'a')
        for offset in xrange(self.HEAD_SIZE, len(data), self.ITEM_SIZE):
            client_mac, _, _, rssi, _, _, _, _, _ = struct.unpack_from(self.ITEM_PATTERN, data, offset)
            que_client = data_dict[ap_mac]
            if client_mac not in que_client:
                que_client[client_mac] = []
            que_client[client_mac].append((time, rssi))

if __name__ == '__main__':
    host = '0.0.0.0'
    port = 10234
    # modify type here before you start collect rssi data (area_type --> the type of area)
    area_type = 0
    Daemon(area_type).start()

    
    
