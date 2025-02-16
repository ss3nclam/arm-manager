import logging
from .current_project import CurrentProject
from .journal import Journal
from .archive import Archive
from ..system import System
from ..system_service import SystemService
from ...config import MPLC4_PATH

class MPLC4:

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MPLC4, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        try:
            if System.get_dir_size(MPLC4_PATH) is None:
                raise FileNotFoundError("расположение mplc4 не обнаружено ")
            elif System._run_quiet(["psql", "--version"]):
                raise SystemError("в системе не обнаружено psql")
        except Exception as err:
            logging.critical(f"{self.__class__.__name__}: {err}")
            System.exit(1)

        self._service = System.get_service("mplc4.service")
        self._project = CurrentProject()
        self._journal = Journal()
        self._archive = Archive()

    @property
    def service(self) -> SystemService:
        return self._service

    @property
    def project(self) -> CurrentProject:
        return self._project

    @property
    def journal(self) -> Journal:
        return self._journal

    @property
    def archive(self) -> Archive:
        return self._archive
