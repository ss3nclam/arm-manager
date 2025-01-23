import argparse as ap
from src.config import _SIZE_UNITS_K
from src.modules.system import System

_APP_DN = "Приложение для мониторинга работы ARM'а"
_APP_EPILOG = ""
_COLOR_FLAG_DN = "цветовая индикация пороговых значений"
_INTERVAL_FLAG_DN = "интервал опроса, сек."
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
    '-n',
    '--interval',
    type = int,
    default = 1,
    help = _INTERVAL_FLAG_DN,
)
_ap.add_argument(
    '-u',
    '--size-unit',
    type = str,
    default = "GB",
    help = _UNIT_FLAG_DN,
    choices = _SIZE_UNITS_K,
)
_ap.add_argument(
    '-w',
    '--width',
    type = int,
    default = 40,
    help = _WIDTH_FLAG_DN,
)
args = _ap.parse_args()

if __name__ == "__main__":
    print(args)
