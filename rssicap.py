#!/usr/bin/env python
from __future__ import print_function
import struct
import socket
import fcntl
import time
import os
from threading import RLock, Thread
from time import sleep
from contextlib import contextmanager
from collections import namedtuple, deque, defaultdict

import pcap


ANTENNA_SIGNAL_BIT = 5
Field = namedtuple('Field', ['name', 'format'])
FIELDS = (
    Field('TSFT', 'Q'),
    Field('Flags', 'B'),
    Field('Rate', 'B'),
    Field('Channel', 'HH'),
    Field('FHSS', 'BB'),
    Field('Antenna_signal', 'b'),
)

SMOOTH_INTERVAL = 1.5

DEBUG = True


def log(*args, **kwargs):
    if not DEBUG:
        return
    print(*args, **kwargs)


def get_mac(dev):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return fcntl.ioctl(s.fileno(), 0x8927, struct.pack('256s', dev[:15]))[18:24]


def mac_to_str(mac):
    return ':'.join(['%02x' % ord(x) for x in mac])


_field_pattern_cache = {}


def get_field_pattern(field_bits, key=None):
    key = frozenset(field_bits) if key is None else key
    try:
        return _field_pattern_cache[key]
    except KeyError:
        pass
    formats = ['>']
    offset = 0
    for bit in field_bits:
        for f in FIELDS[bit].format:
            size_f = struct.calcsize('=' + f)
            pad = 'x' * ((size_f - offset % size_f) % size_f)
            formats.append(pad)
            formats.append(f)
            offset += len(pad) + size_f
    _field_pattern_cache[key] = pattern = ''.join(formats)
    return pattern


def parse_packet(rtpacket):
    """
    return: (signal, client_mac) or None

    None will be returned when the packet is not a ethernet packet.
    """
    it_version, it_pad, it_len = struct.unpack_from('<BBH', rtpacket, 0)
    if it_version != 0 or it_len < 8 or it_len + 34 > len(rtpacket):
        # log('version', it_version, 'len', it_len)
        return None
    start = 4
    masks = []
    while start + 4 < it_len:
        it_present = struct.unpack_from('<I', rtpacket, start)[0]
        masks.append(it_present)
        start += 4
        if ((it_present >> 31) & 1) == 0:
            break

    def read_bit(i):
        return (masks[i >> 5] >> (i & 0x1f)) & 1

    if not read_bit(ANTENNA_SIGNAL_BIT):
        # log('no ANTENNA_SIGNAL_BIT field')
        return None

    # Parse fields before ANTENNA_SIGNAL_BIT (inclusive).
    field_bits = filter(read_bit, xrange(ANTENNA_SIGNAL_BIT + 1))
    pattern = get_field_pattern(field_bits, masks[0])
    field_vals_flat = struct.unpack_from(pattern, rtpacket, start)
    # Read signal field
    signal = field_vals_flat[-1]
    # Read source mac
    eth_start = it_len
    client_mac = rtpacket[eth_start + 10:eth_start + 16]
    assert len(client_mac) == 6
    return signal, client_mac


class Daemon:

    def __init__(self, wdev, out_ip, out_port, interval):
        """
        wdev: Wireless device
        (out_ip, out_port): Send data to this address by TCP or UDP
        interval: Time interval
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
        wdev = self.wdev
        os.system('ifconfig {} down && ifconfig {} up'.format(wdev, wdev))
        log('Daemon started:\n  dev: {}\n  mac: {}\n  dest: {}\n  interval: {}\n'.format(
            wdev, self.ap_mac, self.addr, self.interval))
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
                        # DEBUG
                        print('  ', mac_to_str(client_mac), len(que))
                        signal = sum([signal for _, signal in que]) / len(que)
                        signals.append((client_mac, signal))
                    self.send_record(timestamp, signals)

    def run_capture(self):
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
        self.need_quit = True

    @contextmanager
    def guard(self):
        try:
            yield
        except:
            self.quit()
            raise

    def send_record(self, timestamp, signals):
        """
        A record contains a head and a body.
        head:
        ----------------------------------------------------------------------------------------
        | type(1u) | vendor(1u) | version(1u) | ap_mac(6) | time(8u) | errcode(1u) | count(1u) |
        ----------------------------------------------------------------------------------------
        body:
        ----------------------
        | mac(6) | value(10) | x count
        ----------------------
        value:
        --------------------------------------------------------------
        | dev_type(1u) | seq_number(2u) | rssi(1s) | dev_version(1u) |
        --------------------------------------------------------------
        ------------------------------------------------------
        | data1(1) | data2(1) | dev_status(1u) | default(2u) |
        ------------------------------------------------------
        """
        try:
            while signals:
                signals, reset_signals = signals[:255], signals[255:]
                head = struct.pack('>BBB6sIxxxxBB',
                        0xbd, 0, 0, self.ap_mac, timestamp, 0, len(signals))
                body = b''.join(
                    struct.pack('>6sBHbBBBBH', client_mac, 1, 0x00, signal, 0, 0, 0, 0, 0x00)
                    for client_mac, signal in signals
                )
                record = head + body
                self.sock.sendto(record, self.addr)
                log(timestamp, 'sent', len(signals), 'signals')
                # log(timestamp, ' different clients', len(set([mac for mac, _ in signals])))
                signals = reset_signals
        except socket.error as e:
            log('error:', e)
            return


def main():
    import sys
    if len(sys.argv) < 5:
        exit('usage: rssicap.py wdev out_ip out_port interval')
    else:
        wdev, out_ip, out_port, interval = sys.argv[1:]
        out_port = int(out_port)
        interval = int(interval)
        Daemon(wdev, out_ip, out_port, interval).start()


if __name__ == '__main__':
    main()
