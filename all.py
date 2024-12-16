import streamlit as st
import networkx as nx
from pyvis.network import Network
import json
import os
import subprocess

# charger le json, en remontant d'un niveau pour aller dans transcoder-tools (ou le json de dependances est stocké)
current_directory = os.getcwd()
project_root = os.path.abspath(os.path.join(current_directory, '..'))
json_file_path = os.path.join(project_root, 'transcoder-tools', 'transcodeSumUp.json')

with open(json_file_path, "r") as file:
    raw_data = json.load(file)

# Transformer le JSON en un dictionnaire plat
data = [entry[1] for entry in raw_data]

# Initialiser le graphe
G = nx.DiGraph()

# Récupérer les informations des fichiers uniquement en prenant uniquement ceux qui ont un chemin et un nom et un prenant en key, son basename de chemin 
dependance_file_info = {
    os.path.basename(item["filePath"]): item
    for item in data if item.get("filePath") and item.get("name")
}

# build les arretes et noeuds
for item in data:
    # si pas de filepath c'est pas un fichier donc on skip
    if not item.get("filePath") or not item.get("name"):
        continue

    # sinon on recupe file, nom, inject    
    fichier = os.path.basename(item["filePath"])
    name = item["name"]
    injections = item.get("injections", [])

    #on trouve les dépendances pères et enfants
    #si le nom du fichier en question est présent dans les injections d'un autre fichier alors cet autre fichier est pére de celui ci
    dependances_parents = [
        os.path.basename(other_item["filePath"])
        for other_item in data if name in other_item.get("injections", [])
    ]
    # si dans les injections du fichier en question il y'en à un qui à un path (donc un fichier) alors il est fils
    dependances_enfants = [
        os.path.basename(dependance_file_info[injection_name]["filePath"])
        for injection_name in injections if injection_name in dependance_file_info
    ]

    #pour le fichier en question on creer une arrete du parent vers lui et de lui vers ses enfants
    for parent in dependances_parents:
        G.add_edge(parent, fichier)
    for enfant in dependances_enfants:
        G.add_edge(fichier, enfant)

# Ajoute tous les fichiers au graphe comme nœuds indépendants
for file in dependance_file_info.keys():
    fichier = os.path.basename(file)
    if fichier not in G.nodes:
        G.add_node(fichier)

# build le graph interactive
# prend en arguments 
def create_graph(selects=None, enable_physics=True):
    net = Network(notebook=True)

    # si on selectionne un fichier ou un groupe de fichier, on prend tous les files
    if selects:
        for file in selects:
            # on recupe les infos du file
            file_data = dependance_file_info.get(file, {})
            name = file_data.get("name", file)
            success = file_data.get("success", True)
            color = (
                'red' if success is False else
                '#464547' if "component" in file else
                '#AB6EEF' if "constant" in file else
                '#84D0DA' if "data.service" in file else
                '#5f7ddf' if "restangular" in file else
                '#1EC5F1' if "service" in file else
                '#EDE544' if "directive" in file else
                '#8eef6a' if "pipe" in file else
                '#d67df0'
            )
            # on l'ajoute en noeud 
            net.add_node(file, label=file, shape='box', size=70, color=color, title=name)

        # dans le graph creer on va chercher si l'arrete qui va d'un noeud à l'autre est presente dans selects, si c'est le cas on ajoute l'arrete. ce qui permet de recuperer toutes les dependances depuis un seul fichier selectionné
        for edge in G.edges():
            if edge[0] in selects and edge[1] in selects:
                edge_color = 'blue' if "component" in edge[0] else '#FF69B4'
                net.add_edge(edge[0], edge[1], color=edge_color, width=2)


    # si rien n'est selectionné (par defaut), on affiche tout le graph (tous les fichiers)          
    else:
        # on va chercher tous le graph
        for file in G.nodes():
            file_data = dependance_file_info.get(file, {})
            name = file_data.get("name", file)
            success = file_data.get("success", True)
            color = (
                'red' if success is False else
                '#464547' if "component" in file else
                '#AB6EEF' if "constant" in file else
                '#84D0DA' if "data.service" in file else
                '#5f7ddf' if "restangular" in file else
                '#1EC5F1' if "service" in file else
                '#EDE544' if "directive" in file else
                '#8eef6a' if "pipe" in file else
                '#d67df0'
            )
            net.add_node(file, label=file, shape='box', size=70, color=color, title=name)

        for edge in G.edges():
            edge_color = 'blue' if "component" in edge[0] else '#FF69B4'
            net.add_edge(edge[0], edge[1], color=edge_color, width=2)

    
    # parametres/options du graph
    # on à la possibilité d'activer et désactiver la "force" entre les noeuds
    physics_option = "true" if enable_physics else "false"
    # options: tailles des noeuds....
    net.set_options(f"""
        var options = {{
        "interaction": {{
            "selectable": true
        }},
        "nodes": {{
            "font": {{
            "size": 16,
            "color": "#ffffff"
            }},
            "borderWidth": 2
        }},
        "edges": {{
            "arrows": {{
            "to": {{
                "enabled": true,
                "scaleFactor": 0.5
            }}
            }},
            "smooth": {{
            "type": "continuous"
            }}
        }},
        "physics": {{
            "enabled": {physics_option},
            "barnesHut": {{
                "gravitationalConstant": -4000,
                "centralGravity": 0.01,
                "springLength": 300,
                "springConstant": 0.005,
                "damping": 0.09
            }},
            "minVelocity": 0.5
        }}
        }}
    """)
    # on save le graphs, des qu'un new est charger dans l'app pour pouvoir le visualiser plus en precision
    net.save_graph("graph_interactive.html")
    # on l'affiche dans une fenetre dans l'app
    st.components.v1.html(open("graph_interactive.html", "r").read(), height=711)

# app streamlit
# couper les espaces blancs en haut
st.markdown("""
    <style>
    .block-container {
       padding-top: 2rem;
   }
   </style>
""", unsafe_allow_html=True)

# titre
title_placeholder = st.empty()
title_placeholder.header("Arbre des dépendances de la migration", divider='rainbow')

# toutes les posibilités de fichiers à selectionner pour visualiser: soit all (par defaut, tout l'arbre), soit les fichiers avec transcodage echoué puis tous leur arbres, soit les transcodage echoué uniquement, soit tous les fichiers individuelles disponibes 
file_names = ["all", "échecs et dépendances", "uniquement échecs"] + [os.path.basename(name) for name in dependance_file_info.keys()]
select = st.selectbox("Consulter un fichier particulier", file_names, index=0)

# Ajouter la case pour activer/désactiver la force des nœuds, avantage/incovénient de true : beaucoup plus beau sur le graph complet/ met du temps pour charger , puis false: l'inverse
enable_physics = st.checkbox("Activer la force des nœuds", value=False)

# pour avoir la descendances d'un file
def get_dependencies(G, file):
    return list(nx.descendants(G, file)) + [file]

# par defaut le graph complet
selects = None

# on recup tous les files échoué
failed_nodes = [node for node, data in dependance_file_info.items() if data.get("success") is False]

if select == "all":
    create_graph(enable_physics=enable_physics)

elif select == "échecs et dépendances":
    failed_and_dependencies = set()
    # on recup tous les noeuds étent dans les échecs
    for node in failed_nodes:
        # puis on obtient leurs descendances
        failed_and_dependencies.update(get_dependencies(G, node))
    create_graph(selects=failed_and_dependencies, enable_physics=enable_physics)

elif select == "uniquement échecs":
    # uniquement leur dépendances direct (n-1)
    create_graph(selects=failed_nodes, enable_physics=enable_physics)

# sinon c'est qu'un file en particulier à été selectionné   
else:
    # on verifie qu'il est bien dans le graph
    if os.path.basename(select) in G.nodes:
        # on recups toute sa descendnaces, car lorsque on s'interesse à un fichier en particulier on s'interesse à toutes ses descendances , on part de ce fichier en plus haut niveau meme si il à des dependances péres
        selects = get_dependencies(G, os.path.basename(select))
        create_graph(selects=selects, enable_physics=enable_physics)
    else:
        st.warning(f"Le fichier '{select}' n'existe pas dans le graphique.")



#########################  section pour relancer un transcoadage sur les fichiers en statut echec  #######################################"
# go racine
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# on va add un bouton pour relancer ce transcodage
# lorsque ce bouton est cliqué on execture index_commander.js qui prend en argument le fichier pivot (ici clas.json) et l'option --alreaydyGenaratedElements qui va chercher dans le json des dependances tous les fichiers avec success: False (ici trancodeSumUp)

# Chemins necessaire
js_script_path = os.path.join(project_root, "transcoder-tools", "index_commander.js")
# ATTENTION: MODIF LE NOM DU FICHIER PIVOT (clas.json)
pivot_file = os.path.join(project_root, "transcoder-tools", "classification", "clas.json")
dependencies_file = os.path.join(project_root, "transcoder-tools", "transcodeSumUp.json")


def run_js():
    command = [
        "node",
        js_script_path,
        pivot_file,
        "--alreaydyGenaratedElements",
        dependencies_file
    ]

    # Lancer le script et afficher les logs dans le terminal
    process = subprocess.run(
        command,
        cwd=os.path.dirname(js_script_path),  
        text=True  # Activer l'encodage texte pour la sortie
    )

    if process.returncode == 0:
        print("Script exécuté avec succès.")
    else:
        print(f"Erreur lors de l'exécution du script. Code de retour : {process.returncode}")


if st.button("Relancer les échecs"):
    st.write("Relance des fichiers en échec en cours...")
    # Appeler la fonction qui exécute le script Node.js
    run_js()
    
    # Message de succès
    st.success("Tous les fichiers en échec ont été relancés avec succès !")
    st.rerun()




########################   section sidebar pour afficher les informations personaliser d'un fichier   ######################################

# on peut voir les infos que des files présent dans le graph en cours
selectable = selects if selects else list(G.nodes())
selected = st.sidebar.selectbox("Choisissez un fichier:", selectable)

if selected:
    st.sidebar.markdown(f"""
        <h2 style="color: black; text-decoration: underline;">
            {selected}
        </h2>
    """, unsafe_allow_html=True)

    dependances_pere = ", ".join(
        parent for parent, child in G.edges() if child == selected
    )
    st.sidebar.write(f"**Dépendances parents** : {dependances_pere}")

    dependances_fils = ", ".join(
        child for parent, child in G.edges() if parent == selected
    )
    st.sidebar.write(f"**Dépendances enfants** : {dependances_fils}")

    file_data = dependance_file_info.get(selected, None)
    if file_data:
        dependances_internes = ", ".join(file_data.get('injections', []))
        tyype = file_data.get('type', "Non spécifié")
        paath = file_data.get('filePath', "Non spécifié")  
        suc = file_data.get('success', "Non spécifié")

        st.sidebar.write(f"**À l'intérieur** : {dependances_internes}")
        st.sidebar.write(f"**Type** : {tyype}")
        st.sidebar.write(f"**Path complet** : {paath}")
        st.sidebar.write(f"**Success** : {suc}")
    else:
        st.sidebar.write("Pas d'informations disponibles pour ce fichier.")
