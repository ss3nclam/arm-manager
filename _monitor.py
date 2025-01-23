#!/usr/bin/python3

# import argparse

# from os import get_terminal_size

from src.modules import System as sm
from src.modules import SystemService

# _APP_DESCRIPTION = \
# """
# Приложение для получения сводки информации
# """
# _args_parser = argparse.ArgumentParser(description=_APP_DESCRIPTION)
# _args_parser.add_argument('-s', '--size', type=int, help='Пример флага')
# _args_parser.add_argument('-c', '--color', action='store_true', help='Пример числового аргумента', )

# args = _args_parser.parse_args()

OUT_WIDTH: int = 40
# OUT_WIDTH = get_terminal_size(0).columns
DIR_SIZE_UNIT: str = "GB"
TITLE_COLOR: str = "default"
COLORED_ALL: bool = True
# COLORED_ALL: bool = args.color
COLORED_PERCENT_USAGE: bool = True
COLORED_SERVICE_STATE: bool = True

_K_UNITS = {
    "KB": 1,
    "MB": 2,
    "GB": 3,
}
_FCOLSIZE = OUT_WIDTH // 2
_SCOLSIZE = OUT_WIDTH - _FCOLSIZE
_SERVICES_LIST = ["postgresql", "mplc4", "mplc4-cleaner"]
_SERVICES_STATES_COLORS = {
    "active": "default",
    "inactive": "red",
    "activating": "yellow",
    "deactivating": "yellow",
    "failed": "red",
    "not-found": "red",
    "dead": "red",
}
_ANSI_COLORS = {
    "red": "\033[1;31m",
    "green": "\033[1;32m",
    "yellow": "\033[1;33m",
    "blue": "\033[1;34m",
    "purple": "\033[1;35m",
    "cyan": "\033[1;36m",
    "end": "\033[0m",
}
_ERR = (
   ("передан некорректный тип процента использования", 1),
   ("передан некорректный тип порогов индикации", 2),
   ("значение порога индикации может быть только в пределах 0-100", 3),
   ("предупредительный порог индикации не может быть больше критического", 4),
   ("ошибка вычисления размера каталога", 5),
)


def colored(string: str, color: str) -> str:
    if not COLORED_ALL:
        color = "default"
    if color == "default":
        return string
    return _ANSI_COLORS[color] + f"{string!s}" + _ANSI_COLORS["end"]


def get_services_info():
    out = []
    for service in _SERVICES_LIST:
        state = SystemService(service).state
        color = "default" if not COLORED_SERVICE_STATE \
            else _SERVICES_STATES_COLORS[state]
        out.append(
            (service, colored(state, color))
        )
    return out


def format_percent_usage(
        percent_usage, warning_threshold: int = 80, crytical_threshold: int = 90
    ) -> str:
    try:
        if not isinstance(percent_usage, (int, float)):
            raise TypeError(*_ERR[0])
        elif not (
            isinstance(warning_threshold, int) and \
            isinstance(warning_threshold, int)
        ):
            raise TypeError(*_ERR[1])
        elif not (
            (warning_threshold in range(101)) or (warning_threshold in range(101))
        ):
            raise ValueError(*_ERR[2])
        elif crytical_threshold < warning_threshold:
            raise AttributeError(*_ERR[3])
        else:
            color = "default"
            if COLORED_PERCENT_USAGE:
                if 0 <= percent_usage <= warning_threshold:
                    pass
                elif percent_usage <= crytical_threshold:
                    color = "yellow"
                else:
                    color = "red"
            return colored(f"{percent_usage:.1f}%", color)
    except Exception as err:
        return colored(f"ERR{err.args[1]}", "red")


def format_dir_size(value: float):
    try:
        if value is None:
            raise ValueError(*_ERR[4])
        else:
            return f"{value / 1024**_K_UNITS[DIR_SIZE_UNIT]:.2f} {DIR_SIZE_UNIT}"
    except Exception as err:
        return colored(f"ERR{err.args[1]}", "red")


_len_ansi = lambda s: 0 if not "\033[" in f"{s!s}" else 11
_title = lambda s: f" {s} ".center(_FCOLSIZE + _SCOLSIZE + _len_ansi(s), "-")
_col1 = lambda s: s.ljust(_FCOLSIZE + _len_ansi(s))
_col2 = lambda s: s.rjust(_SCOLSIZE + _len_ansi(s))


def make_table(lines) -> str:
    out_lines = []
    for line in lines:
        if isinstance(line, (tuple, list)):
            out_lines.append(_col1(line[0]) + _col2(line[1]))
        elif isinstance(line, str):
            if line != "":
                out_lines.append(_title(colored(line, TITLE_COLOR)))
            else:
                out_lines.append(line)
    out = "\n".join(out_lines)
    return out


def main():
    cpu_usage = format_percent_usage(sm.get_cpu_usage())
    ram_usage = format_percent_usage(sm.get_ram_usage())
    disk_usage, disk_usage_detail = sm.get_diskspace_usage(True)
    disk_usage = format_percent_usage(disk_usage)
    psql_size = format_dir_size(sm.get_dir_size("/var/lib/pgsql"))
    mplc4_log_size = format_dir_size(sm.get_dir_size("/opt/mplc4/log"))
    sys_log_size = format_dir_size(sm.get_dir_size("/var/log/journal"))

    lines = (
        "Services",
        *get_services_info(),
        "",
        "System",
        ("CPU", cpu_usage),
        ("RAM", ram_usage),
        ("Diskspace", disk_usage),
        ("Diskspace (detail)", disk_usage_detail),
        "",
        "Directories",
        ("PSQL", psql_size),
        ("MPLC4 log", mplc4_log_size),
        ("System log", sys_log_size),
    )
    out = make_table(lines)
    print(out)


if __name__ == "__main__":
    main()
