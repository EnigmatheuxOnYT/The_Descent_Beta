#Projet : The Descent
#Auteurs : Ahmed-Adam REZKALLAH, Noé SAMUEL

"""
Module gérant les interactions avec les fichiers externes
"""
import os
import json
from utils import get_path

#Plus utilisé
def load_pattern(name:str)->list[list[int|float]]:
    with open(os.sep.join(["data","scout_patterns",name+".json"])) as f:
        return json.load(f)

def load_species(name:str)->dict[str]:
    with open(os.sep.join(["data","species",name+".json"])) as f:
        return json.load(f)

def load_foodtype(name:str)->dict[str]:
    with open(os.sep.join(["data","foods",name+".json"])) as f:
        return json.load(f)

def load_sim_env(path:str)->dict[str,int]:
    with open(get_path(path)) as f:
        return json.load(f)
    
def load_sim_hist_info(path:str="data/simulations/info_sim_hist.json"):
    with open(get_path(path)) as f:
        return json.load(f)