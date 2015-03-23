#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Monitor:
    """
        Monitor Model
    """
    def __init__(self, dpm_proxy):
        self.__dpm_proxy = dpm_proxy

    def getAllClientMac(self):
        """
            get all appeared client macs
            :return: get all appeared client macs
        """
        return self.__dpm_proxy.getAllClientMac()

    def query(self, target_client_macs):
        """
            query the result by a list of client macs
            :param target_client_macs: a list of client macs you want to query
            :return:
        """
        result = {}
        data = self.__dpm_proxy.query()
        timestamp = data.keys()[0]
        clients_data = data[timestamp]
        for client_mac in target_client_macs:
            if client_mac not in clients_data.keys():
                continue
            result[client_mac] = clients_data[client_mac]
        # print result
        return {
            'result' : result,
            'timestamp' : timestamp,
        }