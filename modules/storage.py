import json
import os
import re
from .utils import console

class Storage:
    def __init__(self, storage_file):
        self.storage_file = f"storage/{storage_file}"
        
        storage_dir = os.path.dirname(self.storage_file)
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)

    def store_projects(self, items):
        stable_version = re.compile(r"^\d+\.\d+(\.\d+)?$")
        all_mods = []

        for item in items:
            project = {
                "title": item["title"],
                "slug": item["slug"],
                "author": item["author"],
                "description": item["description"],
                "downloads": item["downloads"],
                "categories": item["categories"],
                "versions": [v for v in item["versions"] if stable_version.match(v)]
            }
            all_mods.append(project)

        with open(self.storage_file, 'w') as f:
            json.dump(all_mods, f, indent=4)