import os
import json
import logging
import chromadb
from .utils import console
from rich.prompt import Prompt
from rich.progress import Progress

logger = logging.getLogger(__name__)

class ChromaDB:
    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(path="storage/vector_database")

    def build_database(self, project_type):
        collection = self.chroma_client.get_or_create_collection(name=project_type)
        json_storage = f"storage/{project_type}s.json"

        if not os.path.exists(json_storage):
            console.print(f"[bold red]No JSON storage file found called {json_storage}[/]")
            logger.error(f"No JSON storage file found for {json_storage}.")
            return
        
        with open(json_storage, "r") as f:
            all_projects = json.load(f)

        descriptions = []
        meta_datas = []
        slugs = []
        batch_size = 2000

        for project in all_projects.values():
            categories_list = project.get("categories", []) or ["Unknown"]
            categories_string = ", ".join(categories_list)
            
            full_description = f"{project.get('description')} || Categories: {categories_string}"
            descriptions.append(full_description)

            versions_list = project.get('versions') or ["Unknown"]

            meta_datas.append({
                "title": project.get('title'),
                "author": project.get('author'),
                "downloads": project.get('downloads'),
                "versions": versions_list,
                "categories": categories_list
            })

            slugs.append(project.get("slug"))
        
        with Progress() as progress:
            task = progress.add_task(f"[bold blue]Building database for {project_type}s[/]", total=len(slugs))

            for i in range(0, len(slugs), batch_size):
                end = i + batch_size

                collection.add(
                    documents=descriptions[i:end],
                    metadatas=meta_datas[i:end],
                    ids=slugs[i:end]
                )
                progress.advance(task, batch_size)


        console.print(f"[bold green]Database for {project_type}s succesfully built![/]")

    def get_projects(self, project_type, prompt: str, result_amount: int):
        try:
            collection = self.chroma_client.get_collection(project_type)
        except ValueError:
            console.print(f"[bold red]Couldn't find database for '{project_type}s'.[/]")
            return
        
        # Get the filters
        if project_type == 'mod':
            criteria = Prompt.ask(
                "Which modloader are you using?(leave empty for all)",
                choices=[
                    "fabric",
                    "forge",
                    "neoforge",
                    "quilt"
                ],
                default=""
            )
        elif project_type == 'shader':
            criteria = Prompt.ask(
                "Which shader mod are you using?(leave empty for all)",
                choices=[
                    "iris",
                    "optifine"
                ],
                default=""
            )
        elif project_type == 'plugin':
            criteria = Prompt.ask(
                "Which server software are you using?(leave empty for all)",
                choices=[
                    "paper",
                    "bukkit",
                    "spigot",
                    "folia",
                    "purpur"
                ],
                default=""
            )
        else:
            criteria = None

        version_criteria = console.input("What version should the project be?(leave empty for all): ") or ""

        # Apply the filters to the query
        filters = []
        
        query_kwargs = {
            "query_texts": [prompt],
            "n_results": result_amount,
        }
            
        if criteria:
            filters.append({"categories": {"$contains": criteria}})

        if version_criteria:
            filters.append({"versions": {"$contains": version_criteria}})

        if len(filters) == 1:
            query_kwargs["where"] = filters[0]
        elif len(filters) > 1:
            query_kwargs["where"] = {
                "$and": filters
            }

        results = collection.query(**query_kwargs)

        return results
    
    def format_results(self, results):
        pass # Adding in future
    