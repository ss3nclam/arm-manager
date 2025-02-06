import logging
import os
import sys
from collections import namedtuple
from platform import system
from shutil import disk_usage
from time import sleep

ntuple_memusage = namedtuple("MemUsage", "total used free")


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

    if system() != "Linux":
        sys.exit(1)

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
        :raises Exception: Если не удалось получить данные о загрузке CPU.
        """
        try:
            idle, total = cls._get_cpu_time()
            sleep(0.1)
            idle2, total2 = cls._get_cpu_time()
            return (1 - (idle2 - idle) / (total2 - total)) * 100
        except Exception as err:
            msg = "не удалось получить данные о загрузке процессора"
            logging.warning(f"{cls.__name__}: {msg}: {err}")

    @classmethod
    def get_mem_usage(cls):
        """
        Возвращает информацию об использовании оперативной памяти.

        :return: Именованный кортеж с полями:
            - `total`: Общий объем памяти (в байтах).
            - `used`: Используемый объем памяти (в байтах).
            - `free`: Свободный объем памяти (в байтах).
        :rtype: ntuple_memusage
        :raises Exception: Если не удалось получить данные об использовании памяти.
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
            logging.warning(f"{cls.__name__}: {msg}: {err}")

    @classmethod
    def get_disk_usage(cls):
        """
        Возвращает информацию об использовании дискового пространства.

        :return: Именованный кортеж с полями:
            - `total`: Общий объем дискового пространства (в байтах).
            - `used`: Используемый объем дискового пространства (в байтах).
            - `free`: Свободный объем дискового пространства (в байтах).
        :rtype: ntuple_memusage
        :raises Exception: Если не удалось получить данные об использовании диска.
        """
        try:
            return ntuple_memusage(*disk_usage("/"))
        except Exception as err:
            msg = "не удалось получить данные об использовании дискового пространства"
            logging.warning(f"{cls.__name__}: {msg}: {err}")

    @classmethod
    def get_file_size(cls, filepath: str):
        """
        Возвращает размер файла в байтах.

        :param filepath: Путь к файлу.
        :type filepath: str
        :return: Размер файла в байтах.
        :rtype: int
        :raises FileNotFoundError: Если файл не существует.
        :raises Exception: Если не удалось получить данные о размере файла.
        """
        try:
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"пути {filepath!r} не существует")
            return os.path.getsize(filepath)
        except Exception as err:
            msg = "не удалось получить данные о размере файла"
            logging.warning(f"{cls.__name__}: {msg}: {err}")

    @classmethod
    def get_dir_size(cls, path: str):
        """
        Возвращает общий размер директории в байтах.

        :param path: Путь к директории.
        :type path: str
        :return: Общий размер директории в байтах.
        :rtype: int
        :raises SystemError: Если директория не существует.
        :raises Exception: Если не удалось получить данные о размере директории.
        """
        try:
            if not os.path.exists(path):
                raise SystemError(f"пути {path!r} не существует")
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
            logging.warning(f"{cls.__name__}: {msg}: {err}")
