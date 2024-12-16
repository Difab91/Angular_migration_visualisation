import streamlit as st
import os
from data_loader import dependance_file_info, failed_nodes
from graph import create_graph, get_dependencies, G
from reTransco import run_js
import importlib
import data_loader
import graph


# Recharger les modules pour éviter la mise en cache
importlib.reload(data_loader)
importlib.reload(graph)




# cut les espaces blancs en haut
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

selects = None

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