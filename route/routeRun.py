#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pexpect
import socket

def ssh_cmd(ip, passwd, cmd):
    ssh = pexpect.spawn('ssh root@' + ip)
    try:
        i = ssh.expect(['password:', '(yes/no)'])
        if i == 0 :
            ssh.sendline(passwd)
        elif i == 1:
            ssh.sendline('yes\n')
            ssh.expect('password: ')
            ssh.sendline(passwd)
        ssh.sendline(cmd)
        while True:
            r = ssh.readline()
            print r,
    except pexpect.EOF:
        print "EOF"
        ssh.close()
    except KeyboardInterrupt:
        print "KeyboardInterrupt"
        ssh.close()

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        exit('usage: python routeRun.py des_ip interval')
    else:
        des_ip, interval = sys.argv[1:]
    hostIP = socket.gethostbyname(socket.gethostname())
    print 'host ip: ' + hostIP
    ssh_cmd(des_ip, 'winnergz', 'python rssiCapture.py wlan0 ' + hostIP + ' 10234 ' + interval)
