# REFACT Переписать конфиг в класс
import logging
import sys
import json

try:
    with open('./config.json', "r") as file:
        cfg = dict(json.load(file))

    LOGGING_CONFIG = logging.basicConfig(
        format = cfg['LOGGING']['format'],
        level = cfg['LOGGING']['level'],
    )
    MAX_DISK_USAGE: int = cfg ["CLEANER"]["max_disk_usage"]
    INSPECTION_FREQUENCY: int = cfg ["CLEANER"]["inspection_frequency"]
    MPLC4_PATH = "/opt/mplc4"
    IGNORED_FILES: tuple = (
        'start_log.txt'
    )
    _SIZE_UNITS_K = {
        "B": 0,
        "KB": 1,
        "MB": 2,
        "GB": 3,
    }
except Exception as error:
    logging.error(f' ошибка чтения конфига - "{error}", завершение работы..')
    sys.exit(1)
