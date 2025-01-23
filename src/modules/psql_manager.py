import logging
from ..config import DB_USERNAME
from .system import System

_PSQL_SIZE_CMD = "sudo psql -U {} -c \
'SELECT pg_database.datname as name, \
pg_database_size(pg_database.datname) as size \
FROM pg_database';".format(DB_USERNAME)

_ERR_PSQL_EXISTS = SystemError("PSQL не обнаружена на устройстве")
_ERR_PSQL_SIZE_FETCHING = SystemError("не удалось получить данные о размерах баз данных")


class PSQLManager:

    _logs_owner: str = __qualname__

    @classmethod
    def is_psql_exists(cls) -> bool:
        return not System.run_cmd("psql -V").returncode

    @classmethod
    def get_size(cls):
        try:
            if not cls.is_psql_exists():
                raise _ERR_PSQL_EXISTS

            shell = System.run_cmd(_PSQL_SIZE_CMD)
            if not shell.stdout or shell.stderr:
                raise _ERR_PSQL_SIZE_FETCHING

            raw_cmd_lines = shell.stdout.split("\n")
            if len(raw_cmd_lines) <= 4:
                raise _ERR_PSQL_SIZE_FETCHING

            db_name_size_tuple = tuple(
                (name, int(size)) for name, size in \
                (line.replace("|", "").split() for line in raw_cmd_lines[2:-3])
            )
            return sum(size for _, size in db_name_size_tuple)

        except Exception as err:
            logging.warning(f'{System._logs_owner}: {err}')
            print(err)
