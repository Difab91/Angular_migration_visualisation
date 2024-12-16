import os
import streamlit as st
import networkx as nx
from pyvis.network import Network
from data_loader import data, dependance_file_info



# Initialiser le graphe
G = nx.DiGraph()


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

    # Ajouter des nœuds au graphe en fonction des fichiers sélectionnés
    if selects:
        for file in selects:
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
            if edge[0] in selects and edge[1] in selects:
                edge_color = 'blue' if "component" in edge[0] else '#FF69B4'
                net.add_edge(edge[0], edge[1], color=edge_color, width=2)
    else:
        # Afficher tous les nœuds et arêtes si aucune sélection
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

    # Configuration des options du graphe
    physics_option = "true" if enable_physics else "false"

    # Options d'espacement pour physique désactivée
    spacing_option = """
        "layout": {
            "hierarchical": {
                "enabled": false,
                "nodeSpacing": 200,
                "treeSpacing": 700,
                "blockShifting": false,
                "edgeMinimization": false,
                "parentCentralization": false
            }
        },
    """ if not enable_physics else ""

    # Options complètes
    net.set_options(f"""
        var options = {{
            "interaction": {{
                "selectable": true,
                "dragNodes": true
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
            {spacing_option}
            "physics": {{
                "enabled": {physics_option},
                "barnesHut": {{
                    "gravitationalConstant": -7000,
                    "centralGravity": 0.01,
                    "springLength": 400,
                    "springConstant": 0.005,
                    "damping": 0.09
                }},
                "minVelocity": 0.5
            }}
        }}
    """)

    # Sauvegarder et afficher le graphe
    net.save_graph("graph_interactive.html")
    st.components.v1.html(open("graph_interactive.html", "r").read(), height=711)






# pour avoir la descendance d'un file
def get_dependencies(G, file):
    return list(nx.descendants(G, file)) + [file]