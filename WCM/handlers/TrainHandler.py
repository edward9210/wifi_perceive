#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.web import RequestHandler
import json

from WCM.models.Train import Train

class TrainHandler(RequestHandler):
    def get(self):
        self.render('train.html', model = Train())

class AjaxTrainHandler(RequestHandler):
    def post(self):
        name = self.get_argument('name')
        results = Train().getDataByName(name)
        self.write(json.dumps(results))