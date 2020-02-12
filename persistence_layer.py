import logging

word_counter = dict()


# Currently assuming single process single machine, no need for persistence
class WordCounterPersistence(object):
    @classmethod
    def increment(cls, words_diff):
        for w in words_diff:
            logging.debug('Adding {!s} to word {!s}', words_diff[w], w)
            word_counter[w] = word_counter.get(w, 0) + words_diff[w]

    @classmethod
    def stats(cls, word_value):
        return word_counter.get(word_value, 0)
