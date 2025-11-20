from collections import namedtuple
from datetime import datetime
import json
import logging

from ...config import MPLC4_PATH

ntuple_projectinfo = namedtuple(
    "ProjectInfo", "name last_modified_time"
)

class CurrentProject:
    """
    Класс для работы с текущим проектом MPLC4.

    Предоставляет информацию о проекте,
    такую как его имя и время последнего изменения.
    """

    def __init__(self):
        self._log_owner = self.__class__.__name__

    # BUG Возможно тормозит загрузку проекта на арм
    # TESTME Протестировать без vpn
    def _read_project_config(self):
        """
        Читает конфигурационный файл проекта (ProjInfo.json)
        и возвращает его содержимое в виде словаря.

        :return: Содержимое конфигурационного файла в виде словаря.
        :rtype: dict
        :raises FileNotFoundError: Если файл конфигурации не найден.
        """
        path = f"{MPLC4_PATH}/server/cfg/ProjInfo.json"
        with open(path, "r") as file:
            return dict(json.load(file))

    @property
    def info(self):
        """
        Возвращает информацию о текущем проекте.

        :return: Именованный кортеж с полями:
            - `name`: Имя проекта.
            - `last_modified_time`: Время последнего изменения проекта
            в формате struct_time.
        :rtype: ntuple_projectinfo
        """
        try:
            cfg = self._read_project_config()
            name = cfg.get("ProjectName", None)
            last_modified_time_str = cfg.get(
                "VersionEditsInfo", {}
            ).get("Дата последнего изменения", None)
            last_modified_time = None \
                if not last_modified_time_str \
                else datetime.strptime(last_modified_time_str, "%d.%m.%Y %H:%M:%S.%f")
            return ntuple_projectinfo(name, last_modified_time)
        except FileNotFoundError:
            logging.warning(f"{self._log_owner}: файл конфигурации не найден")
        except Exception as err:
            logging.exception(f"{self._log_owner}: неизвестная ошибка: {err}")
