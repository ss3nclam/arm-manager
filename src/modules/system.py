import logging
import os
import subprocess as sp
import sys
import collections
import platform
import shutil
import time

from .system_service import SystemService

ntuple_memusage = collections.namedtuple("MemUsage", "total used free")


class NotAFileError(Exception):
    """Исключение, вызываемое, если путь не является файлом."""
    pass


class NotADirectoryError(Exception):
    """Исключение, вызываемое, если путь не является директорией."""
    pass


class System:
    """
    Класс для получения системной информации,
    такой как использование CPU, памяти,
    диска и размер файлов/директорий.

    .. note::
        Класс работает только на Linux-системах.
        При попытке использования на других ОС
        программа завершится с кодом 1.
    """

    exit = lambda status: sys.exit(status)

    def _run_quiet(args: list) -> int:
        """
        Внутренний метод для выполнения команды без вывода в консоль.

        :param args: Список аргументов команды.
        :type args: list
        :return: Код возврата команды.
        :rtype: int
        """
        return sp.run(
            args,
            stdout = sp.DEVNULL,
            stderr = sp.DEVNULL,
        ).returncode

    try:
        if platform.system() != "Linux":
            raise SystemError("система не соответствует требованиям")
        elif os.geteuid():
            raise PermissionError("недостаточно прав для запуска")
        elif _run_quiet(["systemctl", "--version"]):
            raise SystemError("в системе не обнаружено systemd")
        elif _run_quiet(["lsof", "-h"]):
            raise SystemError("в системе не обнаружено lsof")
    except Exception as err:
        logging.critical(f"{__qualname__}: {err}")
        exit(1)

    @classmethod
    def _get_cpu_time(cls):
        """
        Внутренний метод для получения данных о времени работы CPU
        из `/proc/stat`.

        :return: Кортеж из двух значений: время простоя (idle)
        и общее время работы CPU (total).
        :rtype: tuple[int, int]
        """
        with open("/proc/stat", "r") as file:
            line = file.readline()
            parts = line.split()
            idle = int(parts[4])
            total = sum(map(int, parts[1:8]))
        return idle, total

    @classmethod
    def get_cpu_usage(cls):
        """
        Возвращает текущую загрузку CPU в процентах.

        :return: Загрузка CPU в процентах (от 0 до 100).
        :rtype: float
        """
        try:
            idle, total = cls._get_cpu_time()
            time.sleep(0.1)
            idle2, total2 = cls._get_cpu_time()
            return (1 - (idle2 - idle) / (total2 - total)) * 100
        except Exception as err:
            msg = "не удалось получить данные о загрузке процессора"
            logging.error(f"{cls.__name__}:get_cpu_usage: {msg}: {err}")

    @classmethod
    def get_mem_usage(cls):
        """
        Возвращает информацию об использовании оперативной памяти.

        :return: Именованный кортеж с полями:
            - `total`: Общий объем памяти (в байтах).
            - `used`: Используемый объем памяти (в байтах).
            - `free`: Свободный объем памяти (в байтах).
        :rtype: ntuple_memusage
        """
        try:
            with open("/proc/meminfo", "r") as file:
                lines = tuple(
                    map(
                        lambda x: int(x.split()[1]) * 2**10,
                        file.readlines()[:5],
                    )
                )
            total, free = lines[:2]
            buff_cache = sum(lines[3:5])
            used = total - free - buff_cache
            return ntuple_memusage(total, used, total - used)
        except Exception as err:
            msg = "не удалось получить данные об использовании оперативной памяти"
            logging.error(f"{cls.__name__}:get_mem_usage: {msg}: {err}")

    @classmethod
    def get_disk_usage(cls):
        """
        Возвращает информацию об использовании дискового пространства.

        :return: Именованный кортеж с полями:
            - `total`: Общий объем дискового пространства (в байтах).
            - `used`: Используемый объем дискового пространства (в байтах).
            - `free`: Свободный объем дискового пространства (в байтах).
        :rtype: ntuple_memusage
        """
        try:
            return ntuple_memusage(*shutil.disk_usage("/"))
        except Exception as err:
            msg = "не удалось получить данные об использовании дискового пространства"
            logging.error(f"{cls.__name__}:get_disk_usage: {msg}: {err}")

    @classmethod
    def _check_path_exists(cls, path: str):
        """
        Проверяет, существует ли указанный путь.

        :param path: Путь для проверки.
        :type path: str
        :raises FileNotFoundError: Если путь не существует.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"пути {path!r} не существует")

    @classmethod
    def _check_is_file(cls, path: str):
        """
        Проверяет, является ли указанный путь файлом.

        :param path: Путь для проверки.
        :type path: str
        :raises NotAFileError: Если путь не является файлом.
        """
        cls._check_path_exists(path)
        if not os.path.isfile(path):
            raise NotAFileError(f"путь {path!r} не является файлом")

    @classmethod
    def _check_is_dir(cls, path: str):
        """
        Проверяет, является ли указанный путь директорией.

        :param path: Путь для проверки.
        :type path: str
        :raises NotADirectoryError: Если путь не является директорией.
        """
        cls._check_path_exists(path)
        if not os.path.isdir(path):
            raise NotADirectoryError(f"путь {path!r} не является директорией")

    @classmethod
    def get_file_size(cls, path: str):
        """
        Возвращает размер файла в байтах.

        :param filepath: Путь к файлу.
        :type filepath: str
        :return: Размер файла в байтах.
        :rtype: int
        """
        try:
            cls._check_is_file(path)
            return os.path.getsize(path)
        except Exception as err:
            msg = "не удалось получить данные о размере файла"
            logging.error(f"{cls.__name__}:get_file_size: {msg}: {err}")

    @classmethod
    def isusedfile(cls, path: str) -> bool:
        """
        Проверяет, используется ли файл каким-либо процессом.

        :param path: Путь к файлу.
        :type path: str
        :return: `True`, если файл используется, иначе `False`.
        :rtype: bool
        """
        try:
            cls._check_is_file(path)
            sp.run(
                ["sudo", "lsof", path],
                stdout = sp.DEVNULL,
                stderr = sp.DEVNULL,
                check = True,
            )
            return True
        except sp.CalledProcessError as err:
            return False
        except Exception as err:
            msg = "не удалось проверить использование файла"
            logging.error(f"{cls.__name__}:isusedfile: {msg}: {err}")
            return False


    @classmethod
    def get_dir_size(cls, path: str):
        """
        Возвращает общий размер директории в байтах.

        :param path: Путь к директории.
        :type path: str
        :return: Общий размер директории в байтах.
        :rtype: int
        """
        try:
            cls._check_is_dir(path)
            total_size = 0
            for dirpath, _, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    size = cls.get_file_size(filepath)
                    if size:
                        total_size += size
            return total_size
        except Exception as err:
            msg = "не удалось получить данные о размере директории"
            logging.error(f"{cls.__name__}:get_dir_size: {msg}: {err}")

    @classmethod
    def _remove(cls, target_type: str, path: str) -> bool:
        """
        Внутренний метод для удаления файла или директории.

        :param target_type: Тип цели для удаления. Допустимые значения:
        "file" (файл) или "dir" (директория).
        :type target_type: str
        :param path: Путь к файлу или директории, которые нужно удалить.
        :type path: str
        :return: `True`, если удаление прошло успешно, иначе `False`.
        :rtype: bool
        """
        _log_owner = f"{cls.__name__}:remove_{target_type}"
        try:
            if target_type == "file":
                cls._check_is_file(path)
                os.remove(path)
            elif target_type == "dir":
                cls._check_is_dir(path)
                shutil.rmtree(path)
            else:
                raise ValueError("некорректное значение аргумента target_type")
            return True
        except (FileNotFoundError, NotAFileError, NotADirectoryError, ValueError) as err:
            logging.error(f"{_log_owner}: {err}")
            return False
        except Exception as err:
            logging.exception(f"{_log_owner}: неизвестная ошибка: {err}")
            return False

    @classmethod
    def remove_file(cls, path: str) -> bool:
        """
        Удаляет файл по указанному пути.

        :param path: Путь к файлу, который нужно удалить.
        :type path: str
        :return: `True`, если файл успешно удалён, иначе `False`.
        :rtype: bool
        """
        return cls._remove("file", path)

    @classmethod
    def remove_dir(cls, path: str) -> bool:
        """
        Удаляет директорию по указанному пути.
        Директория удаляется рекурсивно, включая все её содержимое.

        :param path: Путь к директории, которую нужно удалить.
        :type path: str
        :return: `True`, если директория успешно удалена, иначе `False`.
        :rtype: bool
        """
        return cls._remove("dir", path)

    @classmethod
    def get_service(cls, name: str):
        """
        Возвращает объект SystemService для управления службой.

        :param name: Имя службы.
        :type name: str
        :return: Объект SystemService для управления службой.
        :rtype: SystemService
        """
        return SystemService._create(name)

    @classmethod
    def get_journal_size(cls):
        """
        Возвращает общий размер системного журнала,
        расположенного в директории /var/log.

        :return: Общий размер журнала в байтах.
        :rtype: int
        """
        return cls.get_dir_size("/var/log")

    @classmethod
    def vacuum_journal(cls, timestamp: int) -> bool:
        """
        Очищает системный журнал,
        удаляя записи старше указанного времени.

        :param timestamp: Время в секундах,
        старше которого записи будут удалены.
        :type timestamp: int
        :return: `True`, если очистка прошла успешно, иначе `False`.
        :rtype: bool
        """
        _log_owner = f"{cls.__name__}:vacuum_journal"
        try:
            if not isinstance(timestamp, int):
                raise TypeError("параметр timestamp может быть только типа int")
            sp.run(
                ["sudo", "journalctl", "--vacuum-time=" + f"{timestamp}s"],
                check = True,
                stdout = sp.DEVNULL,
                stderr = sp.DEVNULL,
            )
            return True
        except TypeError as err:
            logging.error(f"{_log_owner}: {err}")
            return False
        except sp.CalledProcessError as err:
            msg = "ненулевой код возврата команды"
            logging.error(f"{_log_owner}: {msg} - {err.returncode}: {err.stderr}")
            return False
        except Exception as err:
            logging.exception(f"{_log_owner}: неизвестная ошибка: {err}")
            return False
