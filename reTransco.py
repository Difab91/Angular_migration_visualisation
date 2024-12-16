import os
import subprocess

# Aller à la racine du projet
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Chemins nécessaires
# attention : modif avec le name du fichier pivot
pivot_file = os.path.join(project_root, "clas.json")
dependencies_file = os.path.join(project_root, "transcodeSumUp.json")

# fonction qui permet d'executer la commande ts pour un retranscodage sur les fichiers en echecs 
def run_js():
    command = f"npm run start -- {pivot_file} --alreadyGenaratedElements {dependencies_file}"

    # Exécuter la commande dans le shell
    process = subprocess.run(
        command,
        cwd=project_root,  
        shell=True,  
        text=True  
    )

    if process.returncode == 0:
        print("Script exécuté avec succès.")
    else:
        print(f"Erreur lors de l'exécution du script. Code de retour : {process.returncode}")

