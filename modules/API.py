import json
import time
import logging
import requests
from .utils import console
from rich.progress import Progress

logger = logging.getLogger(__name__)

class API:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Camiel13/TheWanderingModder/0.1 (camielvanderlocht@gmail.com)'
        }
        self.base_url = "https://api.modrinth.com/v2"
        

    def get_projects(self, type):
        offset = 0
        limit = 100
        total_projects = 1      # Will get changed on the first request, is 1 so the while loop starts
        facets = json.dumps([[f"project_type:{type}"]])
        all_projects = []
        
        with Progress() as progress:
            task = progress.add_task(f"[cyan]Getting {type}s from modrinth...", total=None)

            while offset < total_projects:
                response = requests.get(
                    url=f"{self.base_url}/search",
                    headers=self.headers,
                    params={
                        'limit': limit,
                        'query': '',
                        'offset': offset,
                        'facets': facets
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    hits = data.get("hits")

                    if total_projects == 1:
                        total_projects = data.get("total_hits")
                        progress.update(task, total=total_projects)
                    offset += limit
                    progress.advance(task, len(hits))

                    all_projects.extend(hits)
                    time.sleep(0.5)
                else:
                    print("Something went wrong while getting the mods.")
                    break
                    
            return all_projects