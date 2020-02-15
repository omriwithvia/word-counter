import logging

from sqlalchemy.engine import url as sqlalchemy_url, create_engine
from sqlalchemy.orm import sessionmaker


class WordCounterPersistence(object):
    # Assuming I have a chance to tune this number with big data sets before going live :joy:
    MAX_BUFFER_SIZE = 1000

    COUNT_BUFFER = dict()

    @classmethod
    def increment(cls, session, words_diff):
        for w in words_diff:
            logging.debug('Adding {!s} to word {!s}', words_diff[w], w)
            cls.COUNT_BUFFER[w] = cls.COUNT_BUFFER.get(w, 0) + words_diff[w]

        cls.flush_if_needed(session)

    @classmethod
    def stats(cls, session, word_value):
        # Assuming we don't have SQL injection. Not handling now - TODO before going to production
        total_count = session.execute("select total_count from wordcounts where word_value = '{!s}'".format(word_value)).scalar()
        return total_count

    @classmethod
    def flush_buffer(cls, session):
        words_to_update = cls.COUNT_BUFFER.keys()
        if not words_to_update:
            return

        # Surround each word with quotes, and join with commas TODO make it more readable
        words_with_quotes = [w.join(2*["'"]) for w in words_to_update]
        words_string = ','.join(words_with_quotes)
        existing_words = cls._update_existing_words(session, words_string)
        cls._insert_new_words(session, existing_words)

        session.commit()
        # Assuming garbage collection kicks in fast enough to clean previous dict.
        cls.COUNT_BUFFER = dict()

    @classmethod
    def _update_existing_words(cls, session, words_string):
        existing_words = session.execute(
            'select word_value from wordcounts where word_value in ({!s})'.format(words_string))
        if existing_words.rowcount == 0:
            return []
        existing_word_values = [w[0] for w in existing_words]
        update_queries = ["update wordcounts set total_count = total_count + {!s} where word_value = '{!s}';"
                              .format(cls.COUNT_BUFFER[w], w) for w in existing_word_values]
        # Didn't go into details but assuming multi=True means we're doing only one round-trip to the DB
        conn = session.connection().connection
        cursor = conn.cursor()  # get mysql db-api cursor
        cursor.execute(''.join(update_queries))

        return existing_word_values

    @classmethod
    def flush_if_needed(cls, session):
        if len(cls.COUNT_BUFFER.keys()) <= cls.MAX_BUFFER_SIZE:
            cls.flush_buffer(session)

    @classmethod
    def _insert_new_words(cls, session, existing_words):
        new_words = [w for w in cls.COUNT_BUFFER if w not in existing_words]
        if not new_words:
            return
        values_string = ','.join(["('{!s}', {!s})".format(w, cls.COUNT_BUFFER[w]) for w in new_words])
        insert_queries = 'insert into wordcounts (word_value, total_count) values {!s}'.format(values_string)
        session.execute(insert_queries)


class SessionMakerFactory(object):
    @classmethod
    def get_session_maker(cls, db_driver, db_name, db_host, db_user, db_password, db_port):
        db_url = sqlalchemy_url.URL(db_driver, db_user, db_password, db_host, db_port, db_name)
        logging.info("using DB {!s}".format("mysql://{!s}:redacted@{!s}:{!s}/{!s}".format(
            db_user, db_host, db_port, db_name
        )))
        engine = create_engine(db_url)
        session_maker = sessionmaker(bind=engine, autoflush=False)
        return session_maker
