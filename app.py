import logging
import re

import requests
import ujson
from sqlalchemy.engine import url as sqlalchemy_url
from tornado.ioloop import IOLoop
from tornado.web import Application, url, RequestHandler

from persistence_layer import WordCounterPersistence


class WordCounterApplication(Application):
    """Implementation of the via-rider-payments server as web service for testing"""

    def __init__(self, port, db_driver=None, db_host=None, db_name=None, db_user=None, db_password=None, db_port=None):
        self.port = port
        self.handlers = self._GetHandlers()
        self.settings = dict(compress_response=False, debug=True)
        # self.session_maker = DbClient.get_session_maker(db_driver, db_name, db_host, db_user, db_password, db_port)
        super(WordCounterApplication, self).__init__(self.handlers, **self.settings)

    @staticmethod
    def from_configurator(configurator):
        return WordCounterApplication(configurator.get_port())

    def _GetHandlers(self):
        handlers = [url('/counter', CounterHandler),
                    url('/stats', StatsHandler)]

        return handlers

    def start_app(self):
        self.listen(int(self.port), "0.0.0.0")
        logging.info('Running in DEBUG mode')
        logging.info('Word counter service listening on port {!s}'.format(self.port))
        IOLoop.current().start()

    @staticmethod
    def StopIOLoop():
        IOLoop.current().stop()


class BaseHandler(RequestHandler):
    def post(self):
        # TODO(Omri) throw better error when it's not json or other error with request
        request = ujson.loads(self.request.body)
        logging.info('Request to counter handler {!s}'.format(request))

        response = self.handle(request)
        self.write(ujson.dumps(response))

    def handle(self, request):
        raise NotImplementedError()


# TODO(Omri) move those to different files once we're good


class CounterHandler(BaseHandler):
    def handle(self, request):
        data_reader = ReaderFactory.produce(request)
        sentence = data_reader.read()

        words_list = re.findall(r'\w+', sentence)
        word_counts = self._count_words(words_list)

        # Sending the whole list because when it's not in-mem I might want to do it in a bulk to save comms with persistence level
        WordCounterPersistence.increment(word_counts)
        # TODO(Omri) add regexp and update counter layer

        return dict(success=True)

    def _count_words(self, words_list):
        counts = dict()
        for w in words_list:
            if w not in counts:
                counts[w] = 1
            else:
                counts[w] += 1

        return counts


class StatsHandler(BaseHandler):
    def handle(self, request):
        # TODO(Omri) do this
        count_value = WordCounterPersistence.stats(request['word'])
        return dict(count=count_value)


class ReaderFactory(object):
    @staticmethod
    def produce(request):
        # Assuming input as text is not too big.
        # If required I would go with reading request as a stream, request as raw text (no JSON because I don't know a
        # way to parse a really big JSON "as a stream" without allocating all the memory),
        # identifying input type file:// or http(s):// or nothing alike.
        if request.get('sentence'):
            return StringDataReader(request['sentence'])
        elif request.get('url'):
            # Assuming starts with "http://"
            return HttpDataReader(request['url'])
        elif request.get('filename'):
            # Assuming it fits operation system format - either /home/whatever of C:\dir\filename.ext
            return FileDataReader(request['filename'])

        raise ValueError('Bad request - could not find and valid input source')


class StringDataReader(object):
    def __init__(self, sentence):
        self.data = sentence

    def read(self):
        return self.data


class HttpDataReader(object):
    def __init__(self, url):
        self.url = url

    def read(self):
        return requests.get(self.url, stream=True)


class FileDataReader(object):
    def __init__(self, filename):
        self.filename = filename

    def read(self):
        # Assuming file exists and we'll crash if not
        # Assuming file not too big
        # TODO(Omri) wrap with better error.
        with open(self.filename, 'r') as f:
            return f.read()

#
# class DbClient(object):
#     @classmethod
#     def get_session_maker(cls, db_driver, db_name, db_host, db_user, db_password, db_port):
#         db_url = sqlalchemy_url.URL(db_driver, db_user, db_password, db_host, db_port, db_name)
#         logging.info("using DB {!s}".format("mysql://{!s}:redacted@{!s}:{!s}/{!s}".format(
#             db_user, db_host, db_port, db_name
#         )))
#         engine = create_engine(db_url,
#                                echo=db_echo,
#                                pool_recycle=pool_recycle)
#         session_maker = sessionmaker(bind=engine, autoflush=False)
#         return session_maker
