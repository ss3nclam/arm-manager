import logging
import subprocess as sp


class ServiceExistError(Exception):
    """Исключение, вызываемое при попытке работы с несуществующей службой."""
    pass


class SystemService:
    """
    Класс для управления системными службами через команду `systemctl`.

    :param name: Имя службы. Если имя не заканчивается на `.service`,
    оно будет добавлено автоматически.
    :raises ServiceExistError: Если указанная служба не существует.
    """

    _VALID_ACTIONS = ("start", "stop", "restart")

    # def __init__(self, name: str):
    #     self._name = name if name.endswith(".service") else name + ".service"
    #     if not self._service_exists():
    #         raise ServiceExistError(f"службы {self._name!r} не существует")
    #     self._log_owner = f"{self.__class__.__name__}:{self._name}"

    def __init__(self, *args, **kwargs):
        """
        Запрещает создание экземпляра класса напрямую.

        :raises Exception: Всегда вызывает исключение, так как экземпляр
        должен создаваться через метод `_create`.
        """
        raise Exception(
            f"экземпляр класса {self.__class__.__name__} можно создать только при помощи класса System"
        )

    @classmethod
    def _create(cls, name: str):
        """
        Создает экземпляр класса `SystemService`.

        :param name: Имя службы.
        :return: Экземпляр класса `SystemService`.
        :raises ServiceExistError: Если указанная служба не существует.
        """
        obj = object.__new__(cls)
        obj._name = name if name.endswith(".service") else name + ".service"
        if not obj._service_exists():
            raise ServiceExistError(f"службы {obj._name!r} не существует")
        obj._log_owner = f"{obj.__class__.__name__}:{obj._name}"
        return obj

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self._name!r})"

    def _service_exists(self) -> bool:
        """
        Проверяет, существует ли служба в системе.

        :return: `True`, если служба существует, иначе `False`.
        :rtype: bool
        """
        result = sp.run(
            ["sudo", "systemctl", "show", "-p", "LoadState", self._name],
            stdout=sp.PIPE,
            text=True
        )
        return "LoadState=loaded" in result.stdout

    @property
    def name(self) -> str:
        """
        Возвращает имя службы.

        :return: Имя службы.
        :rtype: str
        """
        return self._name

    @property
    def state(self) -> str:
        """
        Возвращает текущее состояние службы.

        :return: Состояние службы (например, `active`, `inactive`, `failed`).
        :rtype: str
        """
        _log_owner = f"{self._log_owner}:state"
        try:
            cmd_args = ["sudo", "systemctl", "is-active", self._name]
            cmd = sp.run(cmd_args, stdout=sp.PIPE, text=True)
            return cmd.stdout.strip()
        except Exception as err:
            logging.exception(f"{_log_owner}: ошибка проверки статуса")

    def isactive(self) -> bool:
        """
        Проверяет, активна ли служба.

        :return: `True`, если служба активна, иначе `False`.
        :rtype: bool
        """
        return self.state == "active"

    def _manage_service(self, action: str, timeout: int) -> bool:
        """
        Вспомогательный метод для выполнения действий над службой.

        :param action: Действие (`start`, `stop`, `restart`).
        :param timeout: Максимальное время выполнения команды (в секундах).
        :return: `True`, если команда выполнена успешно, иначе `False`.
        :raises ValueError: Если действие недопустимо.
        """
        _log_owner = f"{self._log_owner}:{action}"
        if action not in self._VALID_ACTIONS:
            raise ValueError(f"недопустимое действие: {action!r}")
        elif action == self._VALID_ACTIONS[0] and self.isactive():
            logging.warning(f"{_log_owner}: сброс запуска, служба уже активна")
            return True
        elif action == self._VALID_ACTIONS[1] and not self.isactive():
            logging.warning(f"{_log_owner}: сброс останова, служба уже неактивна")
            return True
        try:
            cmd_args = ["sudo", "systemctl", action, self._name]
            sp.run(cmd_args, check=True, timeout=timeout)
            logging.info(f"{_log_owner}: команда успешно выполнена")
            return True
        except (sp.CalledProcessError, sp.TimeoutExpired) as err:
            msg = f"ненулевой код возврата ({err.returncode})" \
                if isinstance(err, sp.CalledProcessError) \
                else f"исчерпан лимит ожидания ({err.timeout} сек.)"
            logging.error(f"{_log_owner}: {msg}")
            return False
        except Exception as err:
            logging.exception(f"{_log_owner}: неизвестная ошибка: {err}")
            return False

    def start(self, timeout: int = 30) -> bool:
        """
        Запускает службу.

        :param timeout: Максимальное время выполнения команды (в секундах).
        :return: `True`, если команда выполнена успешно, иначе `False`.
        """
        return self._manage_service("start", timeout)

    def stop(self, timeout: int = 30) -> bool:
        """
        Останавливает службу.

        :param timeout: Максимальное время выполнения команды (в секундах).
        :return: `True`, если команда выполнена успешно, иначе `False`.
        """
        return self._manage_service("stop", timeout)

    def restart(self, timeout: int = 30) -> bool:
        """
        Перезапускает службу.

        :param timeout: Максимальное время выполнения команды (в секундах).
        :return: `True`, если команда выполнена успешно, иначе `False`.
        """
        return self._manage_service("restart", timeout)
