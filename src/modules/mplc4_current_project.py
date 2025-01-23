import json


class MPLC4CurrentProject:

    def __init__(self):
        self._config = self._read_config()
        if self._config:
            self._name = self._config["ProjectName"]
        else:
            self._name = (None, None)

    def _read_config(self):
        try:
            with open("/opt/mplc4/cfg/ProjInfo.json", "r") as file:
                return json.load(file)
        except Exception as err:
            return

    @property
    def info(self) -> tuple:
        return (self._name)
