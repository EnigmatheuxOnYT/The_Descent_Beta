#Projet : The Descent
#Auteurs : Ahmed-Adam REZKALLAH, Noé SAMUEL


#importation des modules python
from utils import ticks
from typing import Literal
from utils import Point

#Literal permet de définir un ensemble de valeurs autorisées pour un type
#Définition des traits de personnalité possibles pour un animal
personnality_trait = Literal["fearful","patient","eater","reproductive","sociable"]
#type pour représenter la personnalité d’un animal : un dictionnaire qui associe chaque trait à un float représentant à quel point l'animal a cette personalité
personnality = dict[personnality_trait,float]


# Classes et sous-classes représentant les objectifs des animaux
class Objective:
    def __init__(self,type:str,subattribute:str=None): #initialisation d'un objectif
        self.start_time=ticks() #le nombre de ticks à la création de l'objectif
        self.type=type #le nom de l'objectif ex:"go_to", "find"
        self.subattribute_name=subattribute #nom d'un sous-attribut ex:"pos","food_type"
        self.completed = False #indique si l'objectif à été accompli
        self.current_subobjective:SubObjective=None #permet d'avoir un autre objectif mais à la création de l'attribut il n'y en a pas
        self.current_object = None #contient l'objet concerné par l'objectif ex:si l'animal doit manger et que l'objet qu'il doit manger est une baie alors cette baie sera l'attribut self.current_object
        self.importance = -1 #priorité de l'objectif
        
    def __str__(self): #méthode magique pour renvoyer un str spécifié quand on fait str(objet_de_la_classe_Objectif)
        return f"<Objective {self.type} {self.subattribute}>" if self.subattribute_name else f"<Objective {self.type}>"

    @property
    def subattribute(self):
        if self.subattribute_name is None:raise TypeError(f"Un Objectif de type {self.type} n'a pas de sous-attribut")
        return getattr(self,self.subattribute_name)

#Trouver (et manger) un type de nourriture
class Find(Objective): #hérite de la classe Objective
    def __init__(self,food_types:list[str]):
        super().__init__("find","food_type") #applique le init de la classe Objective avec  type = "find" et sous-attribut = "food_type"
        self.food_types=food_types
        self.scouting = False
    
    def switch_scouting(self):
        self.scouting = True
        self.current_object = None
        self.current_subobjective = None

#Se reproduire
class Reproduce_o(Objective): #hérite de la classe Objective
    def __init__(self):
        super().__init__("reproduce") #applique le init de la classe Objective avec  type = "reproduce"
        self.scouting = False
        self.following_since = 0
        
    def switch_scouting(self):
        self.scouting = True
        self.current_object = None
        self.current_subobjective = None

#Fuir un prédateur
class Flee(Objective): #hérite de la classe Objective
    def __init__(self,animal):
        super().__init__("flee","animal") #applique le init de la classe Objective avec  type = "flee" et sous-attribut = "animal"
        self.animal=animal
        self.current_object = animal #l'animal à fuir

class MakeAffinities(Objective): #hérite de la classe Objective
    def __init__(self):
        super().__init__("affinities") #applique le init de la classe Objective avec  type = "affinities"
        self.scouting = False
        
    def switch_scouting(self):
        self.scouting = True
        self.current_object = None
        self.current_subobjective = None

class Rest(Objective): #hérite de la classe Objective
    def __init__(self):
        super().__init__("rest") #applique le init de la classe Objective avec  type = "rest"
        self.was_scouting=False


class SubObjective(Objective):pass

# Aller à une certaine position
class GoTo(SubObjective): #hérite de la classe SubObjective
    def __init__(self,pos:tuple[float,float],must_stop:bool=True):
        super().__init__("go_to","pos") #applique le init de la classe SubObjective avec en entrées "go_to" et "pos"
        self.pos = pos #position à atteindre
        self.must_stop=must_stop

# Sous-objectif pour chercher qqch
class Scout(SubObjective): #hérite de la classe SubObjective
    def __init__(self,pattern:list[Point]):
        super().__init__("scout","pattern") #applique le init de la classe SubObjective avec en entrée "scout" et "pattern"
        self.pattern = pattern #liste des points à explorer
        self.current_index = 0 #index de la liste des points à explorer

#Sous-objectif pour terminer l'objectif principal (va potentiellement changer pour un autre moyen de détecter qu'un objectif doit être finalisé)
class CompleteObjective(SubObjective): #hérite de la classe SubObjective
    def __init__(self):
        super().__init__("complete") #applique le init de la classe Objective avec  type = "complete"

#Tuer une proie
class Kill(SubObjective): #hérite de la classe SubObjective
    def __init__(self,animal):
        super().__init__("kill","animal") #applique le init de la classe Objective avec  type = "attack" et sous-attribut = "animal"
        self.animal=animal
        self.current_object = animal #la proie

#Classes représentant les différentes actions possibles que peuvent faire les animaux
class Action:
    def __init__(self,type:str,subattribute:str=None):
        self.type=type
        self.subattribute=subattribute

    def __str__(self):#méthode magique pour renvoyer un str spécifié quand on fait str(objet_de_la_classe_Action)
        return f"<Action {self.type} {getattr(self,self.subattribute)}>" if self.subattribute else f"<Objective {self.type}>"

#Ne rien faire (sera traité comme avancer tout droit)
class NoneAction(Action): #hérite de la classe Action
    def __init__(self,*args,**kwargs):
        super().__init__("none") #applique le init de la classe Action avec  type = "none"

#Se déplacer en fonction d'un mouvement
class Move(Action): #hérite de la classe Action
    def __init__(self,movement):
        super().__init__("move","movement") #applique le init de la classe Action avec  type = "move" et subattribute = "movement"
        self.movement=movement #vecteur du déplacement

#Tourner en fonction d'une proportion de l'angle maximal que peut tourner un animal (Animal.turn) valeur entre -1 et 1
class Turn(Action): #hérite de la classe Action
    def __init__(self,angle_mod):
        super().__init__("turn","angle_mod")  #applique le init de la classe Action avec  type = "turn" et subattribute = "angle_mod"
        self.angle_mod=angle_mod #entre -1 et 1 : tourner de angle_mod*angle_max_de_rotation

#Manger une nourriture à proximité immédiate et quand l'animal est à l'arrêt
class Eat(Action): #hérite de la classe Action
    def __init__(self,food):
        super().__init__("eat","food")  #applique le init de la classe Action avec  type = "eat" et subattribute = "food"
        self.food=food #objet représentant la nourriture en question

#Attaquer un autre animal à proximité immédiate
class Attack(Action): #hérite de la classe Action
    def __init__(self,animal):
        super().__init__("attack","animal")  #applique le init de la classe Action avec  type = "attack" et subattribute = "animal"
        self.animal=animal #la cible

class Socialize(Action):
    def __init__(self,animals:list):
        super().__init__("socialize","animals")
        self.animals = animals

#Se reproduire avec un animal à proximité immédiate
class Reproduce_a(Action): #hérite de la classe Action
    def __init__(self,animal):
        super().__init__("reproduce","animal")  #applique le init de la classe Action avec  type = "reproduce" et subattribute = "animal"
        self.animal=animal #animal avec lequel il vas se reproduire

class Rest_a(Action):
    def __init__(self,*args,**kwargs):
        super().__init__("rest")  #applique le init de la classe Action avec  type = "reproduce"

