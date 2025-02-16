import logging
import sys
import json

try:
    with open('./config.json', "r") as file:
        cfg = dict(json.load(file))

    LOGGING_CONFIG = logging.basicConfig(
        format = cfg['logging']['format'],
        level = cfg['logging']['level'],
    )
    MAX_DISKUSAGE_PERC: int = cfg["max_diskusage_perc"]
    INSPECTION_FREQUENCY: int = cfg["inspection_frequency"]
    MPLC4_PATH: str = cfg["mplc4_path"]
    IGNORED_FILES = (
        'start_log.txt'
    )
    PSQL_CFG = cfg["psql"]
except Exception as error:
    logging.error(f' ошибка чтения конфига - "{error}", завершение работы..')
    sys.exit(1)
