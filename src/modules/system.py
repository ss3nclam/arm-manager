import logging
import subprocess
import time


class System:

    _logs_owner: str = __qualname__

    @classmethod
    def run_cmd(cls, command: str):
        return subprocess.run(
            args = command,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
            shell = True,
            text = True
            )

    @classmethod
    def _get_cpu_time(cls):
        with open("/proc/stat", "r") as file:
            line = file.readline()
            parts = line.split()
            idle_time = int(parts[4])
            total_time = sum(map(int, parts[1:8]))
        return idle_time, total_time

    @classmethod
    def get_cpu_usage(cls, interval: float = 0.1):
        try:
            if not isinstance(interval, (int, float)):
                raise TypeError("задан некорректный тип интервала")
            else:
                if interval <= 0:
                    raise ValueError("интервал для расчётов загрузки ЦП не может быть <= 0")
                elif interval > 1:
                    raise ValueError("слишком большой интервал для расчётов загрузки ЦП")
            idle, total = cls._get_cpu_time()
            time.sleep(interval)
            idle2, total2 = cls._get_cpu_time()
            cpu_usage = (1 - (idle2 - idle) / (total2 - total)) * 100
            return cpu_usage
        except Exception as err:
            msg = "не удалось получить данные об использовании носителя"
            logging.error(f'{System._logs_owner}: {msg}: {err}')
            return

    @classmethod
    def get_ram_usage(cls):
        try:
            with open("/proc/meminfo", "r") as file:
                lines = file.readlines()
            mem_total = int(lines[0].split()[1])
            mem_free = int(lines[1].split()[1])
            buff_cache = int(lines[3].split()[1]) + int(lines[4].split()[1])
            mem_used = mem_total - mem_free - buff_cache
            memory_used_percent = (mem_used / mem_total) * 100
            return memory_used_percent
        except Exception as err:
            msg = "не удалось получить данные об использовании оперативной памяти"
            logging.error(f'{System._logs_owner}: {msg}: {err}')
            return

    @classmethod
    def get_diskspace_usage(cls, detail: bool = False):
        _format = lambda param: f"{param / 1024:.2f}"
        cmd = r"sudo df -B1 /boot | awk '{print $3,$2}' | grep -E '^[^А-Яа-я]+$'"
        try:
            shell = System.run_cmd(cmd)
            if not shell.stdout or shell.stderr:
                raise SystemError(
                    f"ошибка выполнения команды {cmd!r}: " + shell.stderr.strip()
                )
            _int = lambda raw: int(raw.rstrip("%"))
            used, total = \
                map(_int, shell.stdout.split())
            usage_percent = used / total * 100
            if not detail:
                return round(usage_percent, 2)
            else:
                return total, used, round(usage_percent, 2)
        except Exception as err:
            msg = "не удалось получить данные об использовании носителя"
            logging.error(f'{System._logs_owner}: {msg}: {err}')
            return

    @classmethod
    def get_dir_size(cls, filepath: str):
        try:
            cmd = f"sudo du -sh -B1 {filepath} " + r"| awk '{print $1}'"
            shell = System.run_cmd(cmd)
            if not shell.stdout or shell.stderr:
                raise SystemError(
                    f"ошибка выполнения команды {cmd!r}: " + shell.stderr.strip()
                )
            value = shell.stdout.strip()
            return int(value)
        except Exception as err:
            msg = "не удалось получить данные о размере директории"
            logging.error(f'{System._logs_owner}: {msg}: {err}')
            return
