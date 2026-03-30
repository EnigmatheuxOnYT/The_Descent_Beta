Projet : The Descent
Auteurs : Ahmed-Adam REZKALLAH, Noé SAMUEL
==========================================

<pre>
2026_IDduProjet_TheDescent/
├── data/                               # Dossier contenant toutes les données du projet
│   ├── assets/                         # Dossier contenant tous les assets utilisés pour le projet
│   │   ├── animals/                    # Dossier contenant les sprites des animaux 
│   │   ├── font/                       # Police utilisée dans le projet
│   │   ├── foods/                      # Dossier contenant les sprites de la nourriture
│   │   ├── menu/                       # Dossier contenant les sprites du menu principal, boutons, tableau de bord, etc.
│   │   ├── placeholders/               # Dossier contenant les placeholders si des sprites animaux/nourriture sont manquants
│   │   ├── plants/                     # Dossier contenant les sprites des plantes
│   │   └── sim_bgs/                    # Fond de la simulation
│   ├── credits/                        # Contient le fichier .txt des crédits du menu principal
│   ├── file_type_managing/             # Dossier de gestion des extensions de fichiers
│   ├── foods/                          # Fichiers des nourritures
│   ├── params/                         # Fichiers des paramètres
│   ├── simulations/                    # Données d'exportation des simulations
│   ├── species/                        # Fichiers des espèces animales
│   └── templates/                      # Fichiers de base pour la création d'animaux ou nourritures
│
├── docs/                               # Dossier contenant les documents descriptifs du projet
│   ├── codes_de_sortie.txt             # Document listant les codes de sortie possibles pour l'application et leur signification.
│   ├── nature_du_code.txt              # Document détaillant la nature du code et l'usage de l'IA conformément au règlement article 4.5
│   ├── resume_du_projet.txt            # Document résumant l'intérêt du projet en 500 caractères ou moins
│   └── librairies_utilisees.txt        # Document listant toutes les librairies/bibliothèques utilisées dans le projet
│
├── exemples/                           # Répertoire exemples facultatif
│   ├── maquettes_avancement/           # Maquettes des différentes interfaces de l'application
│   └── Brainstorming_Miro.jpg          # Image du document Miro nous ayant servi de base pour le brainstorming au début du projet
│
├── sources/                            # Dossier contenant tous les fichiers python
│   ├── environnement/                  # Dossier contenant les différents fichiers concernant l'environnement
│   │   ├── geometry.py                 # Fichier contenant la classe gérant les hitboxs
│   │   ├── json_loader.py              # Fichier permettant de charger les informations des animaux depuis les json
│   │   ├── main.py                     # Fichier gérant les mécaniques principales de l'environnement
│   │   ├── objects.py                  # Fichier déclarant les classes des animaux et de la nourriture
│   │   ├── scale.py                    # Fichier contenant une fonction de convertissage des unités de la simulation
│   │   ├── world.py                    # Fichier contenant les information de base pour l'environnement
│   │   └── ia/                         # Dossier contenant les différents fichiers concernant l'intelligence artificielle des animaux
│   │       ├── base.py                 # Fichier déclarant les classes d'objectifs et d'actions possibles
│   │       └── main.py                 # Fichier gérant le comportement des animaux à chaque instant
│   ├── argument_launcher.py            # Fichier permettant de lancer l'application directement depuis un fichier de sauvegarde
│   ├── credits_launcher.py             # Fichier permettant d'afficher les crédits défilant dans le menu principal
│   ├── csv_export.py                   # Fichier gérant l'exportation en format csv et l'affichage des graphiques/diagrammes
│   ├── file_dialog.py                  # Fichier permettant l'ouverture de l'explorateur de fichiers pour choisir un fichier à ouvrir
│   ├── file_loader.py                  # Fichier gérant les exportations et chargements des fichiers externes de simulation
│   ├── file_type_manager.py            # Fichier gérant l'enregistrement des extensions de fichiers .sim et .simstat sous Windows
│   ├── loading_screen_mac.py           # Fichier gérant l'écran de chargement sur MacOS
│   ├── loading_screen_win.py           # Fichier gérant l'écran de chargement sur Windows
│   ├── main.py                         # Fichier main à lancer, il contient les liaisons entre les autres parties du code
│   ├── menu.py                         # Fichier gérant l'affichage du menu
│   ├── setup_check.py                  # Fichier vérifiant votre environnement python avant le lancement
│   ├── simulation.py                   # Fichier gérant la simulation de l'environnement
│   ├── text_input.py                   # Fichier du pop-up de sauvegarde de simulation
│   └── utils.py                        # Fichier contenant les parties cruciales au fonctionnement de l'application
│
├── tests/                              # Dossier contenant tous les tests réalisés au cours du projet
│   └── [Nom_du_test]/                  # Dossier ayant comme nom le ou les test(s) réalisé(s)
│       └── [Fichiers_test.py]          # Script(s) de test
│
├── LICENCE                             # Licence du projet
├── presentation.md                     # Document de présentation du projet
├── README.md                           # Guide d'installation et d'utilisation
├── requirements.txt                    # Librairies/bibliothèques nécessaires au fonctionnement du projet
└── requirements_tests.txt              # Librairies/bibliothèques nécessaires aux scripts de test
</pre>
