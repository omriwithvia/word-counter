import logging

import ujson
from tornado.web import RequestHandler


class BaseHandler(RequestHandler):
    def post(self):
        # Assuming request is well structured - of course in production apps I'll add better handling
        request = ujson.loads(self.request.body)
        logging.info('Request to counter handler {!s}'.format(request))

        response = self.handle(request)
        self.write(ujson.dumps(response))

    def handle(self, request):
        raise NotImplementedError()
