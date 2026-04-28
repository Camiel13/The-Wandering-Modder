from modules.API import API
from modules.storage import Storage
import os
from modules.utils import console

class TheWanderingModder:
    def __init__(self):
        self.API = API()
        self.storages = {
            "mod": Storage('mods.json'),
            "datapack": Storage('datapacks.json'),
            "resourcepack": Storage('resourcepacks.json'),
            "shader": Storage('shaders.json'),
            "plugin": Storage('plugins.json')
        }

    def sync_projects(self, project_type='mod'):
        if project_type not in self.storages:
            print(f"Unknown project type: {project_type}")
            return

        if os.path.exists(self.storages[project_type].storage_file):
            overwrite = console.input(f"You already have these projects stored in [bold blue]{self.storages[project_type].storage_file}[/]. Do you want you want to overwrite/update them?(y/n):")
            if overwrite.lower() != "y":
                return

        projects_data = self.API.get_projects(type=project_type)
        if projects_data:
            self.storages[project_type].store_projects(projects_data)