#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse as ap
import logging
from os import get_terminal_size
import time

from src import ArmReportMaker as rm
from src import System as sm
from src import SystemService

_ERR = [
    "неподдерживаемая единица измерения, ожидается KB | MB | GB",
    "передан некорректный тип значения, ожидается int",
]

_ERR_ALL = rm._ERR + _ERR

def _get_err_code(err):
    if err.args[0] not in _ERR_ALL:
        err_code = 66
    else:
        err_code = _ERR_ALL.index(err.args[0]) + 1
    return err_code

_ERRS_DN = ";\n".join(f"{i + 1} - {d}" for i, d in enumerate(_ERR_ALL))

_APP_DN = "Приложение для сбора информации о работе ARM'а"
_APP_EPILOG = \
f"""
Коды ошибок: {_ERRS_DN}.
"""
_COLOR_FLAG_DN = "цветовая индикация пороговых значений"
_UNIT_FLAG_DN = "единица измерения размера отслеживаемых директорий (по умоланию GB)"
_WIDTH_FLAG_DN = "ширина вывода (40-100), при ином значении \
будет растягиваться во всю ширину терминала (по умоланию 40)"

_ap = ap.ArgumentParser(description=_APP_DN, epilog=_APP_EPILOG)
_ap.add_argument(
    '-c',
    '--color',
    action='store_true',
    help=_COLOR_FLAG_DN,
)
_ap.add_argument(
    '-u',
    '--size-unit',
    type=str,
    default="GB",
    help=_UNIT_FLAG_DN,
    choices=("KB", "MB", "GB"),
)
_ap.add_argument(
    '-w',
    '--width',
    type=int,
    default=40,
    help=_WIDTH_FLAG_DN,
)
args = _ap.parse_args()

import os
import subprocess

def _restart_with_watch():
    script_name = os.path.basename(__file__)
    command = f"watch -n 1 python3 {script_name}"
    print(f"Перезапуск скрипта с помощью команды: {command}")
    subprocess.run(command, shell=True)

tracked_services = [
    "postgresql",
    "mplc4",
    "mplc4-cleaner",
]

try:
    rm.colored_all = args.color

    if args.size_unit not in rm._K_UNITS:
        raise ap.ArgumentError(args.width, _ERR_ALL[6])
    else:
        rm.dir_size_unit = args.size_unit

    if not isinstance(args.width, int):
        raise ap.ArgumentError(args.width, _ERR_ALL[7])
    elif args.width not in range(40, 101):
        rm.table_width = get_terminal_size(0).columns
    else:
        rm.table_width = args.width

    # rm.title_color = "default"
    # rm.colored_percent_usage = True
    # rm.colored_service_state = True

    if __name__ == "__main__":
        # print("kek")
        services_states = []
        for name in tracked_services:
            service = SystemService(name)
            state = service.state
            services_states.append((name, state))
        disk_usage_summary = sm.get_diskspace_usage(True)
        report = rm.make_report(
            services_states = tuple(services_states),
            cpu_usage = sm.get_cpu_usage(),
            ram_usage = sm.get_ram_usage(),
            # disk_usage_summary = sm.get_diskspace_usage(True),
            disk_usage = disk_usage_summary[0],
            disk_usage_detail = disk_usage_summary[1],
            psql_size = sm.get_dir_size("/var/lib/pgsql"),
            mplc4_log_size = sm.get_dir_size("/opt/mplc4/log"),
            sys_log_size = sm.get_dir_size("/var/log/journal"),
        )
        print(report)

except Exception as err:
    print(err)
    logging.exception(err)
    exit(_get_err_code(err))
