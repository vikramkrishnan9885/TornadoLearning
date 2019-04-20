import tornado.platform.twisted
tornado.platform.twisted.install()

import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options

from tornado.options import define, options
define("port", default=9001, help="run on given port", type=int)

from twisted.internet import reactor
from twisted.enterprise import adbapi

import json

dbpool = adbapi.ConnectionPool("sqlite3", "users.db", check_same_thread=False)

def getName(email):
    return dbpool.runQuery("SELECT id, name, email FROM users WHERE email = ?",
                           (email,))

def printResults(results):
    for elt in results:
        print(elt[0])

def finish():
    dbpool.close()
    reactor.stop()

class MainHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        email = self.get_argument("email")
        #print(email)
        data = getName(email)
        data.addCallback(self.on_response)
        ### NOTE: THAT THE A FUNCTION ANNOTATED WITH @tornado.web.asynchronous 
        ### will end with a addCallback OR addCallbacks

    def on_response(self, response):
        #print(response)
        d = dict()
        d['id'] = response[0][0]
        d['name'] = response[0][1]
        d['email'] = response[0][2]
        #self.write(json.dumps(response))
        self.write(json.dumps(d))
        self.finish()
        

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
        ]
        tornado.web.Application.__init__(self, handlers)

if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
    reactor.callLater(1, finish)
    reactor.run()
    
