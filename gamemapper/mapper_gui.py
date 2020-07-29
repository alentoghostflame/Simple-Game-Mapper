from gamemapper.storage import ConfigData, RamData, TileData, SaveManager, SymbolData, TextureData, EMPTY_TEXTURE
import pathlib
import string
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf


class TextureManager:
    def __init__(self, config: ConfigData, ram_data: RamData):
        """
        Loads and manages TextureData objects in the given RamData object.

        :param config: ConfigData object to read from.
        :param ram_data: RamData object to read from and write to.
        """
        self._config = config
        self._ram_data = ram_data
        self._css_provider = Gtk.CssProvider()

    def load(self):
        """
        Loads all textures from the textures folder into RAM.
        :return:
        """
        # noinspection PyArgumentList
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), self._css_provider,
                                                 Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self._initialize_empty_background()
        texture_path = pathlib.Path("textures")
        texture_path.mkdir(exist_ok=True)
        for file in texture_path.iterdir():
            if file.is_file():
                self._process_file(file)

        css_string = ""
        for texture_name in self._ram_data.textures:
            css_string += f"\n{self._ram_data.textures[texture_name].css}"

        self._css_provider.load_from_data(css_string.encode("utf_8"))

    def _initialize_empty_background(self):
        """
        Creates the empty texture class.
        :return:
        """
        empty_texture = TextureData(EMPTY_TEXTURE, EMPTY_TEXTURE.lower())
        empty_texture.css = f".{empty_texture.class_name} {{ }}"
        self._ram_data.textures[empty_texture.name] = empty_texture

    def _process_file(self, file: pathlib.Path):
        """
        Turns an image path into a TextureData object that's loaded into RAM.

        :param file: pathlib.Path object that leads to an image.
        :return:
        """
        texture_data = TextureData(file.stem, str(file.absolute()))
        self._ram_data.textures[texture_data.name] = texture_data

    def set_texture(self, widget: Gtk.Widget, texture_name: str) -> bool:
        """
        Clears existing CSS texture class(es) from the given Gtk.Widget and gives it the CSS texture class that
        corresponds with the given background name, if it exists.

        :param widget: Gtk.Widget object to change the background of.
        :param texture_name: String name of the texture to apply.

        :return: Boolean True if a corresponding class was found and applied, False otherwise.
        """
        button_style: Gtk.StyleContext = widget.get_style_context()
        for class_name in button_style.list_classes():
            if class_name.startswith("texture_"):
                button_style.remove_class(class_name)
        texture_data = self._ram_data.textures.get(texture_name, None)
        if texture_data:
            widget.get_style_context().add_class(texture_data.class_name)
            widget.show()
            return True
        else:
            return False


class SimpleGameMapperGUI:
    def __init__(self, config: ConfigData, ram_data: RamData, saves: SaveManager, textures: TextureManager):
        """
        Main GTK GUI object for the simple game mapper, controlling the Gtk.Window object. Manages the top-most events.

        :param config: ConfigData object to read from.
        :param ram_data: RamData object to read from and write to.
        :param saves: SaveManager object to use.
        :param textures: TextureManager object to use.
        """
        self._config: ConfigData = config
        self._ram_data: RamData = ram_data
        self._saves: SaveManager = saves
        self._textures: TextureManager = textures

        self._window = Gtk.Window()
        self._css_provider = Gtk.CssProvider()
        self._main_layout = MainLayout(self._config, self._ram_data, self._saves, self._textures)

    def setup(self):
        """
        Shortcut to run all setup functions.
        :return:
        """
        self.setup_window()
        self.setup_css()
        self.setup_main_layout()

    def setup_window(self):
        """
        Sets up the main Gtk.Window object.
        :return:
        """
        self._window.connect("delete-event", self._quit_program)
        self._window.connect("destroy", Gtk.main_quit)
        self._window.set_default_size(800, 400)

    def setup_css(self):
        """
        Loads the static CSS file.
        :return:
        """
        self._css_provider.load_from_path("gamemapper/simple_map.css")
        # noinspection PyArgumentList
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), self._css_provider,
                                                 Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def setup_main_layout(self):
        """
        Sets up the MainLayout object.
        :return:
        """
        self._window.add(self._main_layout.grid)
        self._main_layout.setup()

    def run(self):
        """
        Has all GTK GUI objects in the application display and starts the blocking Gtk graphical loop.
        :return:
        """
        self._window.show_all()
        Gtk.main()

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def _quit_program(self, window: Gtk.Window = None, event: Gdk.Event = None):
        """
        Intercepts the quit command with a prompt asking the user if they want to quit for sure. If Yes is selected,
        Gtk.main_quit() is called and the window is closed. If No is selected, the mapper continues.

        :param window: Gtk.Window object, ignored.
        :param event: Gdk.Event object, ignored.

        :return: False if the user selects No, True otherwise to destroy the window.
        """
        return_value = False
        dialog = Gtk.Dialog(Gtk.DialogFlags.MODAL, title="Quit Mapper?")
        dialog.add_button(Gtk.STOCK_YES, Gtk.ResponseType.OK)
        dialog.add_button(Gtk.STOCK_NO, Gtk.ResponseType.CANCEL)

        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            Gtk.main_quit()
        else:
            return_value = True
        dialog.destroy()

        return return_value


class MainLayout:
    def __init__(self, config: ConfigData, ram_data: RamData, saves: SaveManager, textures: TextureManager):
        """
        Manages the main grid that holds the biggest containers and has them work together.

        :param config: ConfigData object to read from.
        :param ram_data: RamData object to read from and write to.
        :param saves: SaveManager object to use.
        :param textures: TextureManager object to use.
        """
        self._config: ConfigData = config
        self._ram_data: RamData = ram_data
        self._saves: SaveManager = saves
        self._textures: TextureManager = textures

        self.grid = Gtk.Grid(valign="fill", halign="fill")
        self._top_bar = TopMenuBar(self._ram_data, self._saves)
        self._map_container = MapContainer(self._config, self._ram_data, self._textures)
        self._side_bar = OptionSideBar(self._config, self._ram_data, self._textures)

    def setup(self):
        """
        Sets up the main grid and has its children run their setups as well.

        :return:
        """
        self.grid.attach(self._top_bar.toolbar, 0, 0, 1, 1)
        self.grid.attach(self._map_container.main_grid, 0, 1, 1, 1)
        self.grid.attach(self._side_bar.notebook, 1, 0, 1, 2)

        self._top_bar.set_reset_functions(self._map_container.initialize_default_grid,
                                          self._side_bar.initialize_symbols)
        self._top_bar.set_load_from_ram_functions(self._map_container.initialize_from_ram,
                                                  self._side_bar.initialize_symbols_from_ram)
        self._top_bar.setup()
        self._map_container.setup()
        self._side_bar.setup()


class TopMenuBar:
    def __init__(self, ram_data: RamData, saves: SaveManager):
        """
        Holds the top buttons, such as resetting, saving, and loading.

        :param ram_data: RamData object to read from and write to.
        :param saves: SaveManager object to use.
        """
        self._ram_data = ram_data
        self._saves = saves
        self.toolbar = Gtk.Toolbar()
        self._new_button = Gtk.ToolButton()
        self._save_button = Gtk.ToolButton()
        self._open_button = Gtk.ToolButton()

        self._map_reset_func = None
        self._symbol_reset_func = None

        self._map_load_func = None
        self._symbol_load_func = None

    def setup(self):
        """
        Sets up all the buttons on the top visually and functionally, then assigns them their spot.
        :return:
        """
        self._new_button.set_icon_name(Gtk.STOCK_NEW)
        self._new_button.set_label("New")
        self._new_button.connect("clicked", self._on_new_pressed)

        self._save_button.set_icon_name(Gtk.STOCK_SAVE)
        self._save_button.set_label("Save")
        self._save_button.connect("clicked", self._on_save_pressed)

        self._open_button.set_icon_name(Gtk.STOCK_OPEN)
        self._open_button.set_label("Load")
        self._open_button.connect("clicked", self._on_load_pressed)

        self.toolbar.insert(self._new_button, 0)
        self.toolbar.insert(self._save_button, 1)
        self.toolbar.insert(self._open_button, 2)

    def set_reset_functions(self, map_reset_func, symbol_reset_func):
        """
        Sets the functions to use when the map and symbols need to be reset.

        :param map_reset_func: Function used to reset the map.
        :param symbol_reset_func: Function used to reset the symbols.
        :return:
        """
        self._map_reset_func = map_reset_func
        self._symbol_reset_func = symbol_reset_func

    def set_load_from_ram_functions(self, map_load_func, symbol_load_func):
        """
        Sets the functions to use when the map and symbols need to be loaded from RamData.

        :param map_load_func: Function used to load the map.
        :param symbol_load_func: Function used to load the symbols.
        :return:
        """
        self._map_load_func = map_load_func
        self._symbol_load_func = symbol_load_func

    # noinspection PyUnusedLocal
    def _on_new_pressed(self, button: Gtk.ToolButton = None):
        """
        Triggers when the new button is pressed, opening a dialog to make sure that the user wants to reset. If the
        user selects Yes, the maps and symbols are reset. Otherwise, nothing happens.
        FIXME: If something errors, the dialog box will not close, requiring the application to be killed.

        :param button: Gtk.ToolButton object, ignored.
        :return:
        """
        dialog = Gtk.Dialog(Gtk.DialogFlags.MODAL, title="Reset Map?")
        dialog.add_button(Gtk.STOCK_YES, Gtk.ResponseType.OK)
        dialog.add_button(Gtk.STOCK_NO, Gtk.ResponseType.CANCEL)

        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            self._map_reset_func()
            self._symbol_reset_func()
        else:
            pass
        dialog.destroy()

    # noinspection PyUnusedLocal
    def _on_save_pressed(self, button: Gtk.ToolButton = None):
        """
        Triggers when the save button is pressed, opening a dialog asking where to save the file and what name the file
        should have. If the user selects a place to save, a save is made at that location and is recorded into RamData.
        Otherwise, nothing happens.
        FIXME: If something errors, the dialog box will not close, requiring the application to be killed.

        :param button: Gtk.ToolButton object, ignored.
        :return:
        """
        dialog = Gtk.FileChooserDialog(title="Save to...", action=Gtk.FileChooserAction.SAVE)
        dialog.set_do_overwrite_confirmation(True)
        if self._ram_data.last_save_folder:
            dialog.set_current_folder(self._ram_data.last_save_folder)
        else:
            dialog.set_current_folder("saves")
        if self._ram_data.last_save_name:
            dialog.set_current_name(self._ram_data.last_save_name)
        else:
            dialog.set_current_name("map_save.yaml")
        dialog.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        dialog.add_button(Gtk.STOCK_SAVE, Gtk.ResponseType.OK)

        self._add_filters(dialog)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            split_file_path = dialog.get_filename().split("/")
            self._ram_data.last_save_folder = "/".join(split_file_path[:-1])
            self._ram_data.last_save_name = split_file_path[-1]

            file_path = dialog.get_filename()
            self._saves.ram_to_disk(file_path)
        else:
            pass

        dialog.destroy()

    # noinspection PyUnusedLocal
    def _on_load_pressed(self, button):
        """
        Triggers when the load button is pressed, opening a dialog asking what file to load from. If the user selects
        a file to load, it will attempt to load it into RamData and have the map and symbols load from RamData.
        Otherwise, nothing happens.
        FIXME: If something errors, the dialog box will not close, requiring the application to be killed.

        :param button: Gtk.ToolButton object, ignored.
        :return:
        """
        dialog = Gtk.FileChooserDialog(title="Load from...", action=Gtk.FileChooserAction.OPEN)
        if self._ram_data.last_save_folder:
            dialog.set_current_folder(self._ram_data.last_save_folder)
        else:
            dialog.set_current_folder("saves")
        dialog.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        dialog.add_button(Gtk.STOCK_OPEN, Gtk.ResponseType.OK)

        self._add_filters(dialog)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            split_file_path = dialog.get_filename().split("/")
            self._ram_data.last_save_folder = "/".join(split_file_path[:-1])
            self._ram_data.last_save_name = split_file_path[-1]

            file_path = dialog.get_filename()
            self._saves.disk_to_ram(file_path)
            self._symbol_load_func()
            self._map_load_func()
        else:
            pass

        dialog.destroy()

    # noinspection PyMethodMayBeStatic
    def _add_filters(self, dialog: Gtk.FileChooserDialog):
        """
        Shortcut to add filter(s) to a given dialog.

        :param dialog: Gtk.FileChooserDialog object to add filter(s) to.
        :return:
        """
        yaml_filter = Gtk.FileFilter()
        yaml_filter.set_name("YAML file")
        yaml_filter.add_mime_type("text/yaml")
        dialog.add_filter(yaml_filter)


class MapContainer:
    def __init__(self, config: ConfigData, ram_data: RamData, textures: TextureManager):
        """
        Manages the map and closely related widgets.

        :param config: ConfigData object to read from.
        :param ram_data: RamData object to read from and write to.
        :param textures: TextureManager object to use.
        """
        self._config: ConfigData = config
        self._ram_data: RamData = ram_data
        self._textures: TextureManager = textures

        self.main_grid = Gtk.Grid(valign="fill", halign="fill")
        self._scrolled_map = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.AUTOMATIC,
                                                vscrollbar_policy=Gtk.PolicyType.AUTOMATIC)
        self._tile_grid = Gtk.Grid(valign="center", halign="center", row_homogeneous=True, column_homogeneous=True)

        self._top_button = Gtk.Button(label="+", hexpand=True)
        self._bottom_button = Gtk.Button(label="+", hexpand=True)
        self._left_button = Gtk.Button(label="+", vexpand=True)
        self._right_button = Gtk.Button(label="+", vexpand=True)

    def setup(self):
        """
        Shortcut to run all setup functions and initialize a basic grid.
        :return:
        """
        self.setup_buttons()
        self.setup_main_grid()
        self.initialize_default_grid()

    def setup_buttons(self):
        """
        Sets up all the buttons visually and functionally.
        :return:
        """
        self._top_button.get_style_context().add_class("map_expander_button")
        self._top_button.connect("clicked", self.add_top)
        self._bottom_button.get_style_context().add_class("map_expander_button")
        self._bottom_button.connect("clicked", self.add_bottom)
        self._left_button.get_style_context().add_class("map_expander_button")
        self._left_button.connect("clicked", self.add_left)
        self._right_button.get_style_context().add_class("map_expander_button")
        self._right_button.connect("clicked", self.add_right)

    def setup_main_grid(self):
        """
        Sets up the main grid visually and functionally and assigns the tile grid and buttons to their spot.
        :return:
        """
        self._scrolled_map.add(self._tile_grid)
        self.main_grid.attach(self._scrolled_map, 1, 1, 1, 1)
        self.main_grid.attach(self._top_button, 1, 0, 1, 1)
        self.main_grid.attach(self._bottom_button, 1, 2, 1, 1)
        self.main_grid.attach(self._left_button, 0, 1, 1, 1)
        self.main_grid.attach(self._right_button, 2, 1, 1, 1)

        self.main_grid.connect("key-press-event", self._on_keypress)
        self.main_grid.connect("key-release-event", self._on_keyrelease)

        self._tile_grid.get_style_context().add_class("map_holder")

    def initialize_default_grid(self):
        """
        Initializes the grid with the default size values in the config.
        :return:
        """
        self.initialize_grid(self._config.default_x_start, self._config.default_x_end, self._config.default_y_start,
                             self._config.default_y_end)

    def initialize_grid(self, x_start=0, x_end=0, y_start=0, y_end=0):
        """
        Clears the current layout and initializes the grid, sized with the given size values.

        :param x_start: Left-most coordinate, needs to be smaller than x_end for valid results.
        :param x_end: Right-most coordinate, needs to be bigger than x_start for valid results.
        :param y_start: Top-most coordinate, needs to be smaller than y_end for valid results.
        :param y_end: Bottom-most coordinate, needs to be bigger than y_start for valid results.
        :return:
        """
        self.clear_layout()

        self._ram_data.x_start = x_start
        self._ram_data.x_end = x_end
        self._ram_data.y_start = y_start
        self._ram_data.y_end = y_end
        for x in range(x_start, x_end + 1):
            for y in range(y_start, y_end + 1):
                self.add_tile_button(x, y)
        self._tile_grid.show_all()

    def initialize_from_ram(self):
        """
        Clears the current layout (but not RamData) and initializes the grid, with size values from RamData and fetching
        TileData from RamData when a reference is found.
        :return:
        """
        self.clear_layout(clear_ram=False)

        for x in range(self._ram_data.x_start, self._ram_data.x_end + 1):
            for y in range(self._ram_data.y_start, self._ram_data.y_end + 1):
                if f"{x}:{y}" in self._ram_data.save_tile_reference:
                    save_tile_index = self._ram_data.save_tile_reference[f"{x}:{y}"]
                    self.add_tile_button(x, y, self._ram_data.tiles[save_tile_index])
                else:
                    self.add_tile_button(x, y)

        self._tile_grid.show_all()

    def clear_layout(self, clear_ram=True):
        """
        Shortcut to destroy all children of the tile_grid object and optionally clear the tile RamData.

        :param clear_ram: Boolean True to clear the tile RamData, False to not.
        :return:
        """
        if clear_ram:
            self._ram_data.tiles.clear()
        if self._tile_grid.get_children():
            for button in self._tile_grid.get_children():
                self._tile_grid.remove(button)

    def add_tile_button(self, x: int, y: int, tile_data: TileData = None):
        """
        Shortcut to add a TileButton object with the given TileData at the given x and y coordinates

        :param x: Integer X coordinate to place the TileButton object.
        :param y: Integer Y coordinate to place the TileButton object.
        :param tile_data: TileData object for the TileButton object to manipulate.
        :return:
        """
        if tile_data:
            tile_button = TileButton(self._ram_data, self._textures, tile_data, size=self._config.square_size)
        else:
            self._ram_data.tiles.append(TileData(x, y))
            tile_button = TileButton(self._ram_data, self._textures, self._ram_data.tiles[-1],
                                     size=self._config.square_size)

        self._tile_grid.attach(tile_button.button, x, y, 1, 1)

    # noinspection PyUnusedLocal
    def add_top(self, button: Gtk.Button):
        """
        Quickly adds a row of TileButtons to the top of the tile map.

        :param button: Gtk.Button object, ignored.
        :return:
        """
        self._ram_data.y_start -= 1
        for x in range(self._ram_data.x_start, self._ram_data.x_end + 1):
            self.add_tile_button(x, self._ram_data.y_start)
        self._tile_grid.show_all()

    # noinspection PyUnusedLocal
    def add_bottom(self, button):
        """
        Quickly adds a row of TileButtons to the bottom of the tile map.

        :param button: Gtk.Button object, ignored.
        :return:
        """
        self._ram_data.y_end += 1
        for x in range(self._ram_data.x_start, self._ram_data.x_end + 1):
            self.add_tile_button(x, self._ram_data.y_end)
        self._tile_grid.show_all()

    # noinspection PyUnusedLocal
    def add_left(self, button):
        """
        Quickly adds a column of TileButtons to the left of the tile map.

        :param button: Gtk.Button object, ignored.
        :return:
        """
        self._ram_data.x_start -= 1
        for y in range(self._ram_data.y_start, self._ram_data.y_end + 1):
            self.add_tile_button(self._ram_data.x_start, y)
        self._tile_grid.show_all()

    # noinspection PyUnusedLocal
    def add_right(self, button):
        """
        Quickly adds a column of TileButtons to the right of the tile map.

        :param button: Gtk.Button object, ignored.
        :return:
        """
        self._ram_data.x_end += 1
        for y in range(self._ram_data.y_start, self._ram_data.y_end + 1):
            self.add_tile_button(self._ram_data.x_end, y)
        self._tile_grid.show_all()

    # noinspection PyUnusedLocal
    def _on_keypress(self, grid: Gtk.Grid, event: Gdk.EventKey):
        """
        Triggers when a key is pressed while an object in the main grid is focused. If the key is an arrow or escape key
        it keeps its normal function. Otherwise if the key is alpha, it is added to the list of currently held down
        keys.

        :param grid: Gtk.Grid object, ignored.
        :param event: Gdk.EventKey object, used to get what key was pressed.
        :return:
        """
        if event.get_keyval()[1] in {Gdk.KEY_Up, Gdk.KEY_Down, Gdk.KEY_Left, Gdk.KEY_Right, Gdk.KEY_Escape}:
            return False
        else:
            if event.string.isalpha():
                self._ram_data.held_buttons.add(event.string.upper())
        return True

    # noinspection PyUnusedLocal
    def _on_keyrelease(self, grid: Gtk.Grid, event: Gdk.EventKey):
        """
        Triggers when a key is released while an object in the main grid is focused. If the key is an arrow or escape
        key it keeps its normal function. Otherwise it if the key is alpha, it is removed from the list of currently
        held down keys.

        :param grid: Gtk.Grid object, ignored.
        :param event: Gdk.EventKey object, used to get what key was released.
        :return:
        """
        if event.get_keyval()[1] in {Gdk.KEY_Up, Gdk.KEY_Down, Gdk.KEY_Left, Gdk.KEY_Right, Gdk.KEY_Escape}:
            return False
        else:
            if event.string.isalpha():
                self._ram_data.held_buttons.remove(event.string.upper())
        return True


class TileButton:
    def __init__(self, ram_data: RamData, textures: TextureManager, tile_data: TileData, size=40, setup=True, **kwargs):
        """
        Manages the Gtk.ToggleButton object that gets placed in the tile grid.

        :param ram_data: RamData object to read and write to.
        :param textures: TextureManager object used to set the texture of the Gtk.ToggleButton.
        :param tile_data: TileData object to read and write to.
        :param size: Integer pixel size to try to be.
        :param setup: Boolean True to run the setup function, False to not.
        :param kwargs: Additional keyword arguments to pipe to the Gtk.ToggleButton.
        """
        self._ram_data = ram_data
        self._textures = textures
        self._preferred_size = size
        self._tile_data = tile_data
        self.button = Gtk.ToggleButton(relief=Gtk.ReliefStyle.NONE, **kwargs)

        if setup:
            self.setup_button()

    def setup_button(self):
        """
        Visually and functionally sets up the button, then if there's readable data
        :return:
        """
        self.button.get_style_context().add_class("map_button")
        self.button.set_size_request(self._preferred_size, self._preferred_size)
        self.button.connect("toggled", self._on_toggle)
        self.button.connect("button-press-event", self._on_press)
        self.button.connect("enter", self._on_mouse_enter)

        if self._tile_data.enabled:
            self.button.set_active(True)
        if self._tile_data.tags:
            self.update_tags()
            self.update_tooltip()
        if self._tile_data.texture and self._tile_data.texture != EMPTY_TEXTURE:
            self._textures.set_texture(self.button, self._tile_data.texture)

    # noinspection PyUnusedLocal
    def _on_press(self, button: Gtk.ToggleButton, event: Gdk.EventButton) -> bool:
        """
        Triggered when the button is pressed, contains the logic controlling if symbols get updated, textures get
        changed, or the button is toggled.

        :param button: Gtk.ToggleButton object to change the texture of when needed.
        :param event: Gdk.EventButton object, ignored.

        :return: Boolean True to consume the input, False to let it toggle the button.
        """
        return_value = False

        if self.button.get_active():
            if self._ram_data.held_buttons:
                self._tile_data.apply_letter_tags(self._ram_data.held_buttons)
                self.update_tags()
                self.update_tooltip()
                return_value = True
            elif self._ram_data.selected_texture != EMPTY_TEXTURE:
                self._tile_data.texture = self._ram_data.selected_texture
                self._textures.set_texture(button, self._tile_data.texture)
                return_value = True
            elif self._ram_data.selected_texture == EMPTY_TEXTURE and \
                    (self._tile_data.texture and self._tile_data.texture != EMPTY_TEXTURE):
                self._tile_data.texture = self._ram_data.selected_texture
                self._textures.set_texture(button, self._tile_data.texture)
                return_value = True
        else:
            if self._ram_data.held_buttons:
                self._tile_data.apply_letter_tags(self._ram_data.held_buttons)
                self.update_tags()
                self.update_tooltip()
            elif self._ram_data.selected_texture != EMPTY_TEXTURE:
                self._tile_data.texture = self._ram_data.selected_texture
                self._textures.set_texture(button, self._tile_data.texture)
        return return_value

    def _on_toggle(self, button: Gtk.ToggleButton):
        """
        Triggered when the button is toggled. Updates the TileData object as needed.

        :param button: Gtk.ToggleButton object to change the texture of when needed.
        :return:
        """
        self._tile_data.enabled = self.button.get_active()
        if not self._tile_data.enabled:
            self._tile_data.tags.clear()
            self.update_tags()
            self.update_tooltip()
            self._textures.set_texture(button, EMPTY_TEXTURE)

    def update_tags(self):
        """
        Updates the visual aspect of the tags/symbols, adding newlines and cutting off as needed.
        :return:
        """
        label_string = ""
        tag_count = 0
        for tag in self._tile_data.tags:
            tag_count += 1
            if (tag_count - 1) % 3 == 0 and tag_count != 1:
                label_string += "\n"
            label_string += tag
            if tag_count >= 6:
                break
        self.button.set_label(label_string)
        self.button.show_all()

    def update_tooltip(self):
        """
        Updates the tooltip with what data the current tags/symbols correspond with, if such data exists.
        :return:
        """
        tooltip_string = ""
        for tag in self._tile_data.tags:
            if self._ram_data.symbols[tag].get_value():
                tooltip_string += f"{self._ram_data.symbols[tag].get_value()}\n"
        self.button.set_tooltip_text(tooltip_string.strip())

    # noinspection PyMethodMayBeStatic
    def _on_mouse_enter(self, button: Gtk.ToggleButton):
        button.grab_focus()


class OptionSideBar:
    def __init__(self, config: ConfigData, ram_data: RamData, textures: TextureManager):
        """
        Manages the sidebar and the widgets in it.

        :param config: ConfigData object to read from.
        :param ram_data: RamData object to read from and write to.
        :param textures: TextureManager object to use.
        """
        self._config: ConfigData = config
        self._ram_data: RamData = ram_data
        self._textures: TextureManager = textures
        self.notebook = Gtk.Notebook()
        self._symbol_scroll = Gtk.ScrolledWindow()
        self._symbol_grid = Gtk.Grid()
        self._texture_scroll = Gtk.ScrolledWindow()
        self._texture_list = Gtk.ListBox()

    def setup(self):
        """
        Sets up all the widgets in the sidebar and initializes the symbols and textures.
        :return:
        """
        self._symbol_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self._symbol_scroll.add(self._symbol_grid)
        self._texture_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self._texture_scroll.add(self._texture_list)
        self._texture_list.connect("row-selected", self._on_texture_row_selected)

        self.notebook.append_page(self._symbol_scroll, Gtk.Label(label="Symbols"))
        self.notebook.append_page(self._texture_scroll, Gtk.Label(label="Textures"))

        self.initialize_symbols()
        self.initialize_textures()

    def clear_symbols(self, clear_ram=True):
        """
        Shortcut to destroy all children of the symbol grid and optionally clear the symbol RamData.

        :param clear_ram: Boolean True to clear the symbol RamData, False to not.
        :return:
        """
        if clear_ram:
            self._ram_data.symbols.clear()
        if self._symbol_grid.get_children():
            for element in self._symbol_grid.get_children():
                self._symbol_grid.remove(element)

    def initialize_symbols(self):
        """
        Initializes the symbol list with blank listings.
        :return:
        """
        self.clear_symbols()
        for i in range(len(string.ascii_uppercase)):
            self.add_symbol_row(i, string.ascii_uppercase[i])
        self._symbol_grid.show_all()

    def initialize_symbols_from_ram(self):
        """
        Initializes the symbol list, reading from RamData.
        :return:
        """
        self.clear_symbols(clear_ram=False)
        for i in range(len(string.ascii_uppercase)):
            self.add_symbol_row(i, string.ascii_uppercase[i],
                                symbol_data=self._ram_data.symbols.get(string.ascii_uppercase[i], None))
        self._symbol_grid.show_all()

    def add_symbol_row(self, row: int, character: str, symbol_data: SymbolData = None):
        """
        Shortcut to add a SymbolWidget to the symbol grid.

        :param row: Integer index to insert the SymbolWidget at, 0 being the top.
        :param character: String character that the SymbolWidget will show.
        :param symbol_data: Optional SymbolData object to correspond with the SymbolWidget.
        :return:
        """
        if symbol_data:
            symbol_widget = SymbolWidget(symbol_data)
        else:
            self._ram_data.symbols[character] = SymbolData(character)
            symbol_widget = SymbolWidget(self._ram_data.symbols[character])
        symbol_widget.add_to_grid(self._symbol_grid, row)

    def initialize_textures(self):
        """
        Initializes the textures list.
        :return:
        """
        texture_name_list = list(self._ram_data.textures.keys())
        texture_name_list.sort()
        for texture_name in texture_name_list:
            self._texture_list.add(TextureWidget(self._config, self._ram_data.textures[texture_name]).add_me)

    # noinspection PyUnusedLocal
    def _on_texture_row_selected(self, listbox: Gtk.ListBox, row: Gtk.ListBoxRow):
        """
        Triggers when a texture row is selected, updating RamData with the currently selected texture.

        :param listbox: Gtk.ListBox object, ignored.
        :param row: Gtk.ListBoxRow object, used to get the label containing the texture name.
        :return:
        """
        for child in row.get_child():
            if isinstance(child, Gtk.Label):
                self._ram_data.selected_texture = child.get_label().strip()


class SymbolWidget:
    def __init__(self, symbol_data: SymbolData, setup=True):
        """
        A group of related functions to manage a symbol listing.

        :param symbol_data: SymbolData object to read from.
        :param setup: Boolean True to run the setup function, False to not.
        """
        self._symbol_data: SymbolData = symbol_data
        self._label = Gtk.Label(label=symbol_data.character, halign="start")
        self._entry = Gtk.Entry(halign="end")

        if setup:
            self.setup()

    def setup(self):
        """
        Visually sets up the widgets and functionally sets up the SymbolData object.
        :return:
        """
        self._label.get_style_context().add_class("sidebar_symbol_label")
        self._symbol_data.register_get_func(self.get_value)

        if self._symbol_data.default_value:
            self._entry.set_text(self._symbol_data.default_value)

    def get_value(self):
        """
        Gets the current text in the Gtk.Entry object.
        :return:
        """
        return self._entry.get_text()

    def add_to_grid(self, grid: Gtk.Grid, index: int):
        """
        Shortcut to add both widgets to the given Gtk.Grid object.

        :param grid: Gtk.Grid object to add to.
        :param index: Integer index of the row to add to, with 0 at the top.
        :return:
        """
        grid.attach(self._label, 0, index, 1, 1)
        grid.attach(self._entry, 1, index, 1, 1)


class TextureWidget:
    def __init__(self, config: ConfigData, texture_data: TextureData, setup=True):
        """
        A group of widgets to display texture information.

        :param config: ConfigData object to read from.
        :param texture_data: TextureData object to read from.
        :param setup: Boolean True to run the setup function, False to not.
        """
        self._config = config
        self._texture_data = texture_data
        self.add_me = Gtk.Grid()
        self._image = Gtk.Image(halign="start", icon_size=self._config.square_size, pixel_size=self._config.square_size)
        self._text = Gtk.Label(label=f"  {texture_data.name}")
        if setup:
            self.setup()

    def setup(self):
        """
        Visually sets up the Gtk.Image object. If TextureData.path leads to a file, it attempts to load it from disk.
        If it's not a file, it uses the stock missing image.
        Also puts the widgets in the right place on the Gtk.Grid object.
        :return:
        """
        if pathlib.Path(self._texture_data.path).is_file():
            # noinspection PyArgumentList,PyCallByClass
            pixel_buffer = GdkPixbuf.Pixbuf.new_from_file_at_size(self._texture_data.path, self._config.square_size,
                                                                  self._config.square_size)
            self._image.set_from_pixbuf(pixel_buffer)
        else:
            self._image.set_from_icon_name(Gtk.STOCK_MISSING_IMAGE, Gtk.IconSize.DIALOG)
        self.add_me.attach(self._text, 1, 0, 1, 1)
        self.add_me.attach(self._image, 0, 0, 1, 1)
