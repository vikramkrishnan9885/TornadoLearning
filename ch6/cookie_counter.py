import tornado.httpserver
import tornado.web
import tornado.ioloop
import tornado.options

from tornado.options import define
from tornado.options import options

define("port", default=8000, type=int, help="stuff")

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        cookie = self.get_secure_cookie("count")
        count = int(cookie) + 1 if cookie else 1

        countString = "1 time" if count == 1 else "%d times" % count

        self.set_secure_cookie("count",str(count))

        self.write(
            """<html><head><title>Cookie Counter</title></head>
            <body><h1>You have viewd this page %s times </h1></body></html>
            """% countString
        )

if __name__ == "__main__":
    tornado.options.parse_command_line()

    settings = {
        "cookie_secret":"abcdefjdhar"
    }

    application = tornado.web.Application([
        (r'/', MainHandler)
    ], **settings)

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()