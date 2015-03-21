#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from tornado.web import RequestHandler

class DPMDataHandler(RequestHandler):
    def get(self):
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(self.settings['dpm_proxy'].query()))
        self.finish()
