from base_handler import BaseHandler
from persistence_layer import WordCounterPersistence


class StatsHandler(BaseHandler):
    def handle(self, request):
        session = self.application.session_maker()
        try:
            count_value = WordCounterPersistence.stats(session, request['word'].lower())

            return dict(count=count_value)
        finally:
            session.close()

