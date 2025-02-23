#!/usr/bin/python3

from argparse import ArgumentParser

from src import Monitor, Report
import logging

ap = ArgumentParser(description="Утилита для мониторинга работы ARM'а", add_help=False)

ap.add_argument(
    "--help",
    action = "store_true",
    help = "Показать справку и выйти",
)
ap.add_argument(
    "-n",
    "--interval",
    type = int,
    default = 2,
    help = "Интервал обновлений в сек. (если 0, будет сделан один снимок)",
)
ap.add_argument(
    "-u",
    "--size-unit",
    type = str,
    default = "B",
    help = "Авто-формат размеров (игнорирует -u)",
    choices = Report._SUK_DICT,
)
ap.add_argument(
    "-h",
    "--human-readable",
    action = "store_true",
    help = "Единица измерения размеров",
)
ap.add_argument(
    "-c",
    "--without-color",
    action = 'store_true',
    help = "Выключить цвета",
)

ARGS = ap.parse_args()


if __name__ == "__main__":
    if ARGS.help:
        ap.print_help()
        exit(0)
    logging.disable()
    Report._READABLE_SIZE = ARGS.human_readable
    Report._SIZE_UNIT = ARGS.size_unit
    Report._COLORED = not ARGS.without_color
    Monitor.run(ARGS.interval)
