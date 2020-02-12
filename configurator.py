import logging
import os


class WordCounterConfigurator(object):
    # This class is here in order to hide configuration implementation from the application

    def get_port(self):
        # Using system variables because it could be useful to configure from outside
        # if we want to go with Docker/K8S/Lambda/whatever.
        return os.getenv('PORT', 8080)

    def get_log_level(self):
        return os.getenv('LOG_LEVEL', logging.DEBUG)
    #
    # def get_db_params(self):
    #     return dict(db_driver=os.getenv('DB_DRIVER', 'mysql'),
    #                 db_host=os.getenv('DB_DRIVER', 'mysql'),
    #                 db_user=os.getenv('DB_DRIVER', 'mysql'),
    #                 db_password=os.getenv('DB_DRIVER', 'mysql'),
    #                 db_name=os.getenv('DB_DRIVER', 'mysql'),
    #                 db_name=os.getenv('DB_DRIVER', 'mysql'),
    #                 db_name=os.getenv('DB_DRIVER', 'mysql'),
    #                 )
