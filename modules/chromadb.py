import os
import json
import logging
import chromadb
from .utils import console
from rich.prompt import Prompt
from rich.progress import Progress
from rich import box
from rich.panel import Panel

logger = logging.getLogger(__name__)

class ChromaDB:
    def __init__(self, storages):
        self.chroma_client = chromadb.PersistentClient(path="storage/vector_database")
        self.storages = storages

    def fetch_existing_data(self, collection):
        existing_data = {"ids": [], "metadatas":[]}
        fetch_batch = 2000
        offset = 0
        total_items = collection.count()

        with Progress(transient=True) as progress:
            task = progress.add_task(description="\n[bold blue]Fetching from database...[/bold blue]", total=total_items)

            while True:
                batch = collection.get(include=["metadatas"], limit=fetch_batch, offset=offset)

                if not batch["ids"]:
                    break
                
                existing_data["ids"].extend(batch["ids"])
                existing_data["metadatas"].extend(batch["metadatas"])

                offset += fetch_batch
                progress.advance(task, len(batch["ids"]))

        known_projects = {} # convert them to the json storages format first
        if existing_data["ids"]:
            for i in range(len(existing_data["ids"])):
                known_projects[existing_data["ids"][i]] = existing_data["metadatas"][i]

        return known_projects

    def build_lists_to_upsert(self, project, descriptions, meta_datas, slugs):
            categories_list = project.get("categories", []) or ["Unknown"]
            categories_string = ", ".join(categories_list)
            
            full_description = f"{project.get('title')}. {project.get('description')}. {categories_string}"
            descriptions.append(full_description)

            versions_list = project.get('versions') or ["Unknown"]

            meta_datas.append({
                "title": project.get('title'),
                "author": project.get('author'),
                "downloads": project.get('downloads'),
                "versions": versions_list,
                "categories": categories_list,
                "description": project.get("description"),
                "project_type": project_type
            })

            slugs.append(project.get("slug"))

    def build_database(self, project_type):
        collection = self.chroma_client.get_or_create_collection(name=project_type)
        all_projects = self.storages[project_type].load_projects()
        batch_size = 250 # How many projects the database loads into memory at once

        # Lists to upsert into the database
        descriptions = []
        meta_datas = []
        slugs = []

        for project in all_projects.values():
            self.build_lists_to_upsert(project=project,
                                        descriptions=descriptions,
                                        meta_datas=meta_datas,
                                        slugs=slugs
            )
        
        with Progress() as progress:
            task = progress.add_task(f"\n[bold blue]Building database for {project_type}s[/]", total=len(slugs))

            for i in range(0, len(slugs), batch_size):
                end = i + batch_size

                collection.add(
                    documents=descriptions[i:end],
                    metadatas=meta_datas[i:end],
                    ids=slugs[i:end]
                )
                progress.advance(task, batch_size)

        console.print(f"[bold green]Database for {project_type}s succesfully built![/]")

    def update_database(self, project_type):
        collection = self.chroma_client.get_collection(name=project_type)
        all_projects = self.storages[project_type].load_projects()

        known_projects = self.fetch_existing_data(collection=collection)

        # Create the lists to upsert
        descriptions = []
        meta_datas = []
        slugs = []
        batch_size = 250 # How many projects the database loads into memory at once

        for project in all_projects.values():
            slug = project.get("slug")

            is_new = slug not in known_projects
            is_updated = False

            if not is_new:
                old_versions = known_projects[slug].get("versions", [])
                new_versions = project.get("versions", [])

                if old_versions != new_versions:
                    is_updated = True

            if not is_new and not is_updated:
                continue

            self.build_lists_to_upsert(project=project,
                                        descriptions=descriptions,
                                        meta_datas=meta_datas,
                                        slugs=slugs
            )

        with Progress() as progress:
            task = progress.add_task(f"\n[bold blue]Updating database for {project_type}s[/]", total=len(slugs))

            for i in range(0, len(slugs), batch_size):
                end = i + batch_size

                collection.upsert(
                    documents=descriptions[i:end],
                    metadatas=meta_datas[i:end],
                    ids=slugs[i:end]
                )

                progress.advance(task, batch_size)

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

        with console.status("\n[bold blue] Searching Database...[/bold blue]"):
            results = collection.query(**query_kwargs)

        return results
    
    def format_results(self, results, project_type):
        if not results.get("ids")[0]:
            logger.error("No results received, quitting formatting:", results)
            return

        for slug, metadata in zip(results.get("ids")[0], results.get("metadatas")[0]):
            frame = Panel(
                border_style="green",
                box=box.DOUBLE,
                title=f"[bold]{metadata.get('title')}[/bold]",
                subtitle=f"[italic]By {metadata.get('author')}[/italic]",
                renderable=f"{metadata.get('description')}\n\n"
                           f"[bold]Downloads:[/bold] [blue]{metadata.get('downloads')}[/blue]\n"
                           f"[bold]Versions:[/bold] [yellow]{', '.join(metadata.get('versions'))}[/yellow]\n"
                           f"[bold]Link:[/bold] [green]https://www.modrinth.com/{project_type}/{slug}[/green]"
            )

            console.print(frame, "\n")

    def database_exists(self, project_type):
        try:
            collection = self.chroma_client.get_collection(name=project_type)
            return collection.count() > 0
        except Exception:
            return False