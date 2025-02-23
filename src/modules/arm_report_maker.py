class ArmReportMaker:

    table_width: int = 40
    dir_size_unit: str = "GB"
    title_color: str = "default"
    colored_all: bool = True
    colored_percent_usage: bool = True
    colored_service_state: bool = True

    _K_UNITS = {
        "B": 0,
        "KB": 1,
        "MB": 2,
        "GB": 3,
    }
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
    _ERR = [
        "неизвестное состояние службы",
        "передан некорректный тип процента использования",
        "передан некорректный тип порогов индикации",
        "значение порога индикации может быть только в пределах 0-100",
        "предупредительный порог индикации не может быть больше критического",
        "ошибка вычисления размера каталога",
    ]

    @classmethod
    def _colored(cls, string: str, color: str) -> str:
        if not cls.colored_all:
            color = "default"
        if color == "default":
            return string
        return cls._ANSI_COLORS[color] + f"{string!s}" + cls._ANSI_COLORS["end"]

    @classmethod
    def _format_err(cls) -> str:
        return cls._colored("ERR", "red")

    @classmethod
    def _format_service_state(cls, state: str) -> str:
        try:
            if state not in cls._SERVICES_STATES_COLORS:
                raise ValueError(cls._ERR[0])
            color = "default" \
                if not cls.colored_service_state \
                else cls._SERVICES_STATES_COLORS[state]
            return cls._colored(state, color)
        except Exception as err:
            return cls._format_err()

    @classmethod
    def _format_percent_usage(
            cls, percent_usage, warning_threshold: int = 80, crytical_threshold: int = 90
        ) -> str:
        try:
            if not isinstance(percent_usage, (int, float)):
                raise TypeError(cls._ERR[1])
            elif not (
                isinstance(warning_threshold, int) and \
                isinstance(warning_threshold, int)
            ):
                raise TypeError(cls._ERR[2])
            elif not (
                (warning_threshold in range(101)) or (warning_threshold in range(101))
            ):
                raise ValueError(cls._ERR[3])
            elif crytical_threshold < warning_threshold:
                raise AttributeError(cls._ERR[4])
            else:
                color = "default"
                if cls.colored_percent_usage:
                    if 0 <= percent_usage <= warning_threshold:
                        pass
                    elif percent_usage <= crytical_threshold:
                        color = "yellow"
                    else:
                        color = "red"
                return cls._colored(f"{percent_usage:.1f}%", color)
        except (ValueError, TypeError, AttributeError) as err:
            return cls._format_err()

    @classmethod
    def _format_dir_size(cls, value: int):
        try:
            if value is None:
                raise ValueError(cls._ERR[5])
            else:
                _round_value = lambda x: f"{x / 1024**cls._K_UNITS[cls.dir_size_unit]:.2f}"
                suffix = " " + cls.dir_size_unit
                if isinstance(value, int):
                    return _round_value(value) + suffix
                if isinstance(value, (tuple, list)):
                    return "/".join(f"{_round_value(v)}" for v in value) + suffix
        except ValueError as err:
            return cls._format_err()

    @classmethod
    def _make_table(cls, lines: tuple, width: int) -> str:
        _fcolsize = width // 2
        _scolsize = width - _fcolsize
        _len_ansi = lambda s: 0 if not "\033[" in f"{s!s}" else 11
        _title = lambda s: f" {s} ".center(_fcolsize + _scolsize + _len_ansi(s), "-")
        _col1 = lambda s: s.ljust(_fcolsize + _len_ansi(s))
        _col2 = lambda s: s.rjust(_scolsize + _len_ansi(s))
        out_lines = []
        for line in lines:
            if isinstance(line, (tuple, list)):
                out_lines.append(_col1(line[0]) + _col2(line[1]))
            elif isinstance(line, str):
                if line != "":
                    out_lines.append(_title(cls._colored(line, cls.title_color)))
                else:
                    out_lines.append(line)
        out = "\n".join(out_lines)
        return out

    @classmethod
    def make_report(
            cls,
            *,
            services_states: tuple,
            cpu_usage: float,
            ram_usage: float,
            disk_usage_detail: tuple,
            psql_size: int,
            mplc4_log_size: int,
            sys_log_size: int,
            mplc4_project_info: tuple,
            host: str
        ) -> str:
        lines = (
            "Main",
            ("Host", host),
            ("Project", mplc4_project_info),
            "",
            "Services",
            *((name, cls._format_service_state(state)) for name, state in services_states),
            "",
            "System",
            ("CPU", cls._format_percent_usage(cpu_usage)),
            ("RAM", cls._format_percent_usage(ram_usage)),
            ("Diskspace", cls._format_percent_usage(disk_usage_detail[2])),
            ("Diskspace (detail)", cls._format_dir_size(disk_usage_detail[:2][::-1])),
            "",
            "Directories",
            ("PSQL", cls._format_dir_size(psql_size)),
            ("MPLC4 log", cls._format_dir_size(mplc4_log_size)),
            ("System log", cls._format_dir_size(sys_log_size)),
        )
        out = cls._make_table(lines, cls.table_width)
        return out
