#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from tornado.web import RequestHandler

from WCM.models.Monitor import Monitor

class MonitorHandler(RequestHandler):
    def get(self):
        self.render('monitor.html')

class AjaxMonitorHandler(RequestHandler):
    def get(self):
        monitor = Monitor(self.settings['dpm_proxy'])
        result = {
            'clients': monitor.getAllClientMac(),
        }
        self.write(json.dumps(result))

    def post(self):
        client_macs = list(json.loads(self.get_argument('clients')))
        monitor = Monitor(self.settings['dpm_proxy'])
        results = monitor.query(client_macs)
        self.write(json.dumps(results))

