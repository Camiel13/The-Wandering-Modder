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
        self.storages = {
            "mod": Storage('mods.json'),
            "datapack": Storage('datapacks.json'),
            "resourcepack": Storage('resourcepacks.json'),
            "shader": Storage('shaders.json'),
            "plugin": Storage('plugins.json')
        }
        self.chroma_client = ChromaDB(storages=self.storages)

    def init_projects(self, project_type='mod'):
        if project_type not in self.storages:
            print(f"Unknown project type: {project_type}")
            return

        if os.path.exists(self.storages[project_type].storage_file):
            storage_action = console.input(f"You already have these projects stored in [bold blue]{self.storages[project_type].storage_file}[/]. Do you want you want to overwrite/update them?(y/n): ")
            if storage_action.lower() != "y":
                pass
            else:
                projects_data = self.API.get_projects(type=project_type)
                if projects_data:
                    self.storages[project_type].store_projects(projects_data)
        else:            
            projects_data = self.API.get_projects(type=project_type)
            if projects_data:
                self.storages[project_type].store_projects(projects_data)

        database_exists = self.chroma_client.database_exists(project_type=project_type)
        if database_exists:
            database_action = console.input(f"You have already built a database for these [bold blue]{project_type}s[/]. Do you want you want to update (u) or overwrite (o) them?: ")
            if database_action.lower() == "u":
                self.chroma_client.update_database(project_type=project_type)
            elif database_action.lower() == "o": 
                self.chroma_client.build_database(project_type=project_type)
            else:
                logger.error(f"Invalid input while selecting database action: {database_action}")
                console.print("Invalid input. Quitting database building.")
        else:
            self.chroma_client.build_database(project_type=project_type)

    def query(self, project_type: str):
        prompt = console.input("What kind of project are you looking for?(use keywords, e.g. health, food, cooking): ")
        result_amount = int(console.input("How many projects do you want?: "))
        
        results = self.chroma_client.get_projects(project_type=project_type,
                                                  prompt=prompt,
                                                  result_amount=result_amount)

        self.chroma_client.format_results(results=results, project_type=project_type)
