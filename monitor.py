import logging
from os import get_terminal_size

from argparse import ArgumentParser
from datetime import datetime
import re
from time import sleep

from src import System, MPLC4


_APP_DESC = "Утилита для мониторинга работы ARM'а"
_CFLAG_DESC = "моно-цвет вывода"
_NFLAG_DESC = "интервал обновлений в секундах (по умолчанию 2), \
при значении 0 будет сделан только один снимок"
_UFLAG_DESC = "единица измерения размеров (по умолчанию G)"

_ap = ArgumentParser(description=_APP_DESC)
_ap.add_argument('-c', '--without-color', action='store_true', help=_CFLAG_DESC)
_ap.add_argument('-n', '--interval', type=int, default=2, help=_NFLAG_DESC)
_ap.add_argument('-u', '--size-unit', type=str, default="G", help=_UFLAG_DESC, choices=("B", "K", "M", "G"))

ARGS = _ap.parse_args()


class Report:

    _ANSI_COLORS = {
        "faint": "\x1b[2m",
        "red": "\x1b[1;31m",
        "green": "\x1b[1;32m",
        "yellow": "\x1b[1;33m",
        "blue": "\x1b[1;34m",
        "purple": "\x1b[1;35m",
        "cyan": "\x1b[1;36m",
        "_end": "\x1b[0m",
    }
    _SERVICES_STATES_COLORS = {
        "active": None,
        "inactive": "red",
        "activating": "yellow",
        "deactivating": "yellow",
        "failed": "red",
        "not-found": "red",
        "dead": "red",
    }
    _DT_FORMAT = "%d.%m.%Y %H:%M:%S"
    _SUK = 1 / 2**{"B": 0, "K": 10, "M": 20, "G": 30}[ARGS.size_unit]
    _OUT_WIDTH = 50

    @classmethod
    def _colored(cls, string: str, color: str):
        if ARGS.without_color or not color:
            return string
        return cls._ANSI_COLORS[color] + string + cls._ANSI_COLORS["_end"]

    @classmethod
    def _split_size(cls, size: int, _devide: int = 2):
        lsize = size // _devide
        rsize = size - lsize
        return lsize, rsize

    @classmethod
    def _align(cls, string: str, side: str, width: int, fill_symb: str = " ") -> str:
        if not ARGS.without_color:
            reg = r"\x1b\[[0-9;]*[mGKH]"
            width += sum(len(m) for m in re.findall(reg, string))
        return f"{string:{fill_symb}{side}{width}}"

    def __init__(self):
        self._mplc = MPLC4()
        self._err_out = self._colored("ERR", "red")

    def _format_size(self, size):
        _format = lambda s: f"{s * self._SUK:.2f}"
        _unit = ARGS.size_unit + "B" if "B" not in ARGS.size_unit else ARGS.size_unit
        if isinstance(size, (int, float)):
            out = _format(size)
        elif isinstance(size, (list, tuple, dict)):
            out = "/".join(_format(i) for i in size)
        else:
            return self._err_out
        return f"{out} {_unit}"

    def _format_usage_perc(
            self,
            percent: float,
            warning_threshold: float = 75.0,
            crytical_threshold: float = 90.0,
        ):
        try:
            if 0 <= percent <= warning_threshold:
                color = None
            elif percent <= crytical_threshold:
                color = "yellow"
            else:
                color = "red"
            return self._colored(f"{percent:.1f}%", color)
        except Exception:
            return self._err_out

    def _format_service_state(self, state: str):
        if not isinstance(state, str) or state not in self._SERVICES_STATES_COLORS:
            return self._err_out
        return self._colored(state, self._SERVICES_STATES_COLORS.get(state))

    def _format_title(self, string: str):
        return self._colored(f" {string} ", "faint")

    def __str__(self):
        width = self._split_size(self._OUT_WIDTH, 3)
        title = lambda s: self._align(s, "^", self._OUT_WIDTH, "-")
        pName = lambda s: self._align(s, "<", width[0])
        pValue = lambda s: self._align(s, ">", width[1])

        mplc = self._mplc
        project_info = mplc.project.info
        if project_info:
            project_name = project_info.name
            project_lastmod = project_info.last_modified_time.strftime(self._DT_FORMAT)
        else:
            project_name = project_lastmod = self._err_out
        services = (
            mplc.archive.service,
            mplc.service,
            System.get_service("mplc4-cleaner")
        )
        cpu_usage_perc = System.get_cpu_usage()
        mem_usage = System.get_mem_usage()
        mem_usage_perc = mem_usage.used / mem_usage.total * 100
        diskspace_usage = System.get_disk_usage()
        diskspace_usage_perc = diskspace_usage.used / diskspace_usage.total * 100
        sys_journal_size = System.get_journal_size()

        lines = (
            "",
            title(self._format_title("MPLC4 Project")),
            "",
            pName("Name") + pValue(project_name),
            pName("Last modified") + pValue(project_lastmod),
            "",
            title(self._format_title("Services")),
            "",
            *(
                pName(service.name.replace(".service", "")) + \
                pValue(self._format_service_state(service.state)) \
                for service in services
            ),
            "",
            title(self._format_title("System resources")),
            "",
            pName("CPU") + pValue(self._format_usage_perc(cpu_usage_perc)),
            pName("RAM") + pValue(self._format_usage_perc(mem_usage_perc)),
            pName("Diskspace") + pValue(self._format_usage_perc(diskspace_usage_perc)),
            "",
            title(self._format_title("Diskspace usage details")),
            "",
            pName("General") + pValue(self._format_size(diskspace_usage[1::-1])),
            pName("MPLC4 Archive") + pValue(self._format_size(mplc.archive.size)),
            pName("MPLC4 Journal") + pValue(self._format_size(mplc.journal.size)),
            pName("System Journal") + pValue(self._format_size(sys_journal_size)),
        )
        return "\n".join(lines) + "\n"


class Monitor:

    _report = Report()

    @classmethod
    def run(cls):
        if ARGS.interval <= 0:
            print(cls._report)
        else:
            every = f"Every {ARGS.interval} sec.."
            while True:
                try:
                    width = Report._split_size(Report._OUT_WIDTH)
                    dt_now = datetime.now().strftime(Report._DT_FORMAT)
                    out = \
                        Report._align(every, "<", width[0]) + \
                        Report._align(dt_now, ">", width[1]) + \
                        f"\n{cls._report}"
                    print("\033c" + out)
                    sleep(ARGS.interval)
                except KeyboardInterrupt:
                    print("\n")
                    break
        System.exit(0)


if __name__ == "__main__":
    Monitor.run()
