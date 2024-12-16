# Migration d'AngularJS vers Angular 17 - Application Streamlit

## Description du projet
Ce projet client s'inscrit dans le cadre de la **migration d'une application complexe** développée en AngularJS vers **Angular 17**. Cette migration a été réalisée durant mon stage de fin d'études et concerne **des milliers de fichiers de code** répartis sur une architecture complexe. 

### Contexte et enjeux
Pour surmonter ce défi, l'utilisation de **l'IA générative** a été envisagée afin de **générer automatiquement les fichiers** du nouveau projet Angular. Cependant, les problèmes de dépendances entre fichiers imposaient une méthodologie rigoureuse pour assurer une migration fluide et structurée.

### Méthodologie adoptée
La solution repose sur un **transcodage progressif et hiérarchisé** des fichiers :
1. **Analyse des dépendances** : Les fichiers sont parcourus en suivant une approche **branche par branche** (services, composants, fichiers de plus haut niveau, etc.).
2. **Transcodage des fichiers de bas niveau** : La migration démarre par les fichiers qui n'ont **pas d'importations internes** pour résoudre progressivement les dépendances ascendantes.
3. **Utilisation d'un fichier pivot** : Un fichier JSON de référence classe chaque fichier JS source par son équivalent cible (exemple : `Controller` -> `Component`) et intègre les prompts IA adaptés.
4. **Automatisation du suivi** : Un **JSON de suivi** est généré et completé pour chaque fichier transcodé, comprenant des informations clés : nom, type de fichier, statut du transcodage, chemin d'injection dans le nouveau projet, etc.

### Rôle de l'application Streamlit
Dans ce contexte, **l'application Streamlit** joue un rôle central. Elle permet de **visualiser et explorer l'arbre des dépendances** du projet, offrant ainsi une **vue d'ensemble structurée** et facilitant la gestion des fichiers à transcrire.

## Fonctionnalités principales
L'application Streamlit propose plusieurs fonctionnalités majeures :

- **Visualisation de l'arbre de dépendances** :
   - Parcours interactif des branches pour isoler des parties spécifiques du projet Angular.
   - Compréhension des relations entre les fichiers (dépendances ascendantes et descendantes).
   - Vue d'ensemble des différents types de fichiers (services, components, pipes, constantes, directives).

- **Vérification et relance du transcodage** :
   - Suivi des fichiers transcodés avec statut détaillé (réussi, échec).
   - Relance des fichiers ayant échoué directement depuis l'interface Streamlit.

- **Inspection des informations par fichier** :
   - **Dépendances ascendantes** (parents) et descendantes (enfants).
   - **Constantes internes** et chemin d'injection dans le projet migré.
   - **Statut du transcodage** et feedback (valeur entre 0 et 1).
   - **Type de fichier** (service, composant, etc.).

## Architecture de l'application
L'application est structurée autour de **quatre fichiers principaux** :

1. **`app.py`** :
   - Fichier principal qui génère l'interface utilisateur Streamlit.

2. **`graph.py`** :
   - Contient les fonctions pour :
     - Construire le graphe interactif.
     - Récupérer les dépendances de l'arbre en cours.

3. **`data_loader.py`** :
   - Fonction de chargement des données issues du fichier transcodage JSON.

4. **`retransco.py`** :
   - Permet d'exécuter la commande **TypeScript** pour relancer ou reprendre les conversions des fichiers ayant échoué précédemment.

### Fichier complet
Un fichier **`all.py`** combine toutes les fonctionnalités mentionnées ci-dessus en une seule implémentation.

## Intégration avec TS_MIGRATION_TOOLS
L'application Streamlit est implémentée comme un module complémentaire de l'outil **TS_MIGRATION_TOOLS**, qui centralise les traitements IA génératifs et les commandes de transcodage. Les appels aux fichiers transcodés sont conçus pour s'intégrer parfaitement à l'architecture globale de cet outil.

## Points forts de l'application
- **Gain de temps considérable** : Automatisation du processus de migration avec suivi visuel interactif.
- **visualisation cibler depuis un fichier cible** : Visualisation claires, personaliser et agréables à regarder selon le besoin actuelle de visualasition du fichier est ses descendances et consultation personaliser et detaillé de ses informations.
- **Contrôle précis** : Visualisation détaillée et relance ciblée des fichiers problématiques.
- **Adaptabilité** : Intégration fluide avec des outils tiers et gestion des grands volumes de données.

## Conclusion
Cette application Streamlit s'est avèré être un **outil puissant et indispensable** pour gérer le projet de migration d'AngularJS vers Angular 17. Grâce à sa capacité à **visualiser, analyser et relancer les transcodages**, elle a permis de transformer un défi complexe en un processus plus agréable, contrôlé et transparent.

---
**Technologies utilisées** : Streamlit, python, (appel à du typeScript)

**Auteur** : *BRAULT Alexis*

**Projet réalisé dans le cadre de mon stage de fin d'études**
