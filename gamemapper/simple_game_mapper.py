from gamemapper.mapper_gui import SimpleGameMapperGUI, TextureManager
from gamemapper.storage import ConfigData, RamData, SaveManager


class SimpleGameMapper:
    def __init__(self):
        self.config: ConfigData = ConfigData()
        self.ram_data: RamData = RamData()
        self.save_manager: SaveManager = SaveManager(self.ram_data)
        self.textures: TextureManager = TextureManager(self.config, self.ram_data)

        self.gui = SimpleGameMapperGUI(self.config, self.ram_data, self.save_manager, self.textures)

    def load(self):
        self.config.load()
        self.textures.load()
        self.gui.setup()

    def save(self):
        self.config.save()

    def run(self):
        self.gui.run()
