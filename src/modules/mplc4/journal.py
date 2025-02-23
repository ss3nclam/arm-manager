import os
from ...config import MPLC4_PATH
from ..system import System


# TODO Добавить обработку исключений
class Journal:

    def __init__(self):
        self._log_owner = self.__class__.__name__
        self._pathdir = MPLC4_PATH + "/log"

    def _fetch_logfile_names(self):
        names_list: list = os.listdir(self._pathdir)
        try:
            names_list.remove('start_log.txt')
        finally:
            return names_list

    @property
    def size(self):
        return System.get_dir_size(self._pathdir)

    def clear(self, all: bool = False):
        # TODO Добавить логику для настраиваемой очистки
        filepaths_list = (
            f"{self._pathdir}/{name}" for name in self._fetch_logfile_names()
        )
        for filepath in filepaths_list:
            if not all:
                if System.isusedfile(filepath):
                    continue
            System.remove_file(filepath)
