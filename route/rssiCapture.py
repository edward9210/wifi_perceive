#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import struct
import socket
import fcntl
import time
import sys
import os
from threading import RLock, Thread
from time import sleep
from contextlib import contextmanager
from collections import deque, defaultdict

import pcap
import dpkt

TYPE = 0x11
SMOOTH_INTERVAL = 1.5

def log(*args, **kwargs):
    """
        print the input args and kwargs
        :param args:
        :param kwargs:
        :return:
    """
    print(*args, **kwargs)


def get_mac(dev):
    """
        get the route's MAC address
        :param dev: the route
        :return: the MAC address of the route
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return fcntl.ioctl(s.fileno(), 0x8927, struct.pack('256s', dev[:15]))[18:24]


def mac_to_str(mac):
    """
        transform MAC address to string
        :param mac:
        :return: the string of MAC address
    """
    return ':'.join(['%02x' % ord(x) for x in mac])


def parse_packet(rtpacket):
    """
        parse the radiotap packet
        :param rtpacket: the radiotap packet
        :return: (signal, client_mac) or None : None will be returned when the packet is not a ethernet packet
    """
    radiotap = dpkt.radiotap.Radiotap(rtpacket)
    it_len = struct.unpack('<H', struct.pack('>H', radiotap.length))[0]
    if radiotap.version != 0 or it_len < 8 or it_len + 34 > len(rtpacket):
        return None
    client_mac = rtpacket[it_len + 10 : it_len + 16]
    #print (mac_to_str(client_mac))
    for field in radiotap.fields:
        # print (`field`)
        if isinstance(field, dpkt.radiotap.Radiotap.AntennaSignal):
            signal = field.db - 256
            if signal < 0 and signal > -128 and len(client_mac) == 6:
                return signal, client_mac
            else:
                # print ('error mac : ' + mac_to_str(client_mac))
                break
    return None


class Daemon:

    def __init__(self, wdev, out_ip, out_port, interval):
        """
            the daemon running on the OpenWrt device
            :param wdev: Wireless device
            :param out_ip: the ip address of sending data
            :param out_port: the port of out_ip
            :param interval: the time interval of sending data (ms)
            :return:
        """
        self.addr = (out_ip, out_port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ap_mac = get_mac('br-lan')
        log('AP Mac:', mac_to_str(self.ap_mac))
        self.interval = interval / 1000.
        self.wdev = wdev
        self.signals = defaultdict(deque)
        self.lock_signals = RLock()
        self.need_quit = False
        self.pcap = None

    def start(self):
        """
            start running the daemon
            :return:
        """
        wdev = self.wdev
        os.system('ifconfig {} down && ifconfig {} up'.format(wdev, wdev))
        log('Daemon started:\n  dev: {}\n  mac: {}\n  dest: {}\n  interval: {}\n'.format(
            wdev, mac_to_str(self.ap_mac), self.addr, self.interval))
        th_send = Thread(target=self.run_send)
        th_capture = Thread(target=self.run_capture)
        ths = [
            th_send,
            th_capture,
        ]

        self.need_quit = False
        for th in ths:
            th.daemon = True
            th.start()

        try:
            for th in ths:
                th.join()
        except KeyboardInterrupt:
            self.quit()

    def run_send(self):
        """
            sending captured data to the (out_ip, out_port) (running by a thread)
            :return:
        """
        with self.guard():
            while not self.need_quit:
                sleep(self.interval)
                with self.lock_signals:
                    timestamp = time.time()
                    to_del = []
                    for client_mac, que in self.signals.iteritems():
                        while que and que[0][0] + SMOOTH_INTERVAL < timestamp:
                            que.popleft()
                        if not que:
                            to_del.append(client_mac)
                    for client_mac in to_del:
                        del self.signals[client_mac]
                    signals = []
                    for client_mac, que in self.signals.iteritems():
                        # que: deque<(timestamp, signal)>
                        signal = sum([signal for _, signal in que]) / len(que)
                        print('\t', mac_to_str(client_mac), len(que), signal)
                        signals.append((client_mac, signal))
                    self.send_record(timestamp, signals)

    def run_capture(self):
        """
            capture the data and save it in a queue (running by a thread)
            :return:
        """
        with self.guard():
            while not self.need_quit:
                recv_count = 0
                cap = pcap.pcap(self.wdev)
                for packet in cap:
                    if self.need_quit:
                        break
                    # log('start capture loop')
                    if packet is None:
                        continue
                    timestamp, rtpacket = packet
                    result = parse_packet(rtpacket)
                    if result is None:
                        # log('failed to parse the packet')
                        continue
                    signal, client_mac = result
                    with self.lock_signals:
                        que = self.signals[client_mac]
                        que.append((timestamp, signal))
                    recv_count += 1

    def quit(self):
        """
            quit the deamon
            :return:
        """
        self.need_quit = True

    @contextmanager
    def guard(self):
        """
            insure two thread(th_send, th_capture) working well
            :return:
        """
        try:
            yield
        except:
            self.quit()
            raise

    def send_record(self, timestamp, signals):
        """
            packet the sending data and send it
            :param timestamp: the timestamp of sending time
            :param signals: (client_mac, rssi)'s list
            :return:
            A record contains a head and a body
            head:
            -------------------------------------------------
            | type(1) | ap_mac(6) | timestamp(8) | count(1) |
            -------------------------------------------------
            body:
            --------------------
            | mac(6) | rssi(1) |
            --------------------
        """
        try:
            head = struct.pack('>B6sIxxxB',
                    TYPE, self.ap_mac, timestamp, len(signals))
            body = b''.join(
                struct.pack('>6sb', client_mac, signal) for client_mac, signal in signals
            )
            record = head + body
            self.sock.sendto(record, self.addr)
            log('time:', timestamp, 'sent', len(signals), 'signals')
            print ('-----------------------------------------------------------------')
        except socket.error as e:
            log('error:', e)
            return

if __name__ == '__main__':
    if len(sys.argv) < 5:
        exit('usage: python rssiCaputure.py wdev out_ip out_port interval')
    else:
        wdev, out_ip, out_port, interval = sys.argv[1:]
        out_port = int(out_port)
        interval = int(interval)
        Daemon(wdev, out_ip, out_port, interval).start()
