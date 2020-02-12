import logging

from app import WordCounterApplication
from configurator import WordCounterConfigurator


def main():
    configurator = WordCounterConfigurator()    # This can later be used with some yaml fle to get configuration if we like
    rider_payments_server = WordCounterApplication.from_configurator(configurator)
    # logging.

    # This line is blocking, no other lines will run after this one
    rider_payments_server.start_app()


if __name__ == '__main__':
    main()
