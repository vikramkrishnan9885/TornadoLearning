import tornado.httpserver
import tornado.web
import tornado.ioloop
import tornado.httpclient
import tornado.options

import urllib
import json
import datetime
import time

from tornado.options import define
from tornado.options import options

define("port", default=8000, help="run on the given port", type=int)

class IndexHandler(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    def get(self):
        query = self.get_argument('q')
        client = tornado.httpclient.AsyncHTTPClient()
        client.fetch("https://api.twitter.com/1.1/search/tweets.json?"+ urllib.parse.urlencode({"q":query, "result_type":"recent", "rpp":100}), callback = self.on_response)

    ### MOVE THE ENTIRE PROCESSING AFTER THE EXTERNAL IO ACTION TO
    ### on_response FUNCTION
    ### CALLBACKS ARE OF THE FORMAT on_response_i(self,reponse), WHERE i IS THE ID
    def on_response(self, reponse):
        body = json.loads(reponse.body)
        result_count = len(body['results'])
        now = datetime.datetime.utcnow()
        raw_oldest_tweet_at = body['result'][-1]['created_at']
        oldest_tweet_at =datetime.datetime.strptime(raw_oldest_tweet_at, "%a, %d %b %Y %H:%M:%S + 0000")
        seconds_diff = time.mktime(now.timetuple())-time.mktime(oldest_tweet_at.timetuple())
        tweets_per_second = float(result_count)/seconds_diff
        self.write("""
        <div style="text-align: center">
            <div style="font-size 72px">%s</div>
            <div style="font-size 144px">%0.2f</div>
            <div style="font-size 24px">tweets per second</div>
        </div>
        """ % (self.get_argument('q'), tweets_per_second))
        self.finish()

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", IndexHandler),
        ]
        tornado.web.Application.__init__(self, handlers)

if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()