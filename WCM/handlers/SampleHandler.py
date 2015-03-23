#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.web import RequestHandler
import json

from WCM.models.Sample import Sample

class SampleHandler(RequestHandler):
    def get(self):
        self.render('sample.html', model = Sample(self.settings['dpm_proxy']))

class StartSampleHandler(RequestHandler):
    def post(self):
        client_mac = self.get_argument('client_mac')
        type = self.get_argument('type')
        model = Sample(self.settings['dpm_proxy'])
        model.start_sampling(client_mac, type)
        self.render('sampling.html', model = model)

class StopSampleHandler(RequestHandler):
    def post(self):
        client_mac = self.get_argument('client_mac')
        type = self.get_argument('type')
        model = Sample(self.settings['dpm_proxy'])
        model.stop_sampling(client_mac, type)
        self.render('sample.html', model = Sample(self.settings['dpm_proxy']))

class AjaxSampleHandler(RequestHandler):
    def post(self):
        client_mac = self.get_argument('client_mac')
        model = Sample(self.settings['dpm_proxy'])
        results = model.sampled_data(client_mac)
        self.write(json.dumps(results))