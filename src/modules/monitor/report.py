import re

from ..system import System
from ..mplc4 import MPLC4


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
    _READABLE_SIZE = False
    _SIZE_UNIT = "B"
    _SUK_DICT = {"B": 0, "K": 10, "M": 20, "G": 30, "T": 40, "P": 50}
    _COLORED = True
    _OUT_WIDTH = 50

    @classmethod
    def _colored(cls, string: str, color: str):
        if not cls._COLORED or not color:
            return string
        return cls._ANSI_COLORS[color] + string + cls._ANSI_COLORS["_end"]

    @classmethod
    def _split_size(cls, size: int, _devide: int = 2):
        lsize = size // _devide
        rsize = size - lsize
        return lsize, rsize

    @classmethod
    def _align(cls, string: str, side: str, width: int, fill_symb: str = " ") -> str:
        if cls._COLORED:
            reg = r"\x1b\[[0-9;]*[mGKH]"
            width += sum(len(m) for m in re.findall(reg, string))
        return f"{string:{fill_symb}{side}{width}}"

    @classmethod
    def _human_readable_size(cls, size_in_bytes):
        for unit in cls._SUK_DICT:
            if size_in_bytes < 1024:
                break
            size_in_bytes /= 1024
        return f"{size_in_bytes:.2f}{unit}"

    @classmethod
    def _format_size(cls, size):
        if cls._READABLE_SIZE:
            _format = cls._human_readable_size
        else:
            suk = 1 / 2**cls._SUK_DICT[cls._SIZE_UNIT]
            _format = lambda s: f"{s * suk:.2f}{cls._SIZE_UNIT}"
        if isinstance(size, (int, float)):
            out = _format(size)
        elif isinstance(size, (list, tuple, dict)):
            out = "/".join(_format(i) for i in size)
        else:
            return cls._err_out
        return out.replace(".00B", "")

    @classmethod
    def _format_usage_perc(
            cls,
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
            return cls._colored(f"{percent:.1f}%", color)
        except Exception:
            return cls._err_out

    @classmethod
    def _format_service_state(cls, state: str):
        if not isinstance(state, str) or state not in cls._SERVICES_STATES_COLORS:
            return cls._err_out
        return cls._colored(state, cls._SERVICES_STATES_COLORS.get(state))

    @classmethod
    def _format_title(cls, string: str):
        return cls._colored(f" {string} ", "faint")

    def __init__(self):
        self._mplc = MPLC4()
        self._err_out = self._colored("ERR", "red")

    def __str__(self):
        width = self._split_size(self._OUT_WIDTH, 3)
        title = lambda s: self._align(s, "^", self._OUT_WIDTH, "-")
        pName = lambda s: self._align(s, "<", width[0])
        pValue = lambda s: self._align(s, ">", width[1])

        def format(type: str, input):
            return {
                "title": self._format_title,
                "service_state": self._format_service_state,
                "usage": self._format_usage_perc,
                "size": self._format_size,
            }[type](input)

        mplc = self._mplc
        project_info = mplc.project.info
        if project_info:
            project_name = project_info.name
            project_lastmod = project_info.last_modified_time.strftime(self._DT_FORMAT)
        else:
            project_name = project_lastmod = self._colored("None", "red")
        services = (
            mplc.archive.service,
            mplc.service,
            System.get_service("arm-cleaner")
        )
        cpu_usage_perc = System.get_cpu_usage()
        mem_usage = System.get_mem_usage()
        mem_usage_perc = mem_usage.used / mem_usage.total * 100
        diskspace_usage = System.get_disk_usage()
        diskspace_usage_perc = diskspace_usage.used / diskspace_usage.total * 100
        sys_journal_size = System.get_journal_size()

        lines = (
            "",
            title(format("title", "MPLC4 Project")),
            "",
            pName("Name") + pValue(project_name),
            pName("Last modified") + pValue(project_lastmod),
            "",
            title(format("title", "Services")),
            "",
            *(
                pName(service.name.replace(".service", "")) + \
                pValue(format("service_state", service.state)) \
                for service in services
            ),
            "",
            title(format("title", "System resources")),
            "",
            pName("CPU") + pValue(format("usage", cpu_usage_perc)),
            pName("RAM") + pValue(format("usage", mem_usage_perc)),
            pName("Diskspace") + pValue(format("usage", diskspace_usage_perc)),
            "",
            title(format("title", "Diskspace usage details")),
            "",
            pName("General") + pValue(format("size", diskspace_usage[1::-1])),
            pName("MPLC4 Archive") + pValue(format("size", mplc.archive.size)),
            pName("MPLC4 Journal") + pValue(format("size", mplc.journal.size)),
            pName("System Journal") + pValue(format("size", sys_journal_size)),
        )
        return "\n".join(lines) + "\n"
