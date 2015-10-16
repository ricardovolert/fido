import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options
import os
import smtplib
from email.mime.text import MIMEText
import json

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
        text = "Please add {name} {email} to slack".format(**data)
        msg = MIMEText(text, 'plain')
        msg['Subject'] = "New Slack user request"
        msg['From']    = "yt slack <noreply@yt-project.org>"
        msg['To']      = "xarthisius.kk@gmail.com"
        msg['CC']      = "mjturk@gmail.com"

        username = os.environ['MANDRILL_USERNAME']
        password = os.environ['MANDRILL_PASSWORD']

        s = smtplib.SMTP('smtp.mandrillapp.com', 587)
        s.login(username, password)
        s.sendmail(msg['From'], msg['To'], msg.as_string())
        s.quit()
                
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
