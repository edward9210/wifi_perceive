#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Sample:
    """
        Sample Model
    """
    def __init__(self, dpm_proxy):
        self.__dpm_proxy = dpm_proxy
        self.__sampling = False
        self.__client_mac = ''
        self.__type = None

    @property
    def client_macs(self):
        return sorted(self.__dpm_proxy.getAllClientMac())

    @property
    def state(self):
        return self.__sampling

    @property
    def mac(self):
        return self.__client_mac

    @property
    def type(self):
        if self.__type == None:
            return 'None'
        else:
            return self.__type

    def start_sampling(self, client_mac, type):
        self.__sampling = True
        self.__client_mac = client_mac
        self.__type = type
        self.__dpm_proxy.addSampleMac(client_mac)

    def stop_sampling(self, client_mac, type):
        data = self.__dpm_proxy.delSampleMac(client_mac)
        print 'data:'
        print data
        # write into database

    def sampled_data(self, client_mac):
        return self.__dpm_proxy.querySampledData(client_mac)