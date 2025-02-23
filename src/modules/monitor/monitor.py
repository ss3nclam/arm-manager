from datetime import datetime
from time import sleep

from ..system import System
from .report import Report


class Monitor:

    _report = Report()

    @classmethod
    def run(cls, interval: int):
        if interval <= 0:
            print(cls._report)
        else:
            every = f"Every {interval} sec.."
            while True:
                try:
                    width = Report._split_size(Report._OUT_WIDTH)
                    dt_now = datetime.now().strftime(Report._DT_FORMAT)
                    out = \
                        Report._align(every, "<", width[0]) + \
                        Report._align(dt_now, ">", width[1]) + \
                        f"\n{cls._report}"
                    print("\033c" + out)
                    sleep(interval)
                except KeyboardInterrupt:
                    print("\n")
                    break
        System.exit(0)
