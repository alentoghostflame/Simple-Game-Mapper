from gamemapper.mapper_gui import SimpleGameMapperGUI
from gamemapper.storage import ConfigData, RamData, SaveManager


class SimpleGameMapper:
    def __init__(self):
        self.config: ConfigData = ConfigData()
        self.ram_data: RamData = RamData()
        self.save_manager: SaveManager = SaveManager(self.ram_data)

        self.gui = SimpleGameMapperGUI(self.config, self.ram_data, self.save_manager)

    def load(self):
        self.config.load()
        self.gui.setup()

    def save(self):
        self.config.save()

    def run(self):
        self.gui.run()
