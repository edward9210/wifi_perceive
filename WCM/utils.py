#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Queue:
    """
        a simple queue
    """
    def __init__(self, maxsize=5):
        self.__que = []
        self.__maxsize = maxsize

    def put(self, data):
        """
            put data into queue
            :param data:
            :return:
        """
        if len(self.__que) >= self.__maxsize:
            self.pop()
        self.__que.append(data)

    def pop(self):
        """
            pop the head data
            :return:
        """
        if len(self.__que) > 0:
            return self.__que.pop(0)

    def head(self):
        """
            get the head data
            :return:
        """
        if len(self.__que) > 0:
            return self.__que[0]
        else:
            return None

    def empty(self):
        """
            check the queue whether it is empty or not
            :return:
        """
        if len(self.__que) == 0:
            return True
        else:
            return False

def mac_to_str(mac):
    """
        transform MAC address into string
        :param mac:
        :return: the string of MAC address
    """
    return str(':'.join(['%02x' % ord(x) for x in mac]))

