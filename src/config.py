import logging
import sys
from configparser import ConfigParser
from os import path

PROJECT_PATH: str = path.split(path.dirname(__file__))[0]

config = ConfigParser()

try:
    config.read(f'{PROJECT_PATH}/config.conf')

    logging_config = logging.basicConfig(
        filename = f'{PROJECT_PATH}/cleaner.log' if config.getboolean('logging', 'to_file') else None,
        format = '%(asctime)s:%(levelname)s:%(message)s',
        level = {
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'debug': logging.DEBUG,
            }.get(config['logging']['level'].lower(), 'debug')
        ) if \
            config.getboolean('logging', 'logging') else None

    getstr = lambda section, option: config.get(section, option)
    getint = lambda section, option: config.getint(section, option)

    MAX_DISK_USAGE: int = getint('defaults', 'max_disk_usage')
    MAX_LOGS_COUNT: int = getint('defaults', 'max_logs_count')
    INSPECTION_FREQUENCY: int = getint('defaults', 'inspection_frequency')
    _MPLC4_LOG_DIR: str = '/opt/mplc4/log'
    IGNORED_FILES: tuple = (
        'start_log.txt'
    )

    DB_USERNAME: str = getstr("database", "user")
    _SIZE_UNITS_K = {
        "B": 0,
        "KB": 1,
        "MB": 2,
        "GB": 3,
    }

except Exception as error:
    logging.error(f' ошибка чтения конфига - "{error}", завершение работы..')
    sys.exit(1)
