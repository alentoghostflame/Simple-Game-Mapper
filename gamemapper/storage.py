from typing import List
import pathlib
import yaml
try:
    from yaml import CSafeLoader as SafeLoader, CSafeDumper as SafeDumper
except ImportError:
    from yaml import SafeLoader, SafeDumper
import os


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
    def __init__(self, x: int = 0, y: int = 0, enabled: bool = False, state: dict = None):
        self.x: int = x
        self.y: int = y
        self.enabled: bool = enabled

        if state:
            self.from_dict(state)

    def from_dict(self, state: dict):
        self.x = state["x"]
        self.y = state["y"]
        self.enabled = state["enabled"]

    def to_dict(self) -> dict:
        return {"x": self.x, "y": self.y, "enabled": self.enabled}


class MapSaveData:
    def __init__(self, state: dict = None):
        self.tiles: List[TileData] = []
        self.x_start: int = 0
        self.x_end: int = 0
        self.y_start: int = 0
        self.y_end: int = 0

        if state:
            self.from_dict(state)

    def verify_state(self, state: dict) -> bool:
        try:
            assert isinstance(state.get("tiles", None), list)
            assert isinstance(state.get("x_start", None), int)
            assert isinstance(state.get("x_end", None), int)
            assert isinstance(state.get("y_start", None), int)
            assert isinstance(state.get("y_end", None), int)
            return True
        except AssertionError:
            return False

    def from_dict(self, state: dict) -> bool:
        if self.verify_state(state):
            for raw_tile_data in state["tiles"]:
                self.tiles.append(TileData(state=raw_tile_data))
            self.x_start = state["x_start"]
            self.x_end = state["x_end"]
            self.y_start = state["y_start"]
            self.y_end = state["y_end"]
            return True
        else:
            return False

    def to_dict(self) -> dict:
        output_dict = {"x_start": self.x_start, "x_end": self.x_end, "y_start": self.y_start, "y_end": self.y_end}

        raw_tile_list = []
        for tile in self.tiles:
            raw_tile_list.append(tile.to_dict())
        output_dict["tiles"] = raw_tile_list

        return output_dict


class SaveManager:
    def __init__(self, ram_data: RamData):
        self._ram_data = ram_data
        self._saves: List[pathlib.Path] = []

    def save_from_ram(self, file_path: str):
        map_save_data = MapSaveData()
        for tile in self._ram_data.tiles:
            if tile.enabled:
                map_save_data.tiles.append(tile)
                if tile.x < map_save_data.x_start:
                    map_save_data.x_start = tile.x
                elif tile.x > map_save_data.x_end:
                    map_save_data.x_end = tile.x
                if tile.y < map_save_data.y_start:
                    map_save_data.y_start = tile.y
                elif tile.y > map_save_data.y_end:
                    map_save_data.y_end = tile.y

        file = open(file_path, "w")
        yaml.dump(map_save_data.to_dict(), file, Dumper=SafeDumper)

    def load(self):
        self.scan_for_saves()

    def scan_for_saves(self):
        save_path = pathlib.Path("saves")
        save_path.mkdir(exist_ok=True)
        for file in save_path.iterdir():
            if file.is_file():
                self._saves.append(file)
