import textwrap

import tornado.httpserver
import tornado.web
import tornado.ioloop
import tornado.options

from tornado.options import define
from tornado.options import options
define("port", default=8000, type=int, help="run on given port")

import motor.motor_tornado
from motor.motor_tornado import MotorClient

db = MotorClient().test_database

import json
import bson
from bson import json_util
#from bson.json_util import dumps

class ReverseHandler(tornado.web.RequestHandler):
    def get(self, input):
        self.write(input[::-1])
    def write_error(self, status_code, **kwargs):
        self.write("Gosh darnit user! You caused a %d error \n" % status_code)

class WrapHandler(tornado.web.RequestHandler):
    def post(self):
        text = self.get_argument("text")
        width = self.get_argument("width", 40)
        self.write(textwrap.fill(text, width))

async def do_find_one():
    document = await db.test_collection.find_one()
    return(document)

class MongoReaderHandler(tornado.web.RequestHandler):
    async def get(self):
        val = await do_find_one()
        self.write(json_util.dumps(val))

    async def head(self):
        val = await do_find_one()
        if val is not None:
            self.set_status(200)
        else:
            self.set_status(404)

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers = [
            (r"/reverse/(\w+)", ReverseHandler),
            (r"/wrap", WrapHandler),
            (r"/mongo", MongoReaderHandler)
        ], 
        db=db
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()