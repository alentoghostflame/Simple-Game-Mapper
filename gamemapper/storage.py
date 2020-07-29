from typing import List, Dict, Set, Iterable
import pathlib
import yaml
try:
    from yaml import CSafeLoader as SafeLoader, CSafeDumper as SafeDumper
except ImportError:
    from yaml import SafeLoader, SafeDumper


# Name of the dummy texture.
EMPTY_TEXTURE = "Empty"


# CSS that textured map tiles will have.
BASE_TEXTURE_CSS = """
.{} {{ 
     background-color: @unfocused_borders;
     background-image: url("{}");
     background-repeat: no-repeat;
     background-size: cover;
     background-position: center;
     {}
}}
"""


class BaseConfig:
    @classmethod
    def __init_subclass__(cls, *args, name: str = "default_config_name", **kwargs):
        """
        Shortcut to make a config file that can easily save to disk via PyYAML. Not intended to be used standalone,
        meant to be subclassed. Will probably error if not subclassed.

        :param args: Positional arguments to hand to the subclass.
        :param name: String name of the config on disk, without the file extension. You could also put the path here.
        :param kwargs: Keyword arguments to hand to the subclass.
        :return:
        """
        super().__init_subclass__(*args, **kwargs)
        cls._config_name = name
        cls._from_disk = False

    def _to_dict(self) -> dict:
        """
        Turns all class variables that don't start with an underscore into a dictionary.
        :return:
        """
        output_dict = dict()
        for key in self.__dict__:
            if key[0] != "_":
                output_dict[key] = self.__dict__[key]
        return output_dict

    def save(self):
        """
        Saves the config to disk.
        :return:
        """
        file_name = f"{self._config_name}.yaml"
        file = open(file_name, "w")
        yaml.safe_dump(self._to_dict(), file)
        file.close()

    def _from_dict(self, state: dict):
        """
        Takes keys from a dictionary and applies them to the class variables when possible.

        :param state: Dictionary object to get class variable values from.
        :return:
        """
        for key in state:
            if key in self.__dict__:
                self.__dict__[key] = state[key]

    def load(self):
        """
        Loads the file from disk.
        :return:
        """
        file_name = f"{self._config_name}.yaml"
        if pathlib.Path(file_name).is_file():
            file = open(file_name, "r")
            state = yaml.safe_load(file)
            file.close()
            self._from_dict(state)
            # noinspection PyAttributeOutsideInit
            self._from_disk = True

    def from_disk(self) -> bool:
        """
        :return: True if loaded successfully from disk, False otherwise.
        """
        return self._from_disk


class RamData:
    def __init__(self):
        """
        Holds data that will be used across the mapper, but not necessarily saved to disk.
        """
        self.tiles: List[TileData] = list()
        self.symbols: Dict[str, SymbolData] = dict()
        self.textures: Dict[str, TextureData] = dict()
        self.x_start: int = 0
        self.x_end: int = 0
        self.y_start: int = 0
        self.y_end: int = 0

        self.save_tile_reference: Dict[str] = dict()
        self.held_buttons: Set[str] = set()
        self.selected_texture: str = EMPTY_TEXTURE

        self.last_save_folder: str = ""
        self.last_save_name: str = ""


class ConfigData(BaseConfig, name="map_config"):
    def __init__(self):
        """
        Config file, meant to be read-only by the program.
        """
        self.default_x_start: int = -1
        self.default_x_end: int = 1
        self.default_y_start: int = -2
        self.default_y_end: int = 2

        self.square_size: int = 50


class TileData:
    def __init__(self, x: int = 0, y: int = 0, enabled: bool = False, state: dict = None):
        """
        Manages data related to a specific map tile.

        :param x: Integer X coordinate of tile.
        :param y: Integer Y coordinate of tile.
        :param enabled: Boolean True if the tile is enabled, False otherwise.
        :param state: Dictionary object to load data from.
        """
        self.x: int = x
        self.y: int = y
        self.tags: Set[str] = set()
        self.enabled: bool = enabled
        self.texture: str = ""

        if state:
            self.from_dict(state)

    def apply_letter_tags(self, tags: Iterable):
        """
        Iterates over the given tags, adding tags and removing ones that it already has.

        :param tags: Iterable object to get tags from.
        :return:
        """
        for tag in tags:
            if tag in self.tags:
                self.tags.remove(tag)
            else:
                self.tags.add(tag)

    def from_dict(self, state: dict):
        """
        Takes keys from a dictionary and applies them to the class variables when possible.

        :param state: Dictionary object to get class variable values from.
        :return:
        """
        self.x = state.get("x", 0)
        self.y = state.get("y", 0)
        self.enabled = state.get("enabled", True)
        self.tags = state.get("tags", set())
        self.texture = state.get("texture", "")

    def to_dict(self) -> dict:
        """
        Outputs certain class variables as a dictionary.
        :return:
        """
        return {"x": self.x, "y": self.y, "enabled": self.enabled, "tags": self.tags, "texture": self.texture}


class SymbolData:
    def __init__(self, character: str = "a", state: dict = None):
        """
        Manages data related to a specific symbol.

        :param character: String character that this SymbolData will represent.
        :param state: Dictionary object to load values from.
        """
        self.character: str = character
        self.default_value: str = ""
        self._get_value_func = None

        if state:
            self.from_dict(state)

    def to_dict(self) -> dict:
        """
        Outputs certain class variable(s) as a dictionary.


        :return: Dictionary object with specific class variables in it.
        """
        return {"value": self.get_value()}

    def from_dict(self, state: dict):
        """
        Takes keys from a dictionary and applies them to the class variables when possible.

        :param state: Dictionary object to get class variable values from.
        :return:
        """
        self.default_value = state["value"]

    def register_get_func(self, function):
        """
        Saves a function that will be used for get_value.

        :param function: Function/method that gets the value of the SymbolWidget that this represents.
        :return:
        """
        self._get_value_func = function

    def get_value(self) -> str:
        """
        Gets the currently value, meant to be used to get SymbolWidget's entry value.
        :return:
        """
        return self._get_value_func()


class TextureData:
    def __init__(self, name: str, image_path: str, extra_css: str = ""):
        """
        Collection of data about a texture.

        :param name: String short name of the texture.
        :param image_path: String path to the image file on disk.
        :param extra_css: String extra CSS to add to the saved css.
        """
        self.name: str = name
        self.class_name: str = f"texture_{self.name.replace(' ', '')}"
        self.path: str = image_path
        self.css: str = BASE_TEXTURE_CSS.format(self.class_name, self.path, extra_css)


class MapSaveData:
    def __init__(self, state: dict = None):
        """
        A collection of variables used to load data to RamData.

        :param state: Dictionary object to load values from.
        """
        self.tiles: List[TileData] = list()
        self.x_start: int = 0
        self.x_end: int = 0
        self.y_start: int = 0
        self.y_end: int = 0
        self.symbols: Dict[str, SymbolData] = dict()

        if state:
            self.from_dict(state)

    def from_dict(self, state: dict) -> bool:
        """
        Takes keys from a dictionary and applies them to the class variables when possible.

        :param state: Dictionary object to get class variable values from.

        :return: Boolean True when state verification passes, False otherwise.
        """
        if verify_save_state(state):
            for raw_tile_data in state.get("tiles", list()):
                self.tiles.append(TileData(state=raw_tile_data))
            self.x_start = state.get("x_start", 0)
            self.x_end = state.get("x_end", 0)
            self.y_start = state.get("y_start", 0)
            self.y_end = state.get("y_end", 0)
            for symbol_char in state.get("symbols", dict()):
                self.symbols[symbol_char] = SymbolData(symbol_char, state=state["symbols"][symbol_char])
            return True
        else:
            print("FAILING VERIFICATION")
            return False

    def to_dict(self) -> dict:
        """
        Outputs certain class variables as a dictionary, and processes certain data types to make them easily usable
        with PyYAML.

        :return: Dictionary object with specific class variables in it.
        """
        output_dict = {"x_start": self.x_start, "x_end": self.x_end, "y_start": self.y_start, "y_end": self.y_end}

        raw_tile_list = list()
        for tile in self.tiles:
            raw_tile_list.append(tile.to_dict())
        output_dict["tiles"] = raw_tile_list

        raw_symbol_dict = dict()
        for symbol_char in self.symbols:
            raw_symbol_dict[symbol_char] = self.symbols[symbol_char].to_dict()
        output_dict["symbols"] = raw_symbol_dict

        return output_dict


def verify_save_state(state: dict) -> bool:
    """
    Verifies a save, making sure that if the data types exist, they are the type of data expected. Missing data will
    pass this check.

    :param state: Dictionary object corresponding to a mapper save file to verify.

    :return: Boolean True if all checks get passed, False if at least one fails.
    """
    try:
        assert isinstance(state.get("tiles", list()), list)
        assert isinstance(state.get("symbols", dict()), dict)
        assert isinstance(state.get("x_start", 0), int)
        assert isinstance(state.get("x_end", 0), int)
        assert isinstance(state.get("y_start", 0), int)
        assert isinstance(state.get("y_end", 0), int)
        assert state.get("x_start", 0) <= state.get("x_end", 0)
        assert state.get("y_start", 0) <= state.get("y_end", 0)
        return True
    except AssertionError:
        return False


class SaveManager:
    def __init__(self, ram_data: RamData):
        """
        Creates saves from and loads saves to the given RamData.

        :param ram_data: RamData object to read and write to.
        """
        self._ram_data = ram_data

    def ram_to_disk(self, file_path: str):
        """
        Turns data in RamData into a save file.

        :param file_path: String path to disk where to put the save file.
        :return:
        """
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

        for symbol_char in self._ram_data.symbols:
            symbol_data = self._ram_data.symbols[symbol_char]
            if symbol_data.get_value():
                map_save_data.symbols[symbol_char] = symbol_data

        file = open(file_path, "w")
        yaml.dump(map_save_data.to_dict(), file, Dumper=SafeDumper)

    def disk_to_ram(self, file_path: str):
        """
        Loads data from disk into RamData.

        :param file_path: String path to disk where to load the save file from.
        :return:
        """
        file = open(file_path, "r")
        raw_map_save_data = yaml.load(file, Loader=SafeLoader)
        map_save_data = MapSaveData(state=raw_map_save_data)

        self._ram_data.tiles = map_save_data.tiles
        self._ram_data.x_start = map_save_data.x_start
        self._ram_data.x_end = map_save_data.x_end
        self._ram_data.y_start = map_save_data.y_start
        self._ram_data.y_end = map_save_data.y_end
        self._ram_data.symbols = map_save_data.symbols

        self._ram_data.save_tile_reference.clear()
        for i in range(len(self._ram_data.tiles)):
            tile = self._ram_data.tiles[i]
            self._ram_data.save_tile_reference[f"{tile.x}:{tile.y}"] = i
