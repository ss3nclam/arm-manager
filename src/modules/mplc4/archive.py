import subprocess

from ..system import System
from ...config import PSQL_CFG

SHELL_PSQL_TEMPLATE = "sudo psql -U {} -c {!r}"
DBS_SIZES = """SELECT pg_database.datname AS name, \
pg_database_size(pg_database.datname) AS size \
FROM pg_database ORDER by size DESC;"""
CREATE_DB = "CREATE DATABASE {dbname} OWNER {owner}"
DROP_DB = "DROP DATABASE IF EXISTS {dbname}"


# FIXME Весь класс на костылях, переписать
class Archive:

    def __init__(self):
        # self._log_owner = self.__class__.__name__
        self._service = System.get_service("postgresql")

    @property
    def service(self):
        return self._service

    def _run_sql_cmd(self, cmd: str, capture_output: bool = False):
        std = subprocess.DEVNULL if not capture_output else subprocess.PIPE
        return subprocess.run(
            SHELL_PSQL_TEMPLATE.format(PSQL_CFG["user"], cmd),
            shell=True,
            text=capture_output,
            stdout=std,
            stderr=std,
        )

    def _create_db(self, name: str):
        owner = "security" if "security" in name else "technology"
        self._run_sql_cmd(CREATE_DB.format(dbname=name, owner=owner))

    def _drop_db(self, name: str):
        self._run_sql_cmd(DROP_DB.format(dbname=name))

    @property
    def size(self):
        shell = self._run_sql_cmd(DBS_SIZES, True)
        if shell.returncode:
            return None
        name_size_gen = (
            map(str.strip, line.split(" |")) \
            for line in shell.stdout.split("\n")[2:-3]
        )
        return sum(
            int(size) for name, size in name_size_gen \
            if name in PSQL_CFG["manage_dbs"]
        )

    def recreate(self):
        for dbname in PSQL_CFG["manage_dbs"]:
            self._drop_db(dbname)
            self._create_db(dbname)
