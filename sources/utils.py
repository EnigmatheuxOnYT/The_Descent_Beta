#Projet : The Descent
#Auteurs : Ahmed-Adam REZKALLAH, Noé SAMUEL, Clément Roux--Bénabou

"""
Module servant de base au projet et définissant les objets les plus importants et utilisés
"""
#importation des modules python
from setup_check import sys,os_name,pygame
from enum import Enum
from typing import Sequence, Union, Callable, overload
import math
import os,json
#import thread_loading as thread_ld

#initialisation de pygame
pygame.init()

#Version
version:tuple[int,int,int,int] = (1,0,0,3)
version_type:str = "DEV-PUBLIC"
version_string:str = "V{}.{}.{}.{} {}".format(*version,version_type)

#Variables utiles pour le développement (ne pas appeler dans le code)
activate_log = True #Affichage des print
max_fps = 60 #FPS max
activate_devmode = True #Peut servir pour tester des trucs
font_dir= os.sep.join(["data","assets","font","BAHNSCHRIFT.ttf"]) #Police de caractères utilisée
default_optimisation_level:int = 1 # appartient à N*

#En cas de version publique, on cache les print, le devmode et change le string de version
if version_type == "PUBLIC":
    activate_log=False
    activate_devmode=False
    version_string="V{}.{}.{}.{}".format(*version)

#Print uniquement si devmode est activé
def devprint(*args,**kwargs):
    if Global.devmode:print(*args,**kwargs)

#si activate_log==False on redéfinie la fonction print pour qu'elle n'affiche rien 
if not activate_log:
    def print(*args,**kwargs):return
del activate_log


#Types
Number = Union[int,float] #type qui est soit un entier soit un flotant
Color = Union[tuple[Number,Number,Number],str,Sequence[Number]] #type recopié de pygame (ColorValue) qui est soit un tuple de 3 nombres, soit un string, soit une liste ou un tuple de nombres
Point = tuple[Number,Number] #Type représentant un point : un tuple de 2 nombres

#Classes
class SignError(TypeError):pass
class InvalidFileError(TypeError):pass

#Fonctions pratiques
def ticks():return pygame.time.get_ticks() #temps écoulé depuis le lancement de pygame
def time_dif(start_time):return ticks()-start_time #temps écoulé depuis start_time
def get_events():return pygame.event.get() #renvoie les évènements pygame
#def mouse_visible(value):pygame.mouse.set_visible(value) #affiche ou cache la souris
def dist(point1:Point,point2:Point):return math.hypot((point1[0]-point2[0]),(point1[1]-point2[1])) #Donne la distance entre deux points
def sqrdist(point1:Point,point2:Point):return (point1[0]-point2[0])*(point1[0]-point2[0])+(point1[1]-point2[1])*(point1[1]-point2[1]) #Donne le carré de la distance entre deux points (plus rapide)
def quit(exit_code=0): #Quitter l'application
    pygame.quit()
    devprint(f"Le programme s'est terminé avec le code de sortie {exit_code}.")
    sys.exit(exit_code)

def get_path(path:str): #Renvoie un path correspondant à l'os
    lst=list()
    last_cut=0
    for i in range(len(path)):
        if path[i] in ["/","\\"]:
            lst.append(path[last_cut:i])
            last_cut=i+1
    lst.append(path[last_cut:])
    return os.sep.join(lst)

def get_btn_name(btn:int): #Donne le nom d'un bouton (pour l'instant en anglais)
    eng_name = pygame.key.name(btn).capitalize()
    if eng_name == "Escape":eng_name="Echap"
    elif eng_name == "Space":eng_name="Espace"
    return eng_name[:7]

#Conformément à l'article 2.2.3 du règlement, cette fonction remplace la fonction originale de pygame pour s'assuer de l'inter-opérabilité
#du projet. Ainsi, on pourra écrire les chemins d'accès de façon plus lisible dans le reste du projet
_pyg_load_img = pygame.image.load
def _check_path_and_load_image(filename:str,namehint:str="")->pygame.Surface: #Semblable à un wrapper mais avec une fonction externe
    filename=get_path(filename)
    return _pyg_load_img(filename,namehint)
pygame.image.load=_check_path_and_load_image
del _check_path_and_load_image

#Etats précis du jeu
class GameState(Enum):
    loading_menu = 10000
    in_main_menu = 10001
    in_sim_setup = 10002
    in_settings = 10004
    in_credits = 10005
    in_menu_loading = 10006
    loading_sim = 10007
    starting_sim_loaded = 10008
    starting_sim_unloaded = 10016
    in_simulation = 10009
    in_control_panel = 10010
    in_panel_settings = 10011
    quitting = 10012
    quitting_canceled = 10013
    saving_simulation = 10014
    filetypes_assignation = 10015
    in_panel_advanced = 10017
    in_panel_stats = 10018
    in_panel_quit = 10019
    in_panel_end = 10020
    in_sim_recap = 10021


#Déclaration en constantes pour l'accessibilité dans tout le code
LOADING_MENU = GameState.loading_menu
IN_MAIN_MENU = GameState.in_main_menu
IN_SIM_SETUP = GameState.in_sim_setup
IN_SETTINGS = GameState.in_settings
IN_CREDITS = GameState.in_credits
IN_MENU_LOADING = GameState.in_menu_loading
STARTING_SIM = GameState.starting_sim_loaded
STARTING_SIM_RANDOM = GameState.starting_sim_unloaded
LOADING_SIM = GameState.loading_sim
IN_SIMULATION = GameState.in_simulation
IN_PANEL_MAIN = GameState.in_control_panel
IN_PANEL_SETTINGS = GameState.in_panel_settings
IN_PANEL_STATS = GameState.in_panel_stats
IN_PANEL_ADV = GameState.in_panel_advanced
IN_PANEL_QUIT = GameState.in_panel_quit
IN_PANEL_END = GameState.in_panel_end
IN_SIM_RECAP = GameState.in_sim_recap
#SAVING_SIMULATION = GameState.saving_simulation
QUITTING = GameState.quitting
QUITTING_CANCELED = GameState.quitting_canceled
FILETYPES_ASSIGNATION = GameState.filetypes_assignation

#groupes d'états pour simplifier le code plus tard
MENU_STATES = [LOADING_MENU,IN_MAIN_MENU,IN_SIM_SETUP,IN_SETTINGS,IN_CREDITS,IN_MENU_LOADING]
SIMULATION_STATES = [STARTING_SIM,STARTING_SIM_RANDOM,LOADING_SIM,IN_SIMULATION,IN_PANEL_MAIN,IN_PANEL_SETTINGS,IN_PANEL_STATS,IN_PANEL_ADV,IN_PANEL_QUIT,IN_PANEL_END]
PANEL_STATES = [IN_PANEL_MAIN,IN_PANEL_SETTINGS,IN_PANEL_STATS,IN_PANEL_ADV,IN_PANEL_QUIT,IN_PANEL_END]
STARTING_SIM_STATES = [STARTING_SIM,STARTING_SIM_RANDOM,LOADING_SIM]
GENERIC_RUNNING_STATES = [QUITTING_CANCELED,IN_SIM_RECAP]
RUNNING_STATES = MENU_STATES+SIMULATION_STATES+GENERIC_RUNNING_STATES+[FILETYPES_ASSIGNATION]
QUIT_STATES = [QUITTING]

class Global: #Stockage des variables globales
    state:GameState = LOADING_MENU #Variable d'état du jeu
    running:bool = True #Variable de fonctionnement du jeu
    _icon = pygame.image.load("data/assets/menu/Icone_TheDescent.png")
    pygame.display.set_icon(_icon) #Icone de la fenêtre
    del _icon
    pygame.display.set_caption("The Descent") #Titre de la fenêtre
    _cursor = pygame.image.load("data/assets/menu/Curseur_souris.png")
    pygame.mouse.set_cursor((0,0),_cursor)
    del _cursor
    screen:pygame.Surface = pygame.display.set_mode((1280,720)) #Variable correspondant au contenu affiché sur la fenêtre de jeu

    opti_lvl = default_optimisation_level #Niveau d'optimisation de la simulation, permet d'obtenir de meilleurs fps (toujours insatisfaisant pour les grosses simulations)
    devmode = activate_devmode
    show_fps=False
del activate_devmode,default_optimisation_level

class UseState: #Super-classe pour l'accès aux variables d'état du jeu
    @property #transforme méthode en attribut
    def running(self):return Global.running
    @running.setter
    def running(self, value: bool):Global.running=value
    @property #transforme méthode en attribut
    def state(self):return Global.state
    @state.setter
    def state(self, value: GameState):Global.state=value


class UseScreen: #Super-classe pour l'accès aux variables de la fenêtre
    @property #transforme méthode en attribut
    def screen(self):return Global.screen
    clock = pygame.time.Clock() #Module temps intégré à pygame
    fps = max_fps
del max_fps


class Settings: #Super-classe pour l'accès aux paramètres
    keybinds:dict[str,int] = {
        "fullscreen":pygame.K_f, #Réglage des touches
        "pause":pygame.K_SPACE,
        "quit":pygame.K_ESCAPE,
        "switch_overlay":pygame.K_t
    }

    rebinding = False
    
    advanced_display:dict[str,bool] = {
        "hitbox":False,
        "path":False,
        "speed_vect":False,
        "fov":False
    }

    __path = os.path.abspath("data/params/params.json")

    @classmethod
    def save(cls):
        settings = {
            "keybinds":cls.keybinds,
            "advanced_display":cls.advanced_display,
            "display_fps":Global.show_fps
        }
        with open(cls.__path,"w") as f:
            json.dump(settings,f)
    
    @classmethod
    def load(cls):
        with open(cls.__path,) as f:
            settings = json.load(f)
        cls.keybinds=settings["keybinds"]
        cls.advanced_display=settings["advanced_display"]
        Global.show_fps=settings["display_fps"]
    
Settings.load()
if Global.devmode:
    Settings.keybinds["test"]=pygame.K_d


class Runable(UseState,UseScreen,Settings): #Super-classe pour l'accès aux 3 super-classes précédentes et aux fonctions de fonctionnement de pygame
    _next_fps_check = 30
    def _handle_base_inputs (self,disable_fullscreen=False): #Gestion des imputs de base (fermeture et plein écran) pour éviter les redondances
        for event in get_events():

            if event.type == pygame.QUIT:
                self.running = False
                self.state = QUITTING

            elif (event.type ==pygame.KEYDOWN and event.key == self.keybinds["fullscreen"]) and not disable_fullscreen and not self.rebinding:
                pygame.display.toggle_fullscreen()
            
            elif (event.type==pygame.KEYDOWN and event.key==self.keybinds["test"]) and not self.rebinding:
                devprint(self.state)
                pygame.event.post(event)

            else:
                pygame.event.post(event) #Re-publie l’événement si d'autres en ont besoin
    
    def _refresh_screen(self): #Rafraichissement de l'écran et gestion de l'affichage de la souris
        #pygame.mouse.set_visible(self.state in MOUSE_STATES)
        if Global.show_fps:
            self.screen.blit(fonts.F20("FPS : "+str(round(self.clock.get_fps()))),(1200,700))
        pygame.display.flip()
        if self.state in SIMULATION_STATES:
            Runable._next_fps_check-=1
            if Runable._next_fps_check==0:
                self._check_fps()
    
    def _check_fps(self):
        actual_fps = self.clock.get_fps()
        if actual_fps == 0 and Global.opti_lvl<10:
            Global.opti_lvl = 10
            devprint("Niveau d'optimisation mis à 10")
        elif actual_fps <= self.fps*.33 and Global.opti_lvl!=100 :
            Global.opti_lvl = min(Global.opti_lvl*round(self.fps/actual_fps),100)
            devprint("Niveau d'optimisation mis à",Global.opti_lvl)
        elif Global.opti_lvl!=1 and actual_fps >= self.fps*0.9:
            Global.opti_lvl = max(Global.opti_lvl-1,1)
            devprint("Niveau d'optimisation mis à",Global.opti_lvl)

        Runable._next_fps_check = 20

    
    def run_fcts (self,allowedstates:list[GameState],*functions:Callable[[],None]): #Fonction de boucle de base prenant en charge les différentes choses redondantes
        while self.running and self.state in allowedstates: #boucle principale
            self._handle_base_inputs()
            for function in functions:
                function()
            self._refresh_screen()
            self.clock.tick(self.fps)

    def run_fcts_once (self,*functions:Callable[[],None]):
        self._handle_base_inputs()
        for function in functions:
            function()
        self._refresh_screen()
        self.clock.tick(self.fps)

#Classe Font pour remplacer/améliorer celle de pygame dans le cas de ce projet
class Font:
    directory=font_dir
    def __init__(self,size:int,antialias:bool=True):
        self.base_font=pygame.font.Font(Font.directory, size)
        self.antialias=antialias
    
    def render(self,text:str,color:Color="black",bg_color:Union[Color,None]=None):
        return self.base_font.render(text,self.antialias,color,bg_color)
    
    def __call__(self, text:str,color:Color="black",bg_color:Union[Color,None]=None):
        return self.render(text,color,bg_color)
del font_dir

#Classe d'affichage de surfaces
class SurfDisplay:
    def __init__(self,surf:pygame.Surface|str,pos:pygame.Rect|Point):
        if isinstance(surf,pygame.Surface):
            self.surf = surf
        elif isinstance(surf,str):
            self.surf=pygame.image.load("data/assets/"+surf+".png")
        else:raise TypeError (type(surf))
        if isinstance(pos,tuple) and len(pos)==2:
            self.pos=pygame.Rect((0,0),self.surf.get_size())
            self.pos.center=pos
        elif isinstance(pos,pygame.Rect):
            self.pos = pos
        else:raise TypeError(type(pos))
    
    def draw(self):
        Global.screen.blit(self.surf,self.pos)
    
    def reload_center(self):
        center=self.pos.center
        self.pos=self.surf.get_rect(center=center)
    
    def __repr__(self):return f"<SurfDisplay({self.pos})>"


class Button: #Classe pour les boutons
    @overload
    def __init__(self,
                 pos:tuple[int,int],
                 area:tuple[int,int],
                 text:str,
                 color:Color,
                 font:Font,
                 hover_color:Color,
                 click_effect:Union[GameState,Callable[[],None]],
                 /,
                 background_color:Color=(0,0,0,0),
                 crown_color:Color=None,
                 true_center:bool=False,
                 other_surf:Union[pygame.Surface]=Global.screen,
                 ):...
    
    @overload
    def __init__(self,
                 pos:Point,
                 norm_path:str,
                 click_effect:Callable[[],None],
                 draw_surf:pygame.Surface=Global.screen,
                 /
                 ):...
    
    def __init__(self,
                 *args,
                 **kwargs
                 ):
        init_1_types_mandatory = [Point,Point,str,Color,Font,Color,GameState|Callable]
        init_1_types_optional = [Color,Color|None,bool,pygame.Surface]
        init_2_types_mandatory = [Point,str,Callable]
        init_2_types_optional = [pygame.Surface]
        if len(args)<=len(init_2_types_mandatory)+len(init_2_types_optional):
            self.__init_2__(*args)
        elif len(args)>=len(init_1_types_mandatory):
            self.__init_1__(*args,**kwargs)
        else:raise TypeError(f"arguments inattendus : "+str(args)+str(kwargs))
        self.hover=False

    def __init_1__(self,
                 pos:tuple[int,int],
                 area:tuple[int,int],
                 text:str,
                 color:Color,
                 font:Font,
                 hover_color:Color,
                 click_effect:Union[GameState,Callable[[],None]],
                 /,
                 background_color:Color=(0,0,0,0),
                 crown_color:Color=None,
                 true_center:bool=False,
                 draw_surf:Union[pygame.Surface]=Global.screen
                 ):
        self.rect = pygame.Rect((0,0),area)
        self.rect.center=pos
        self.click_effect=click_effect
        self.draw_surf = draw_surf
        self.__init_surface(text,font,color,hover_color,background_color,crown_color,true_center)
    
    def __init_2__(self,
                 pos:Point,
                 norm_path:str,
                 click_effect:Callable[[],None],
                 draw_surf:pygame.Surface=Global.screen,
                 /
                 ):
        self.norm_surf = pygame.image.load("data/assets/"+norm_path+".png")
        self.hover_surf = pygame.image.load("data/assets/"+norm_path+"_Hover.png")
        self.rect = self.norm_surf.get_rect(center=pos)
        self.click_effect = click_effect
        self.draw_surf = draw_surf
    
    def __init_surface(self,text:str,font:Font,col1:Color,col2:Color,bg_col:Color,crown_col:Color,true_center:bool):
        #Préparation des surfaces du bouton (normal + hover)
        crown_color=crown_col if crown_col != None else col1
        size = self.rect.size
        text1=font(text,col1)
        text2=font(text,col2)
        if true_center:
            rect=text1.get_rect(center=(size[0]/2,size[1]*13/28))
        else:
            rect=text1.get_rect(center=(size[0]/2,size[1]*8/14))

        #Surface normale
        self.norm_surf = pygame.Surface(size,pygame.SRCALPHA)
        self.norm_surf.fill(bg_col)
        pygame.draw.rect(self.norm_surf, crown_color, pygame.Rect((0,0),size), 2)
        self.norm_surf.blit(text1,rect)

        #Surface quand la souris passe dessus
        self.hover_surf = pygame.Surface(size,pygame.SRCALPHA)
        self.hover_surf.fill(bg_col)
        pygame.draw.rect(self.hover_surf, col2 if crown_color==col1 else crown_color, pygame.Rect((0,0),size), 2)
        self.hover_surf.blit(text2,rect)
        
    
    def update(self):
        #Vérifie si la souris est sur la surface concernée
        self.hover = self.rect.collidepoint(pygame.mouse.get_pos())

    def draw(self):
        #Dessine le bouton avec le bon état
        surf = self.hover_surf if self.hover else self.norm_surf
        self.draw_surf.blit(surf, self.rect)
    
    def clicked (self):
        if isinstance(self.click_effect,GameState):
            Global.state = self.click_effect
            pygame.event.clear()
        elif callable(self.click_effect):
            self.click_effect()
        else:
            raise TypeError(f"click_effect doit être de type GameState ou Callable, pas {type(self.click_effect)}")
    
    def check_click(self,pos:Point):
        if self.rect.collidepoint(pos):
            self.clicked()
            return True
        return False
    
    def __repr__(self):return f"<Button({self.rect.center})>"

#Gestionnaire d'affichage, mise à jour et vérification de click pour les boutons et les SurfDisplay
class DisplayManager:
    def __init__(self,btn_getter:Callable[[],list[Button]]=lambda:[],surf_getter:Callable[[],list[SurfDisplay]]=lambda:[]):
        self.btn_getter=btn_getter
        self.surf_getter=surf_getter
    
    def check_click(self):
        clicked_smth = False
        for event in get_events():
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                for btn in self.btn_getter():
                    if btn.check_click(event.pos):
                        clicked_smth=True
                        break
                else:
                    pygame.event.post(event)
            else:
                pygame.event.post(event)
        return clicked_smth
    
    def update(self):
        for btn in self.btn_getter():
            btn.update()
    
    def draw(self):
        for surf_display in self.surf_getter():
            surf_display.draw()
        for btn in self.btn_getter():
            btn.draw()

#Note : Cette classe a été construite par besoin d'utilisations de vecteurs dont on connaît le fonctionnement exact, et d'init par direction/longueur. Aucune IA n'a été utilisée pendant sa construction.
class Movement:
    """
    Classe des vecteurs.
    Peut être appelée par :
    * Des coordonées cartésiennes `(x,y)` avec ou sans mots-clefs
    * Deux points `(point_1,point_2)` avec mots-clefs, et construira le vecteur du point 1 au point 2
    * Des coodronées polaires `(length,direction)` avec mots-clefs, fonctionne comme les complexes
    """
    @overload
    def __init__(self,x:Number,y:Number):... #Init 1, on donne les coordonnées du vecteur
    @overload
    def __init__(self,*,point_1:Point,point_2:Point):... #Init 2, on donne les extrémités du vecteur
    @overload
    def __init__(self,*,length:Number,direction:Number):... #Init 3, on donne la longueur et direction du vecteur (direction en radians avec 0=droite et sens trigonométrique)

    def __init__(self,*args,**kwargs):
        if args and len(args) == 2 and not kwargs: #Cas où les arguments sont donnés de façon postionnels (donc sans mot-clef) : correspondant à l'init 1
            if isinstance(args[0],Number) and isinstance(args[1],Number):
                self.x,self.y = args #args est un tuple on peut donc assigner ainsi
                return
            raise TypeError("Les arguments positionnels dans l'init de Movement doivent être des nombres.")
        
        x,y=kwargs.get("x"),kwargs.get("y") #kwargs est un dict, la méthode get renvoie donc la valeur associée à la clef donnée, ou none si cette clef n'existe pas

        if x is not None and y is not None: #On doit vérifier avec None car si x ou y vaut 0, leur valeur bool serait False
            self.x,self.y = x,y
            return
        
        p1,p2=kwargs.get("point_1"),kwargs.get("point_2") #Récupération dans le casde l'init 2       

        if p1 is not None and p2 is not None: #Ici, on pourrait utiliser `if p1 and p2` car bool((0,0)) renvoie True, mais par souci de clarté, on laisse identique au reste
            self.x = p2[0] - p1[0] #Init par points
            self.y = p2[1] - p1[1]
            return
        
        t,r=kwargs.get("direction"),kwargs.get("length") #Récupération dans le cas de l'init 3

        if t is not None and r is not None:
            self.x = math.cos(t) * r #Trigonométrie basique vue en cours de maths
            self.y = math.sin(t) * r
            return

        raise AttributeError("Arguments invalides pour Movement")

    #Appels d'init précis, au final pratiquement pas utilisés
    @staticmethod
    def from_points(point_1:Point,point_2:Point):return Movement(point_1=point_1,point_2=point_2)
    @staticmethod
    def from_length_direction(length:Number,direction:Number):return Movement(length=length,direction=direction)
    @staticmethod
    def from_x_y(x:Number,y:Number):return Movement(x,y)
    
    @property
    def length (self):return math.hypot(self.x,self.y) #Calcule la norme du vecteur, math.hypot semble être la façon la plus rapide (et claire) pour faire sqrt(x*x+y*y)

    @length.setter #Le setter d'une property permet de lui assigner une valeur comme si c'était une véritable variable. Par exemple vect.length=1 pour normaliser
    def length (self,value): #Value est la valeur assignée, donc dans le cas vect.length=1, cette fonction sera appelée avec value=1
        if isinstance(value,(int,float)) and value>=0:
            if self.length==0: #Afin d'éviter les erreurs, imparfait mais toujours mieux qu'une erreur
                self.x=value
            else:
                fact = value/self.length #Facteur par lequel la longueur du vecteur doit être multipliée, d'où le cas à part d'une longueur nulle
                self.x*=fact
                self.y*=fact
        else:
            raise SignError("La longueur du mouvement doit être un nombre positif")
        
    #Méthodes "magiques", je les ai trouvées listées ici : https://www.geeksforgeeks.org/python/dunder-magic-methods-python/
    def __add__(self,other):
        if isinstance(other,list) and len(other)==2: #Cas vect+[x,y], on renvoie une liste
            return [other[0]+self.x,other[1]+self.y]
        elif isinstance(other,tuple) and len(other)==2: #Cas vect+(x,y), on renvoie un Point
            return (other[0]+self.x,other[1]+self.y)
        elif isinstance(other,Movement): #Cas vect1+vect2, on renvoie un Movement
            return Movement(self.x+other.x,self.y+other.y)
        else:
            raise TypeError("Peut seulement ajouter un déplacement à une liste ou tuple de longueur 2")
    
    def __sub__(self,other):return self.__add__(-other) #Cas vect-other

    def __rsub__(self,other):return self.__neg__().__add__(other) #Cas other-vect, on fait concrêtement ((-vect)+other)
    
    def __str__(self):return f"<Movement{self.__tuple__()}>" #Cas print(vect) ou str(vect)

    def __radd__(self,other):return self.__add__(other) #Cas other+vect

    def __tuple__(self):return (self.x,self.y) #Cas tuple(vect)

    def __neg__(self):return Movement(-self.x,-self.y) #Cas -vect

    def __mul__(self,other): #Cas vect*x
        if isinstance(other,Number):
            return Movement(self.x*other,self.y*other)
        else:
            raise TypeError(f"Multiplication uniquement acceptée entre un vecteur et un nombre, pas {type(other)}.")
    
    def __rmul__(self,other):return self.__mul__(other) #Cas x*vect

    def __imul__(self,other):return self.__mul__(other) #Cas vect*=x

    @property #Récupération de la direction du vecteur en degrées. Peu conseillé mais utile dans des cas très spécifiques.
    def direction_deg (self):return math.degrees(math.atan2(self.x,self.y)+math.pi)
    
    @property #Quand veut récupérer la direction, il faut être précis, l'objectif ici est d'éviter les erreurs incompréhensibles plus tard causées par la confusion entre degrées et radians
    def direction (self):raise AttributeError("Utiliser direction_rad ou direction_deg pour plus de précision")
    @direction.setter
    def direction (self,value): #Quand on assigne la direction par contre, la valeur DOIT être en radians, et j'avais la flemme de faire une méthode inutile en plus
        if isinstance(value,(float,int)):
            l = self.length
            self.x = math.cos(value)*l
            self.y = math.sin(value)*l
        else:
            raise TypeError(f"La valeur de l'angle doit être un nombre réel, pas {type(value)}")
    
    @property
    def direction_rad(self):return math.atan2(self.y,self.x) #Trigonométrie classique à nouveau, atan2 nous permet d'avoir un angle orienté
    @direction_rad.setter
    def direction_rad(self,value):self.direction=value

    def get_copy(self):return Movement(self.x,self.y) #peut servir

Vect=Movement #Au final peu utilisé, sert surtout à ce qu'il y ait quelque chose pour "Vect" quand on cherhce dans VSCode la classe des vecteurs, surtout utile aux lecteurs éventuels

#Classe pouvant être passée à DisplayManager avec les boutons mais avec le fonctionnement d'une case à cocher
class Checkbox:

    img=pygame.image.load("data/assets/menu/Bouton_Menu_Coche.png").convert_alpha()
    img_hover = pygame.image.load("data/assets/menu/Bouton_Menu_Coche_Hover.png").convert_alpha()
    img_clicked = pygame.image.load("data/assets/menu/Bouton_Menu_Coche_Clique.png").convert_alpha()
    img_clicked_hover = pygame.image.load("data/assets/menu/Bouton_Menu_Coche_Clique_Hover.png").convert_alpha()

    def __init__(self,pos:Point,func:Callable[[],None],click_rect:pygame.Rect,starting_status:bool=False):
        self.img_rect = Checkbox.img.get_rect(center=pos)
        self.func = func
        self.click_rect = click_rect
        self.hover = False
        self.checked = starting_status
    
    def update(self):self.hover = self.click_rect.collidepoint(pygame.mouse.get_pos())
    
    def clicked(self):self.func()

    def check_click(self,pos:Point):
        if self.click_rect.collidepoint(pos):
            self.clicked()
            self.checked = not self.checked
            return True
        return False
    
    def draw(self):
        if self.checked:
            if self.hover:
                Global.screen.blit(Checkbox.img_clicked_hover,self.img_rect)
            else:
                Global.screen.blit(Checkbox.img_clicked,self.img_rect)
        elif self.hover:
            Global.screen.blit(Checkbox.img_hover,self.img_rect)
        else:
            Global.screen.blit(Checkbox.img,self.img_rect)
        

class WritingTypeAndSize:#contient les polices et tailles à utiliser
    F5=Font(5)
    F6=Font(6)
    F7=Font(7)
    F8=Font(8)
    F9=Font(9)
    F10=Font(10)
    F15=Font(15)
    F18=Font(18)
    F20=Font(20)
    F22=Font(22)
    F25=Font(25)
    F30=Font(30)
    F40=Font(40)
    F60=Font(60) 
    F125=Font(125)
fonts=WritingTypeAndSize


if __name__ == "__main__":
    print(version_string)