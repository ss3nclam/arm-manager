import logging
from .config import (
    LOGGING_CONFIG,
    MAX_DISKUSAGE_PERC,
    INSPECTION_FREQUENCY,
    EXIT_IF_FAILS,
)
from .modules import Scheduler, MPLC4, System


# TODO В следующей версии переписать алгоритм очистки
def main():

    mplc = MPLC4()

    def is_limit_reached():
        diskspace_info = System.get_disk_usage()
        diskspace_usage = diskspace_info.used / diskspace_info.total * 100
        out = diskspace_usage >= MAX_DISKUSAGE_PERC
        msg = f"использовано {diskspace_usage:.0f}/{MAX_DISKUSAGE_PERC}%, лимиты: {out!s}"
        logging.info(msg)
        return out

    @Scheduler.job
    def manage_arm():
        if not is_limit_reached():
            logging.info("лимиты не достигнуты, пропуск")
            return
        for timestamp in (i * 3_600 for i in (24, 12, 6, 3, 1)):
            logging.info(f"очистка записей системного журнала старше {timestamp} секунд")
            System.vacuum_journal(timestamp)
            if not is_limit_reached():
                return
        logging.info("очистка журнала mplc")
        mplc.journal.clear()
        if not is_limit_reached():
            return
        logging.info("пересоздание архивных баз данных mplc")
        mplc.service.stop()
        mplc.archive.recreate()
        mplc.service.start()
        if not is_limit_reached():
            return
        logging.warning("после очистки лимиты всё ещё превышены")
        if EXIT_IF_FAILS:
            System.exit(3)

    Scheduler.run(INSPECTION_FREQUENCY)
