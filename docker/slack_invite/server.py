import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options
import os
import json
import slacker

define("port", default=80, help="run on the given port", type=int)

class WrapHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header(
            "Access-Control-Allow-Origin",
            os.environ.get("YTPAGE", "http://yt-project.org")
        )
        self.set_header('Access-Control-Allow-Methods', 'POST, OPTIONS')

    def options(self):
        self.set_header('Access-Control-Allow-Headers', 'Content-type')

    def post(self):
        data = json.loads(self.request.body)
        if "name" not in data:
            self.finish()
            return
        slack = Slacker(os.environ.get("SLACK_TOKEN")

        text = "User: {name} email: {email} requested access slack".format(**data)
        slack.chat.post_message("#general", text)
        self.finish()

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[
            (r"/", WrapHandler)
        ]
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
