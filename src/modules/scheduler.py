import logging
import time
from sys import exit

from ..config import INSPECTION_FREQUENCY


class Scheduler:

    def __init__(self) -> None:
        self.__logs_owner: str = f'{self.__class__.__name__}'

        self.__jobs_list = []


    def job(self, func) -> None:
        func_name: str = func.__name__

        self.__jobs_list.append((func_name, func))
        logging.info(f'{self.__logs_owner}:{func_name}: работа запланирована')


    def run(self) -> None:
        while True:
            for job_name, job in self.__jobs_list:
                logging.info(f'{self.__logs_owner}:{job_name}: запуск')

                try:
                    job()
                    logging.info(f'{self.__logs_owner}:{job_name}: завершение')

                except Exception as error:
                    logging.error(f'{self.__logs_owner}:{job_name}: ошибка запуска - {error}')
                    exit(1)

            logging.info(f'{self.__logs_owner}: ожидание..')
            time.sleep(INSPECTION_FREQUENCY)
