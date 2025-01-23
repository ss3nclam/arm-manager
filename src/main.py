import logging

from .config import logging_config
from .modules.mplc4_logs_manager import MPLC4LogsManager
from .modules.scheduler import Scheduler
from .modules.system_service import SystemService


def main():

    scheduler = Scheduler()
    lm = MPLC4LogsManager()


    @scheduler.job
    def manage_logs():
        if not lm.is_limits_reached():
            logging.info(f'{lm.cls_name}: лимиты не превышены')
            return

        logging.info(f'{lm.cls_name}: лимиты превышены')
        lm.remove('unused')

        if lm.is_limits_reached():
            warning_msg: str = 'лимиты всё ещё превышены,' + \
            'будут удалены используемые файлы и перезапущена служба mplc4'
            logging.warning(f'{lm.cls_name}: {warning_msg}')

            if lm.remove('used'):
                mplc4_service = SystemService('mplc4')
                mplc4_service.restart()

            if mplc4_service.isactive() and not lm.is_limits_reached():
                return

            elif not mplc4_service.isactive():
                logging.warning(
                    f'{lm.cls_name}: не удалось запустить службу mplc4'
                )

            elif lm.is_limits_reached():
                logging.warning(
                    f'{lm.cls_name}: не удалось очистить физ. память доступными службе средствами'
                )


    scheduler.run()
