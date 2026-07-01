# The Wandering Modder
A fast, AI-driven search engine for Minecraft modding. It fetches data via the Modrinth API and uses a local ChromaDB vector database, allowing you to search for mods, shaders, datapacks, resource packs and plugins using natural language.

## Installation
Windows:
```powershell
git clone https://github.com/Camiel13/The-Wandering-Modder.git the_wandering_modder
cd the_wandering_modder
pip install -r requirements.txt
```

Linux:
```bash
git clone https://github.com/Camiel13/The-Wandering-Modder.git the_wandering_modder
cd the_wandering_modder
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage
To start execute this command:
```
python3 main.py
```

### The Wandering Modder Commands
You have to replace `{project_type}` with one of the following project types: `mod`, `datapack`, `resourcepack`, `shader` or `plugin`. **Make sure to describe your project in keywords (e.g. redstone, technical, components, wires)!**
| Command | Explanation |
| :--- | :--- |
| **`{project_type} init`** | Sets up the searching of a specific project type. **!! REQUIRED !!** |
| **`{project_type} query`** | Search the built database for specific mods with keywords.|
| **`help`** | Shows all the commands available.|
| **`clear`** | Clears the terminal. |
| **`exit`** / **`quit`** | Shuts down the program. |

## Hardware Acceleration
You can make the process of building the vector database up to 10-50x faster by using a dedicated Nvidia GPU with the CUDA toolkit. This is done by replacing the normal package with a GPU-supported variant and installing the CUDA toolkit onto your system. **Note that this can only be done when using a Nvidia GPU with the proper installation of the CUDA toolkit and using recent drivers!**
```bash
pip uninstall onnxruntime
pip install onnxruntime-gpu
```

