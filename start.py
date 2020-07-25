from gamemapper import SimpleGameMapper
# from typing import List
# import gi
# gi.require_version("Gtk", "3.0")
# from gi.repository import Gtk, Gdk


# DEFAULT_START_X = -1
# DEFAULT_END_X = 1
# DEFAULT_START_Y = -1
# DEFAULT_END_Y = 1
#
#
# class SimpleGameMapper:
#     def __init__(self):
#         self.window = Gtk.Window()
#         self.window.connect("destroy", Gtk.main_quit)
#         self.window.set_default_size(300, 300)
#
#         self.css_provider = Gtk.CssProvider()
#         self.css_provider.load_from_path("simple_map.css")
#         # noinspection PyArgumentList
#         Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), self.css_provider,
#                                                  Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
#
#         self.main_container = MainContainer()
#         self.window.add(self.main_container.grid)
#
#     def run(self):
#         self.window.show_all()
#         Gtk.main()
#
#
# class MainContainer:
#     def __init__(self):
#         self.grid = Gtk.Grid(valign="fill", halign="fill")
#         self.scrolled_map = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.AUTOMATIC,
#                                                vscrollbar_policy=Gtk.PolicyType.AUTOMATIC)
#         self.map_container = MapContainer(DEFAULT_START_X, DEFAULT_END_X, DEFAULT_START_Y, DEFAULT_END_Y)
#         self.grid.attach(self.scrolled_map, 0, 1, 1, 1)
#         self.scrolled_map.add(self.map_container.main_grid)
#
#         self.top_bar = TopMenuBar()
#         self.top_bar.set_map_reset_func(self.map_container.reset_layout)
#         self.grid.attach(self.top_bar.toolbar, 0, 0, 1, 1)
#
#
# class TopMenuBar:
#     def __init__(self):
#         self.toolbar = Gtk.Toolbar()
#         self.new_button = Gtk.ToolButton()
#         self.new_button.set_icon_name(Gtk.STOCK_NEW)
#         self.new_button.set_label("New")
#
#         self.toolbar.insert(self.new_button, 0)
#
#     def set_map_reset_func(self, function):
#         self.new_button.connect("clicked", function)
#
#
# class MapContainer:
#     def __init__(self, x_start=0, x_end=0, y_start=0, y_end=0):
#         self.map_button_list: List[MapButton] = []
#
#         self.x_start = x_start
#         self.x_end = x_end
#         self.y_start = y_start
#         self.y_end = y_end
#
#         self.main_grid = Gtk.Grid(valign="fill", halign="fill")
#         self.scrolled_map = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.AUTOMATIC,
#                                                vscrollbar_policy=Gtk.PolicyType.AUTOMATIC)
#         self.button_grid = Gtk.Grid(valign="center", halign="center", row_homogeneous=True, column_homogeneous=True)
#
#         self.top_button = Gtk.Button(label="+", hexpand=True)
#         self.bottom_button = Gtk.Button(label="+", hexpand=True)
#         self.left_button = Gtk.Button(label="+", vexpand=True)
#         self.right_button = Gtk.Button(label="+", vexpand=True)
#
#         self.top_button.connect("clicked", self.add_top)
#         self.bottom_button.connect("clicked", self.add_bottom)
#         self.left_button.connect("clicked", self.add_left)
#         self.right_button.connect("clicked", self.add_right)
#
#         self.setup_main_grid()
#         self.create_grid(x_start, x_end, y_start, y_end)
#
#     def create_grid(self, x_start=0, x_end=1, y_start=0, y_end=0):
#         for x in range(x_start, x_end + 1):
#             for y in range(y_start, y_end + 1):
#                 self.map_button_list.append(MapButton(x, y))
#                 self.button_grid.attach(self.map_button_list[-1].button, x, y, 1, 1)
#
#     def setup_main_grid(self):
#         self.scrolled_map.add(self.button_grid)
#         self.main_grid.attach(self.scrolled_map, 1, 1, 1, 1)
#
#         self.main_grid.attach(self.top_button, 1, 0, 1, 1)
#         self.main_grid.attach(self.bottom_button, 1, 2, 1, 1)
#         self.main_grid.attach(self.left_button, 0, 1, 1, 1)
#         self.main_grid.attach(self.right_button, 2, 1, 1, 1)
#
#     def reset_layout(self, button):
#         for button in self.button_grid.get_children():
#             self.button_grid.remove(button)
#         self.map_button_list.clear()
#         self.x_start = DEFAULT_START_X
#         self.x_end = DEFAULT_END_X
#         self.y_start = DEFAULT_START_Y
#         self.y_end = DEFAULT_END_Y
#         self.create_grid(DEFAULT_START_X, DEFAULT_END_X, DEFAULT_START_Y, DEFAULT_END_Y)
#         self.button_grid.show_all()
#
#     def add_top(self, button):
#         self.y_start -= 1
#         for x in range(self.x_start, self.x_end + 1):
#             self.map_button_list.append(MapButton(x, self.y_start))
#             self.button_grid.attach(self.map_button_list[-1].button, x, self.y_start, 1, 1)
#         self.button_grid.show_all()
#
#     def add_bottom(self, button):
#         self.y_end += 1
#         for x in range(self.x_start, self.x_end + 1):
#             self.map_button_list.append(MapButton(x, self.y_end))
#             self.button_grid.attach(self.map_button_list[-1].button, x, self.y_end, 1, 1)
#         self.button_grid.show_all()
#
#     def add_left(self, button):
#         self.x_start -= 1
#         for y in range(self.y_start, self.y_end + 1):
#             self.map_button_list.append(MapButton(self.x_start, y))
#             self.button_grid.attach(self.map_button_list[-1].button, self.x_start, y, 1, 1)
#         self.button_grid.show_all()
#
#     def add_right(self, button):
#         self.x_end += 1
#         for y in range(self.y_start, self.y_end + 1):
#             self.map_button_list.append(MapButton(self.x_end, y))
#             self.button_grid.attach(self.map_button_list[-1].button, self.x_end, y, 1, 1)
#         self.button_grid.show_all()
#
#
# class MapButton:
#     def __init__(self, x: int, y: int, size=40, **kwargs):
#         self._ran_on_size = False
#         self._preferred_size = size
#         self.x = x
#         self.y = y
#         self.button = Gtk.ToggleButton(relief=Gtk.ReliefStyle.NONE, **kwargs)
#         self.button.set_label(f"{self.x}:{self.y}\nA:B")
#         self.button.get_style_context().add_class("map_button")
#         self.button.set_size_request(self._preferred_size, self._preferred_size)
#
#     def get_toggled(self):
#         return self.button.toggled()
#
#


game_mapper = SimpleGameMapper()
game_mapper.load()
game_mapper.run()
game_mapper.save()

