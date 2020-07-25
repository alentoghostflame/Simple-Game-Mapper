from gamemapper.mapper_gui import SimpleGameMapperGUI
from gamemapper.storage import ConfigData, RamData


class SimpleGameMapper:
    def __init__(self):
        self.config: ConfigData = ConfigData()
        self.ram_data: RamData = RamData()

        self.gui = SimpleGameMapperGUI(self.config, self.ram_data)

    def load(self):
        self.config.load()
        self.gui.setup()

    def save(self):
        self.config.save()

    def run(self):
        self.gui.run()
