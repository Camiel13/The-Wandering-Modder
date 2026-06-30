import re
import os
import sys
import time
import logging
import pyfiglet
from rich import box
from rich.table import Table
from modules.utils import console
from the_wandering_modder import TheWanderingModder


with console.status("[bold blue]Aan het opstarten...[/bold blue]"):
    # Define the bot controlling object.
    app = TheWanderingModder()
    COMMAND_REGEX = re.compile(r'^(mod|datapack|resourcepack|shader|plugin)\s+(init|query)$')

    # Check for debug mode and initialize the logging.
    os.makedirs("logs", exist_ok=True)
    log_filename = f"logs/bot_{time.strftime('%Y-%m-%d_%H-%M-%S')}.log"
    log_handlers = [logging.FileHandler(log_filename)]
    
    debug_mode = "-d" in sys.argv
    if debug_mode:
        log_handlers.append(logging.StreamHandler())

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(message)s',
        handlers=log_handlers
    )
    logger = logging.getLogger(__name__)

# Started up, print logo and clear terminal.            
os.system("cls" if os.name == "nt" else "clear")
print(pyfiglet.figlet_format("The Wandering Modder"))

# Start the main loop
try:
    while True:
        command = input("\n-> ").lower().strip()

        match = COMMAND_REGEX.match(command)

        if command == "help":
            console.print("This tool is meant for finding specefic mods by just describing the functionality. You can see the table for the available commands. You have to replace {project_type} with one of the following project types: mod, datapack, resourcepack, shader or plugin.")

            table = Table(title="The Wandering Modder Commands", title_style="bold #0096db", border_style="cyan", box=box.ROUNDED)
            table.add_column("Command", style="bold green")
            table.add_column("Explanation", style="white")

            table.add_row("{project_type} init", "Sets up the searching of a specefic project type. [red]!! REQUIRED !![/red]")
            table.add_row("{project_type} query", "Search the built database for specific mods with keywords.")

            table.add_row("clear", "Clears the terminal.")
            table.add_row("exit/quit", "Shuts down the program.")

            console.print(table)
        elif match:
            project_type = match.group(1)
            action = match.group(2)

            if action == "init":
                app.init_projects(project_type=project_type)
            elif action == "query":
                app.query(project_type=project_type)
        elif command == "clear":
            os.system("cls" if os.name == "nt" else "clear")
            print(pyfiglet.figlet_format("The Wandering Modder", font="5lineoblique"))
        elif command == "exit" or command == "quit":
            with console.status("[bold yellow]Shutting down...![/bold yellow]"):
                logger.info("Shutting down by command...")
            
            console.print("[bold green]Shutdown completed[/bold green]")
            logger.info("Shutdown by command completed!")
            break
        else:
            console.print("[bold red] Command doesn't exist. Use 'help' to see all the commands.")

except KeyboardInterrupt as e:    
    with console.status("[bold yellow]Shutting down...[/bold yellow]"):
        logger.info("Shutting down by keyboard interrupt...")

    logger.info("Shutdown by keyboard interrupt completed!")
    console.print("[bold green]Shutdown completed![/bold green]")