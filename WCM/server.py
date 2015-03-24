#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import tornado.httpserver
import tornado.options
from tornado.options import define, options
from tornado import httpserver, ioloop, web

from proxy.dpm import DPMProxy
from handlers.IndexHandler import IndexHandler
from handlers.MonitorHandler import MonitorHandler, AjaxMonitorHandler
from handlers.DPMDataHandler import DPMDataHandler
from handlers.SampleHandler import SampleHandler, StartSampleHandler, StopSampleHandler, AjaxSampleHandler
from handlers.TrainHandler import TrainHandler, AjaxTrainHandler, TrainResultHandler

subpath = os.path.dirname(os.path.realpath(__file__))

HANDLERS = [
    (r'/', IndexHandler),
    (r'/sample', SampleHandler),
    (r'/train', TrainHandler),
    (r'/training_result', TrainResultHandler),
    (r'/monitor', MonitorHandler),

    (r'/dpmdata', DPMDataHandler),
    (r'/ajax_monitor', AjaxMonitorHandler),
    (r'/start_sample', StartSampleHandler),
    (r'/stop_sample', StopSampleHandler),
    (r'/ajax_sample', AjaxSampleHandler),
    (r'/ajax_train', AjaxTrainHandler),
]


class WCMApp(web.Application):
    def __init__(self, options):
        super(WCMApp, self).__init__(
            handlers=HANDLERS,
            template_path = subpath + '/templates',
            static_path = subpath + '/static',
            debug = True,
            pam_port = options.pamport,
            pam_host = options.pamhost,
            dpm_proxy = DPMProxy(),
        )

        self.settings['dpm_proxy'].listen(10235)



def main():
    from multiprocessing import freeze_support
    freeze_support()

    define('port', default=8080, help='run on the given port', type=int)
    define('pamport', default=10236, help='PAM port', type=int)
    define('pamhost', default='localhost', help='PAM host', type=str)

    tornado.options.parse_command_line()

    app = WCMApp(options)
    http_server = httpserver.HTTPServer(app)
    http_server.listen(options.port)

    ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()

