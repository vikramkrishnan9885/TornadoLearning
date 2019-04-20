import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options

import os

from tornado.options import define, options
define("port", default=8000, help="run on given port", type=int)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(
            "index.html",
            header_text = "This is my header",
            footer_text = "My Footer"
        )

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__),"templates")
        )
        tornado.web.Application.__init__(self, handlers,**settings)

if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()