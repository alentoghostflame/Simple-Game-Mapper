from gamemapper.storage import ConfigData, RamData, TileData
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk


class SimpleGameMapperGUI:
    def __init__(self, config: ConfigData, ram_data: RamData):
        self.config: ConfigData = config
        self.ram_data: RamData = ram_data

        self.window = Gtk.Window()
        self.css_provider = Gtk.CssProvider()
        self.main_layout = MainLayout(self.config, self.ram_data)

    def setup(self):
        self.setup_window()
        self.setup_css()
        self.setup_main_layout()

    def setup_window(self):
        self.window.connect("destroy", Gtk.main_quit)
        self.window.set_default_size(300, 300)

    def setup_css(self):
        self.css_provider.load_from_path("simple_map.css")
        # noinspection PyArgumentList
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), self.css_provider,
                                                 Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def setup_main_layout(self):
        self.window.add(self.main_layout.grid)
        self.main_layout.setup()

    def run(self):
        self.window.show_all()
        Gtk.main()


class MainLayout:
    def __init__(self, config: ConfigData, ram_data: RamData):
        self.config: ConfigData = config
        self.ram_data: RamData = ram_data

        self.grid = Gtk.Grid(valign="fill", halign="fill")
        self.top_bar = TopMenuBar()
        self.map_container = MapContainer(self.config, self.ram_data)

    def setup(self):
        self.grid.attach(self.map_container.main_grid, 0, 1, 1, 1)
        self.grid.attach(self.top_bar.toolbar, 0, 0, 1, 1)

        self.top_bar.set_map_reset_func(self.map_container.reset_layout)
        self.top_bar.setup()
        self.map_container.setup()


class TopMenuBar:
    def __init__(self):
        self.toolbar = Gtk.Toolbar()
        self.new_button = Gtk.ToolButton()
        self.save_button = Gtk.ToolButton()
        self.open_button = Gtk.ToolButton()

    def setup(self):
        self.new_button.set_icon_name(Gtk.STOCK_NEW)
        self.new_button.set_label("New")

        self.save_button.set_icon_name(Gtk.STOCK_SAVE)
        self.save_button.set_label("Save")

        self.open_button.set_icon_name(Gtk.STOCK_OPEN)
        self.open_button.set_label("Load")

        self.toolbar.insert(self.new_button, 0)
        self.toolbar.insert(self.save_button, 1)
        self.toolbar.insert(self.open_button, 2)

    def set_map_reset_func(self, function):
        self.new_button.connect("clicked", function)


class MapContainer:
    def __init__(self, config: ConfigData, ram_data: RamData):
        self.config: ConfigData = config
        self.ram_data: RamData = ram_data

        self.x_start = 0
        self.x_end = 0
        self.y_start = 0
        self.y_end = 0

        self.main_grid = Gtk.Grid(valign="fill", halign="fill")
        self.scrolled_map = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.AUTOMATIC,
                                               vscrollbar_policy=Gtk.PolicyType.AUTOMATIC)
        self.tile_grid = Gtk.Grid(valign="center", halign="center", row_homogeneous=True, column_homogeneous=True)

        self.top_button = Gtk.Button(label="+", hexpand=True)
        self.bottom_button = Gtk.Button(label="+", hexpand=True)
        self.left_button = Gtk.Button(label="+", vexpand=True)
        self.right_button = Gtk.Button(label="+", vexpand=True)

    def setup(self):
        self.setup_buttons()
        self.setup_main_grid()
        self.initialize_default_grid()

    def setup_buttons(self):
        self.top_button.connect("clicked", self.add_top)
        self.bottom_button.connect("clicked", self.add_bottom)
        self.left_button.connect("clicked", self.add_left)
        self.right_button.connect("clicked", self.add_right)

    def setup_main_grid(self):
        self.scrolled_map.add(self.tile_grid)
        self.main_grid.attach(self.scrolled_map, 1, 1, 1, 1)
        self.main_grid.attach(self.top_button, 1, 0, 1, 1)
        self.main_grid.attach(self.bottom_button, 1, 2, 1, 1)
        self.main_grid.attach(self.left_button, 0, 1, 1, 1)
        self.main_grid.attach(self.right_button, 2, 1, 1, 1)

    def initialize_default_grid(self):
        self.initialize_grid(self.config.default_x_start, self.config.default_x_end, self.config.default_y_start,
                             self.config.default_y_end)

    def initialize_grid(self, x_start=0, x_end=0, y_start=0, y_end=0):
        if self.tile_grid.get_children():
            self.ram_data.tiles.clear()
            for button in self.tile_grid.get_children():
                self.tile_grid.remove(button)

        self.x_start = x_start
        self.x_end = x_end
        self.y_start = y_start
        self.y_end = y_end
        for x in range(x_start, x_end + 1):
            for y in range(y_start, y_end + 1):
                self.add_tile_button(x, y)
        self.tile_grid.show_all()

    def reset_layout(self, button):
        self.initialize_default_grid()

    def add_tile_button(self, x, y):
        self.ram_data.tiles.append(TileData(x, y))
        tile_button = TileButton(self.ram_data.tiles[-1])
        self.tile_grid.attach(tile_button.button, x, y, 1, 1)

    def add_top(self, button):
        self.y_start -= 1
        for x in range(self.x_start, self.x_end + 1):
            self.add_tile_button(x, self.y_start)
        self.tile_grid.show_all()

    def add_bottom(self, button):
        self.y_end += 1
        for x in range(self.x_start, self.x_end + 1):
            self.add_tile_button(x, self.y_end)
        self.tile_grid.show_all()

    def add_left(self, button):
        self.x_start -= 1
        for y in range(self.y_start, self.y_end + 1):
            self.add_tile_button(self.x_start, y)
        self.tile_grid.show_all()

    def add_right(self, button):
        self.x_end += 1
        for y in range(self.y_start, self.y_end + 1):
            self.add_tile_button(self.x_end, y)
        self.tile_grid.show_all()


class TileButton:
    def __init__(self, tile_data: TileData, size=40, setup=True, **kwargs):
        self._preferred_size = size
        self.tile_data = tile_data
        self.button = Gtk.ToggleButton(relief=Gtk.ReliefStyle.NONE, **kwargs)

        if setup:
            self.setup_button()

    def setup_button(self):
        self.button.set_label(f"{self.tile_data.x}:{self.tile_data.y}\nA:B")
        self.button.get_style_context().add_class("map_button")
        self.button.set_size_request(self._preferred_size, self._preferred_size)
        self.button.connect("toggled", self.on_toggle)

    def on_toggle(self, button):
        self.tile_data.enabled = self.button.get_active()
