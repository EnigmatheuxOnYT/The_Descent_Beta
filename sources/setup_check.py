#Projet : The Descent
#Auteurs : Ahmed-Adam REZKALLAH, Noé SAMUEL

from warnings import warn,catch_warnings,filterwarnings
#Récupération de l'os
import platform
os_name=platform.system()
if os_name not in ["Darwin","Windows","Linux"]:warn(f"Votre OS (type {os_name}) n'est pas supporté par l'application.")
elif os_name in ["Darwin","Linux"]:print("Note : certaines fonctionnalités telles que le lancement depuis fichier externe et l'écran de chargement ne sont pas disponibles sur MacOS ou Linux")

import sys
def quit(exit_code=0):
    print(f"Le programme s'est terminé avec le code de sortie {exit_code}.")
    sys.exit(exit_code)
if sys.version_info<(3,10,0):
    print(f"Ce logiciel ne fonctionne pas sous python < 3.10. Votre version est {platform.python_version()}")
    quit(200)
elif sys.version_info<(3,13,0):
    warn(f"Ce logiciel est prévu pour python 3.13 ou supérieur. Votre version est {platform.python_version()}")
    import typing
    typing.Self = typing.Any
    del typing
del platform

def attempt_to_install_pygame():
    try:
        import pip
        pip.main(["install","pygame==2.6.1"])
        del pip
    except Exception as e:
        print(f"Installation de pygame 2.6.1 échouée ({e}). Merci d'installer cette version de pygame avant de relancer le programme.")
        quit(203)

def attempt_to_install_mpl():
    try:
        import pip
        pip.main(["install","matplotlib>=3.10.0"])
        del pip
    except Exception as e:
        print(f"Installation de matplotlib>=3.10.0 échouée ({e}). Merci d'installer cette version de matplotlib avant de relancer le programme.")
        quit(206)

from pathlib import Path
import os

def get_base_path():
    if getattr(sys, 'frozen', False):
        # Mode PyInstaller
        return Path(sys._MEIPASS)
    else:
        # Mode normal
        return Path(__file__).resolve().parents[1]

project_abspath = get_base_path()
os.chdir(project_abspath)
del os,project_abspath

try:

    with catch_warnings():
        filterwarnings('ignore', category=UserWarning)
        import os
        sys.stdout = open(os.devnull, 'w')
        del os
        import pygame
        sys.stdout = sys.__stdout__

    pyg_ver=pygame.vernum
    if pyg_ver!=(2,6,1):
        print(f"Pygame doit impérativement être en version 2.6.1 (actuellement {pyg_ver}).")
        install_pygame = input("Voulez-vous installer la version correcte maintenant ? (O/N)")
        if install_pygame=="O":attempt_to_install_pygame()
        else:
            print("Note : Si vous avez installé une autre version de pygame précedemment, il se peut que ce message se déclenche avec la version correcte. Nous vous conseillons de désinstaller et réinstaller la librairie pour régler le problème.")
            print("Merci d'installer cette version de pygame avant de relancer le programme.")
            quit(201)
        del install_pygame
    del pyg_ver

except ModuleNotFoundError:
    install_pygame = input("Attention, pygame n'est pas installé dans votre environnement python. Voulez-vous l'installer maintenant ? (O/N)")
    if install_pygame=="O":attempt_to_install_pygame()
    else:
        print("Merci d'installer cette version de pygame avant de relancer le programme.")
        quit(202)
    del install_pygame

try:
    import matplotlib

    mpl_ver=matplotlib.__version_info__
    if mpl_ver<(3,10,0):
        print(f"Matplotlib doit impérativement être en version 3.10.0 ou supérieur (actuellement {matplotlib.__version__}).")
        install_mpl = input("Voulez-vous installer la version correcte maintenant ? (O/N)")
        if install_mpl=="O":attempt_to_install_pygame()
        else:
            print("Merci d'installer cette version de matplotlib avant de relancer le programme.")
            quit(204)
        del install_mpl
    del mpl_ver

except ModuleNotFoundError:
    install_mpl = input("Attention, matplotlib n'est pas installé dans votre environnement python. Voulez-vous l'installer maintenant ? (O/N)")
    if install_mpl=="O":attempt_to_install_mpl()
    else:
        print("Merci d'installer cette version de matplotlib avant de relancer le programme.")
        quit(205)
    del install_mpl


del warn,catch_warnings,filterwarnings,attempt_to_install_pygame,attempt_to_install_mpl,quit