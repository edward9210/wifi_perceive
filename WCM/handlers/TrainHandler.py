#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.web import RequestHandler
import json

from WCM.models.Train import Train, TrainResult, saveTrainResult

class TrainHandler(RequestHandler):
    def get(self):
        self.render('train.html', model = Train())

class AjaxTrainHandler(RequestHandler):
    def post(self):
        name = self.get_argument('name')
        results = Train().getDataByName(name)
        self.write(json.dumps(results))

class TrainResultHandler(RequestHandler):
    def post(self):
        selected_data_name_list = json.loads(self.get_argument('selected_data'))
        percentage = self.get_argument('percentage')
        treeNum = self.get_argument('tree_num')
        model = TrainResult(selected_data_name_list, percentage, treeNum)
        self.render('train_result.html', model = model)

class SaveTrainResultHandler(RequestHandler):
    def post(self):
        name = self.get_argument('result_name')
        trees = json.loads(self.get_argument('trees'))
        # print name, trees
        saveTrainResult(name, trees)
        self.redirect('/')