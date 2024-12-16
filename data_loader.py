import os
import json

# charger le json, en remontant d'un niveau pour aller dans transcoder-tools (ou le json de dependances est stocké)
current_directory = os.getcwd()
project_root = os.path.abspath(os.path.join(current_directory, '..'))
json_file_path = os.path.join(project_root, 'transcodeSumUp.json')

with open(json_file_path, "r") as file:
    raw_data = json.load(file)

# Transformer le JSON en un dictionnaire plat
data = [entry[1] for entry in raw_data]

# Récupérer les informations des fichiers uniquement en prenant uniquement ceux qui ont un chemin et un nom et un prenant en key, son basename de chemin 
dependance_file_info = {
    os.path.basename(item["filePath"]): item
    for item in data if item.get("filePath") and item.get("name")
}


# on recup tous les files échoué
failed_nodes = [node for node, data in dependance_file_info.items() if data.get("success") is False]
