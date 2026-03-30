#Projet : The Descent
#Auteurs : Ahmed-Adam REZKALLAH, Noé SAMUEL

"""
Ce module contient les paramètres de la carte du simulateur
"""
#importation des modules pythons
from utils import *


has_data = False

width:int
height:int
params:dict[str]

loaded_data = None

def loop_coords(coords:tuple[Number,Number]): #permet de faire une carte qui se boucle
    """
    Hyp:coords est un tuple de deux nombres entiers
    Return: Retourne un tuple du reste de la division euclidienne de chaque coordoné par la largeur et la hauteur de la carte du simulateur.
    """
    return (coords[0]%width,coords[1]%height)

def block_coords(coords:Point):#Remet des coordonées potentiellemet hors de la simu à l'intérieur
    return (min(max(coords[0],0),width),min(max(coords[1],0),height))

def load_sim_params(param_dict:dict[str]):
    global has_data,width,height,params

    try:
        comming_version = tuple(param_dict["app_version"][:3])
        if comming_version != version[:3]:
            devprint("Version de fichier différente de la version de l'app, récupération incertaine")
        params = param_dict["params"]
    except:
        devprint("Version de fichier différente de la version de l'app, récupération incertaine")
        old_version_param_dict = {
            "width":param_dict["width"],
            "height":param_dict["height"],
            "animals":{"cerf":param_dict["animal_amount"]},
            "foods":{"basic":param_dict["food_amount"]}
        }
        params = old_version_param_dict
    
    height = params["height"]
    width = params["width"]

    has_data = True

    devprint("CHARGEMENT DE PARAMETRES DE SIMULATION REUSSI")

def unload():
    global has_data,params
    has_data,params=False,False