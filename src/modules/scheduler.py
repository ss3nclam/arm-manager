import logging
from sys import exit
from time import sleep


class Scheduler:

    _logs_owner: str = __qualname__
    _jobs = []

    @classmethod
    def job(cls, func) -> None:
        func_name: str = func.__name__

        cls._jobs.append((func_name, func))
        logging.info(f'{cls._logs_owner}:{func_name}: работа запланирована')

    @classmethod
    def run(cls, interval: int) -> None:
        while True:
            for job_name, job in cls._jobs:
                logging.info(f'{cls._logs_owner}:{job_name}: запуск')

                try:
                    job()
                    logging.info(f'{cls._logs_owner}:{job_name}: завершение')

                except Exception as error:
                    logging.error(f'{cls._logs_owner}:{job_name}: ошибка запуска - {error}')
                    exit(1)

            logging.info(f'{cls._logs_owner}: ожидание..')
            sleep(interval)
