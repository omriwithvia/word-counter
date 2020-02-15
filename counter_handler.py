import re

from base_handler import BaseHandler
from persistence_layer import WordCounterPersistence
from readers import ReaderFactory


class CounterHandler(BaseHandler):
    def handle(self, request):
        data_reader = ReaderFactory.produce(request)

        session = self.application.session_maker()
        try:
            for sentence in data_reader.readlines():
                words_list = re.findall(r'\w+', sentence)
                word_counts = self._count_words(words_list)

                # Sending the whole list because when it's not in-mem I might want to do it in a bulk to save comms with persistence level
                WordCounterPersistence.increment(session, word_counts)
                WordCounterPersistence.flush_buffer(session)
        finally:
            session.close()

        return dict(success=True)

    def _count_words(self, words_list):
        counts = dict()
        for w in words_list:
            w = w.lower()
            if w not in counts:
                counts[w] = 1
            else:
                counts[w] += 1

        return counts
