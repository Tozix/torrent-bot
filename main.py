import os

import logger
from telegram import MyBot

log = logger.setup_applevel_logger(file_name='logs/main.log')

if __name__ == '__main__':
    try:
        log.debug('Старт программы')
        my_bot = MyBot()
        my_bot.start()
    except KeyboardInterrupt:
        print('Выход из программы')
        os._exit(1)