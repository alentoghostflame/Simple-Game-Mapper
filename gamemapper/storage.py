from typing import List
import pathlib
import yaml


class BaseConfig:
    @classmethod
    def __init_subclass__(cls, name: str = "default_config_name", **kwargs):
        super().__init_subclass__(**kwargs)
        cls._config_name = name
        cls._from_disk = False

    def _to_dict(self) -> dict:
        output_dict = dict()
        for key in self.__dict__:
            if key[0] != "_":
                output_dict[key] = self.__dict__[key]
        return output_dict

    def save(self):
        file_name = f"{self._config_name}.yaml"
        file = open(file_name, "w")
        yaml.safe_dump(self._to_dict(), file)
        file.close()

    def _from_dict(self, state: dict):
        for key in state:
            if key in self.__dict__:
                self.__dict__[key] = state[key]

    def load(self):
        file_name = f"{self._config_name}.yaml"
        if pathlib.Path(file_name).is_file():
            file = open(file_name, "r")
            state = yaml.safe_load(file)
            file.close()
            self._from_dict(state)
            self._from_disk = True

    def from_disk(self) -> bool:
        return self._from_disk


class RamData:
    def __init__(self):
        self.tiles: List[TileData] = []


class ConfigData(BaseConfig, name="map_config"):
    def __init__(self):
        self.default_x_start: int = -1
        self.default_x_end: int = 1
        self.default_y_start: int = -2
        self.default_y_end: int = 2


class TileData:
    def __init__(self, x: int, y: int, enabled=False):
        self.x: int = x
        self.y: int = y
        self.enabled: bool = enabled
