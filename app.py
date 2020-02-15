import logging

from tornado.ioloop import IOLoop
from tornado.web import Application, url

from counter_handler import CounterHandler
from persistence_layer import SessionMakerFactory
from stats_handler import StatsHandler


class WordCounterApplication(Application):
    """Implementation of the via-rider-payments server as web service for testing"""

    def __init__(self, port, db_driver=None, db_host=None, db_name=None, db_user=None, db_password=None, db_port=None):
        self.port = port
        self.handlers = self._GetHandlers()
        self.settings = dict(compress_response=False, debug=True)
        self.session_maker = SessionMakerFactory.get_session_maker(db_driver, db_name, db_host, db_user, db_password, db_port)
        super(WordCounterApplication, self).__init__(self.handlers, **self.settings)

    @staticmethod
    def from_configurator(configurator):
        return WordCounterApplication(configurator.get_port(), **configurator.get_db_params())

    def _GetHandlers(self):
        handlers = [url('/counter', CounterHandler),
                    url('/stats', StatsHandler)]

        return handlers

    def start_app(self):
        self.listen(int(self.port), "0.0.0.0")
        logging.info('Word counter service listening on port {!s}'.format(self.port))
        IOLoop.current().start()

    @staticmethod
    def StopIOLoop():
        IOLoop.current().stop()
