#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.web import RequestHandler

from WCM.models.Test import Test, TestResult

class TestHandler(RequestHandler):
    def get(self):
        self.render('test.html', model = Test())

class TestResultHandler(RequestHandler):
    def post(self):
        data_name = str(self.get_argument('sampled_data'))
        test_name = str(self.get_argument('test_data'))
        # print data_name, test_name
        self.render('test_result.html', model = TestResult(data_name, test_name))