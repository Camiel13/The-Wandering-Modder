import os
import logging
from modules.API import API
from modules.utils import console
from modules.storage import Storage
from modules.chromadb import ChromaDB

logger = logging.getLogger(__name__)

class TheWanderingModder:
    def __init__(self):
        self.API = API()
        self.chroma_client = ChromaDB()
        self.storages = {
            "mod": Storage('mods.json'),
            "datapack": Storage('datapacks.json'),
            "resourcepack": Storage('resourcepacks.json'),
            "shader": Storage('shaders.json'),
            "plugin": Storage('plugins.json')
        }


    def init_projects(self, project_type='mod'):
        if project_type not in self.storages:
            print(f"Unknown project type: {project_type}")
            return

        if os.path.exists(self.storages[project_type].storage_file):
            overwrite = console.input(f"You already have these projects stored in [bold blue]{self.storages[project_type].storage_file}[/]. Do you want you want to overwrite/update them?(y/n): ")
            if overwrite.lower() != "y":
                pass
            else:
                projects_data = self.API.get_projects(type=project_type)
                if projects_data:
                    self.storages[project_type].store_projects(projects_data)
        else:            
            projects_data = self.API.get_projects(type=project_type)
            if projects_data:
                self.storages[project_type].store_projects(projects_data)

        self.chroma_client.build_database(project_type=project_type)

    def query(self, projects_type: str, prompt: str, result_amount: int):
        results = self.chroma_client.get_projects(project_type=projects_type,
                                                  prompt=prompt,
                                                  result_amount=result_amount)
        
        self.chroma_client.format_results(results=results)
