import os
import re
import json
import logging
from .utils import console

logger = logging.getLogger(__name__)

class Storage:
    def __init__(self, storage_file):
        self.storage_file = f"storage/{storage_file}"
        
        storage_dir = os.path.dirname(self.storage_file)
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)

    def store_projects(self, items):
        stable_version = re.compile(r"^\d+\.\d+(\.\d+)?$")
        all_mods = {}

        for item in items:
            all_mods[item['slug']] = {
                    "title": item["title"],
                    "slug": item["slug"],
                    "author": item["author"],
                    "description": item["description"],
                    "downloads": item["downloads"],
                    "categories": item["categories"],
                    "versions": [v for v in item["versions"] if stable_version.match(v)]
            }
            
        with open(self.storage_file, 'w') as f:
            json.dump(all_mods, f, indent=4)

    def load_projects(self):
        if not os.path.exists(self.storage_file):
            console.print(f"[bold red]No JSON storage file found called {self.storage_file}[/]")
            logger.error(f"No JSON storage file found for {self.storage_file}.")
            return None
        
        with open(self.storage_file, "r") as f:
            return json.load(f)