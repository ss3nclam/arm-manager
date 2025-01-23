import logging
import sys

from .system import System


class SystemService(object):

    def __init__(self, name: str) -> None:
        self.name: str = name
        self._logs_owner: str = f'{self.__class__.__name__}:{self.name}'


    @property
    def state(self):
        try:
            cmd: str = f'sudo systemctl is-active {self.name}'
            shell = System.run_cmd(cmd)
            return shell.stdout.strip()
        except Exception:
            shell_error: str = shell.stderr.strip()
            logging.error(f'{self._logs_owner}: ошибка проверки статуса: {shell_error}')
            return None


    def isactive(self):
       return self.state == 'active'


    def start(self) -> None:
        if not self.isactive():
            logging.info(f'{self._logs_owner}: запуск..')
            cmd: str = f'sudo systemctl start {self.name}'
            shell = System.run_cmd(cmd)

            try:
                if self.isactive():
                    logging.info(f'{self._logs_owner}: успешно запущена')

                else:
                    shell_error: str = shell.stderr.strip('\n')
                    raise SystemError(f'неудачное выполнение команды - {shell_error}')

            except Exception as error:
                logging.error(f'{self._logs_owner}: ошибка запуска: {error}')
                sys.exit(1)

        else:
            logging.warning(f'{self._logs_owner}: уже запущена')


    def stop(self):
        # TODO Написать метод для остановки службы
        pass


    def restart(self):
        if self.isactive():
            logging.info(f'{self._logs_owner}: перезапуск..')
            cmd: str = f'sudo systemctl restart {self.name}'
            shell = System.run_cmd(cmd)

            try:
                if self.isactive():
                    logging.info(f'{self._logs_owner}: успешно перезапущена')

                else:
                    shell_error: str = shell.stderr.strip('\n')
                    logging.warning(f'{self._logs_owner}: не удалось перезапустить - "{shell_error}", попытка принудительного запуска..')

                    self.start()

                    if not self.isactive():
                        raise SystemError(f'не удалось перезапустить и принудительно запустить')

            except Exception as error:
                logging.error(f'{self._logs_owner}: ошибка перезапуска: {error}')
                sys.exit(1)

        else:
            logging.warning(f'{self._logs_owner}: неактивна')
            self.start()
