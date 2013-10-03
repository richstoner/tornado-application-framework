
__author__ = 'stonerri'

'''

This code acts as the application's primary controller, and provides links to the following:

'''



import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import tornado.autoreload



from redis import Redis
from rq import Queue

import requests

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)

# utility classes
import json
import os.path
import uuid
import datetime
import logging
import random
import time
import string
from time import mktime, sleep

root = os.path.dirname(__file__)

# needed to serialize any non-standard objects
class GenericEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return int(mktime(obj.timetuple()))

        return json.JSONEncoder.default(self, obj)

class FaviconHandler(tornado.web.RequestHandler):
    def get(self):
        self.redirect('/static/favicon.ico')

# generic object
class Object(object):
    pass



# this presents a single standalone webpage
# important to note we're piping directly, not rendering it as a template
# this let's us bypass having to escape A LOT of angular code (it's possible to mix templating engines, but it's not
# worth the extra effort (for now)
class WebHandler(tornado.web.RequestHandler):

    def get(self):
        try:
            with open(os.path.join(root, 'templates/index.html')) as f:
                self.write(f.read())
        except IOError as e:
            self.write("404: Not Found")













from rqtasks import *

# websockets
class WSHandler(tornado.websocket.WebSocketHandler):


    # place any shared objects or settings in this object during initialization from main loop
    def initialize(self, shared):

        self.shared = shared
        #print self.shared
        tornado.ioloop.IOLoop.instance().add_timeout(datetime.timedelta(seconds=3), self.check_queue)


    def allow_draft76(self):
        # for iOS 5.0 Safari
        return True

    def open(self):
        print 'Websocket connection opened.'

        # self.write_message("Hello World")

    def on_close(self):
        print 'connection closed'

    def on_message(self, message):
        print 'message received %s' % message
        messagedict = json.loads(message)

        return_data = {}
        return_data['result'] = False
        return_data['callback_id'] = messagedict['callback_id']

        if messagedict['type'] == 'kickoff_queue':
            job = self.shared.q.enqueue(count_words_at_url, 'http://nvie.com')

        while not job.result:
            time.sleep(1)

        return_data['data'] = job.result
        return_data['result'] = True

        print 'job complete'
        print job.result

        self.write_message(json.dumps(return_data))

    def check_queue(self):

        print '.'
        list_to_remove = []

        for i in range(len(self.shared.js)):

            j = self.shared.js[i]

            from pprint import pprint
            pprint (vars(j))

            if j.result:
                print j.result
                print 'now removing it'
                list_to_remove.append(i)

                return_data = {}
                return_data['result'] = True
                return_data['func'] = 'update_image'
                return_data['contents'] = json.loads(j.result)

                self.write_message(json.dumps(return_data))

        for index in sorted(list_to_remove, reverse=True):
            print 'removing job at index %d' % index
            del self.shared.js[index]

        #jobs_list = self.shared.q.get_jobs()
        #print self.shared.q.job_ids
        #print jobs_list
        #for n,j in enumerate(jobs_list):
        #    print n, j.result

        tornado.ioloop.IOLoop.instance().add_timeout(datetime.timedelta(seconds=3), self.check_queue)





#tornado.ioloop.IOLoop.instance().add_timeout(datetime.timedelta(seconds=5), self.pollForAccessPoint)


class UploadHandler(tornado.web.RequestHandler):

    def initialize(self, shared):
        self.shared = shared
        print self.shared

    def post(self):

        #print self.request.files.keys()

        file1 = self.request.files['file'][0]
        original_fname = file1['filename']
        extension = os.path.splitext(original_fname)[1]
        fname = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(6))
        final_filename= fname+extension
        full_path = os.path.abspath(root) + "/static/uploads/" + final_filename
        output_file = open(os.path.abspath(root) + "/static/uploads/" + final_filename, 'w')
        output_file.write(file1['body'])
        output_file.close()

        from rqtasks import processImage
        job = self.shared.q.enqueue(processImage,full_path)
        self.shared.js.append(job)

        #print self.shared.js

        self.finish("file" + final_filename + " is uploaded")





# Example code: How to call a function with fixed timing within tornado async loop
# tornado.ioloop.IOLoop.instance().add_timeout(datetime.timedelta(seconds=5), self.pollForAccessPoint)



class Application(tornado.web.Application):

    def __init__(self):

        self.shared_object = Object()
        self.shared_object.js = []
        self.shared_object.q = Queue(connection=Redis())



        handlers = [
            (r'/', WebHandler),
            (r'/ws', WSHandler, dict(shared=self.shared_object)),
            (r'/upload', UploadHandler, dict(shared=self.shared_object))
        ]
        settings = dict(
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=False,
        )
        tornado.web.Application.__init__(self, handlers, **settings)


 # Watch templates and static path directory
        for (path, dirs, files) in os.walk(settings["template_path"]):
            for item in files:
                tornado.autoreload.watch(os.path.join(path, item))

        for (path, dirs, files) in os.walk(settings["static_path"]):
            for item in files:
                tornado.autoreload.watch(os.path.join(path, item))


def main():

    # I don't actually do anything here beyond configure port and allowable IPs
    tornado.options.parse_command_line()

    # init application
    app = Application()
    app.listen(options.port)

    # start the IO loop
    io_loop = tornado.ioloop.IOLoop.instance()
    tornado.autoreload.start(io_loop)
    io_loop.start()

if __name__ == "__main__":
    main()
