#Projet : The Descent
#Auteurs : Ahmed-Adam REZKALLAH, Noé SAMUEL, Clément Roux--Bénabou

#importation des modules pythons
from utils import *
from typing import overload
from typing import Self
import environnement.world as world
from environnement.ia.base import *
from environnement.json_loader import load_species,load_foodtype
from random import random,randint,choice
import file_loader
from environnement.geometry import Triangle
import environnement.scale as scale
from csv_export import Data


def get_simparams(env):
    global simparams
    simparams = env

class NoFruitError(ValueError):pass#définition d'une exception personnalisée NoFruitError qui hérite de ValueError
ScoutingPattern = list[float]#nouveau type qui est une liste de listes de nombres (int ou float)
JsonHitbox = list[list[list[Number]]] #Façon dont les hitboxs sont enregistrées en JSON

# constantes de conversion (échelle de temps et d'espace)
FRAMES_PER_HOUR_REAL = 1200  # 1 heure ds la vraie vie = 20 sec ds la simu = 1200 frames (60 fps)
FRAMES_PER_DAY_REAL = 28800  # 1 jour réel = 480 sec simu = 28800 frames (60 fps)
UNITS_PER_METER = 100  # 100 unités simu = 1 mètre réel

def test_random(chance):return random()<chance

def _check_version_compatibility(upper_versions_args:dict):
    if upper_versions_args != {} and file_loader.is_loaded_file_version_compatible in (True,None):
        print(f"Arguments de fichier externe inattendus : {tuple(upper_versions_args.keys())}")
        file_loader.is_loaded_file_version_compatible = False

class FoodType:
    instances:dict[str,Self] = dict() #dictionnaire contenant tout les types de nourriture

    @staticmethod
    def _clear_dict():
        FoodType.instances=dict()
    
    @staticmethod
    def _load_list(new_list:list[Self]):
        FoodType._clear_dict()
        for foodtype in new_list:
            FoodType.instances[foodtype.name]=foodtype
    
    @staticmethod
    def from_file(name:str)->Self:...

    def __init__(self,
                 name:str,
                 main_sprite:str,
                 hitbox:list[list[list[float|int]]]=[],
                 reduced_to_point_color:Color="green"
                 ):
        """
        Return: Crée un objet de type 'Food Type'
        """
        self.name=name #le nom du type de nourriture
        self._img=pygame.image.load("data/assets/foods/main/"+main_sprite+".png").convert_alpha()#le sprite de la nourriture en question
        self.current_img = self._img
        self.packed=False

        self.hitbox:list[Triangle]=list()
        for points in hitbox:
            self.hitbox.append(Triangle(*points))
        
        self.reduced_to_point_color = reduced_to_point_color
        self.spawns_in_water = False
        
        if FoodType.instances.__contains__(name):
            raise NameError(f"Deux types de nourritures partagent le nom {name}.")

        FoodType.instances[name]=self #afin qu'on puisse facilement accéder à tout les types de nourritures
    
    def change_name(self,new:str):
        if FoodType.instances.__contains__(new):
            raise NameError(f"Deux types de nourritures partagent le nom {new}.")
        FoodType.instances.pop(self.name)
        FoodType.instances[new]=self
        self.name=new
    
    def _pack_for_pickle(self):
        self._img=None
        self.current_img = None
        self.packed=True
    
    def _unpack_from_pickle(self,img):
        self._img=img
        self.current_img = img
        self.packed=False
    
    def scale_sprites(self,new_zoom):
        self.current_img = pygame.transform.scale_by(self._img,new_zoom)
    
    def __repr__(self):return f"<{self.__class__.__name__}({self.name})>"

class FruitType(FoodType):#class héritant de FoodType
    def __init__(self,
                 name:str,
                 scientific_name:str,
                 biome:str,
                 main_sprite:str,
                 fruit_sprite:str,
                 fruit_pos:list[Point],
                 regen_frames:int,
                 base_energy:int,
                 hitbox:JsonHitbox,
                 *,
                 reduced_to_point_color:Color,
                 **upper_versions_args
                 ):
        """
        Return: Crée un objet de type 'Fruit Type'
        """
        _check_version_compatibility(upper_versions_args)
        super().__init__(name,main_sprite,hitbox,reduced_to_point_color=reduced_to_point_color)#applique l'init de FoodType avec name et main_sprite en arg
        self.fruit_pos = fruit_pos
        self.max_fuit_no = len(fruit_pos)
        self._fruit_img = pygame.image.load("data/assets/foods/fruits/"+fruit_sprite+'.png').convert_alpha()
        self.current_fruit_img = self._fruit_img

        self.regen_frames = regen_frames
        self.base_energy = base_energy
        self.scientific_name,self.biome=scientific_name,biome
        
    def _pack_for_pickle(self):
        self._img=None
        self.current_img = None
        self._fruit_img=None
        self.current_fruit_img=None
        self.packed=True
    
    def _unpack_from_pickle(self,img,fruit_img):
        self._img=img
        self.current_img=img
        self._fruit_img=fruit_img
        self.current_fruit_img=fruit_img
        self.packed=False
    
    def scale_sprites(self,new_zoom):
        self.current_img = pygame.transform.scale_by(self._img,new_zoom)
        self.current_fruit_img = pygame.transform.scale_by(self._fruit_img,new_zoom)


class MeatType(FoodType):#class héritant de FoodType
    def __init__(self,name:str,
                 main_sprite:str,
                 hitbox:JsonHitbox,
                 reduced_to_point_color:Color,
                 **upper_versions_args):
        """
        Return: Crée un objet de type 'Meat Type'
        """
        _check_version_compatibility(upper_versions_args)
        super().__init__(name,main_sprite,hitbox,reduced_to_point_color=reduced_to_point_color)#applique l'init de FoodType avec name et main_sprite en arg

class OtherFoodType(FoodType):
    def __init__(self,name:str,
                 main_sprite:str,
                 hitbox:JsonHitbox,
                 base_energy:int,
                 reduced_to_point_color:Color,
                 **upper_versions_args):
        """
        Return: Crée un objet de type 'Meat Type'
        """
        _check_version_compatibility(upper_versions_args)
        self.base_energy=base_energy
        super().__init__(name,main_sprite,hitbox,reduced_to_point_color=reduced_to_point_color)#applique l'init de FoodType avec name et main_sprite en arg

class FishType(OtherFoodType):
    def __init__(self,name:str,
                 main_sprite:str,
                 hitbox:JsonHitbox,
                 base_energy:int,
                 reduced_to_point_color:Color,
                 **upper_versions_args):
        """
        Return: Crée un objet de type 'FishType'
        """
        _check_version_compatibility(upper_versions_args)
        super().__init__(name,main_sprite,hitbox,base_energy,reduced_to_point_color)#applique l'init de FoodType avec name et main_sprite en arg
        self.spawns_in_water=True

def _foodtype_from_file(name:str)->FoodType:
    _values = load_foodtype(name)
    if _values["type"]=="normal":
        return OtherFoodType(**_values["attributes"])
    elif _values["type"]=="fruit":
        return FruitType(**_values["attributes"])
    elif _values["type"]=="meat":
        return MeatType(**_values["attributes"])
    elif _values["type"]=="fish":
        return FishType(**_values["attributes"])
    raise TypeError("Type de nourriture "+name+" inconnu.")

FoodType.from_file=_foodtype_from_file
del _foodtype_from_file

class Food:
    instances:list[Self] = list() #pour contenir toute les instances

    @staticmethod
    def _clear_list():
        Food.instances=list()
    
    @staticmethod
    def _load_list(new_list:list[Self]):
        Food._clear_list()
        for food in new_list:
            Food.instances.append(food)
            if food.packed:raise TypeError(str(food))
    
    def __init__(self,x:float,y:float,kind:Union[FoodType,str]):
        self.x,self.y = x,y
        self.pos = (x,y)
        if isinstance(kind,str):#si kind est un str
            self.type=FoodType.instances[kind]
        elif isinstance(kind,FoodType):#si kind est une instance de la classe FoodType
            self.type:FoodType=kind
        else:
            raise TypeError("Le type de nourriture doit être FoodType ou str, pas",type(kind)) #on fait remonter une erreur si kind n'est ni un str ni un FoodType
        self.rect=self.type._img.get_rect()
        self.rect.center=self.pos
        self.__init_type(self.type.__class__)
        self.hitbox:list[Triangle]=list()
        for triangle in self.type.hitbox:
            new = list()
            for point in triangle.points:
                v=Movement(*point)
                new.append(self.pos+v)
            self.hitbox.append(Triangle(*new))
        self.on_map=True
        Food.instances.append(self) #on ajoute l'instance à la liste d'instances (globale à la classe)
    
    def _eat_fruit(self):#définition de la méthode pour manger un fruit
        for fruit in self.fruits_list:#parcour la list de fruit
            #si le fruit peut être mangé (soit il a été mangé assez longtemps avant soit il n'a pas encore été mangé)
            if simparams.time-fruit["last_eaten"]>self.type.regen_frames or fruit["last_eaten"]==-1:
                fruit["last_eaten"]=simparams.time#met à jour le dernier moment où il a été mangé
                break #arrête de chercher après avoir mangé un fruit
        else:
            raise NoFruitError("Ce buisson n'a pas de fruit à manger")#si aucun fruit n'est disponible à manger
        return self.type.base_energy #retourne l'énergie fournie par le fruit mangé
    
    def _draw_fruit(self,surf:pygame.Surface,zoom:float,ofx:Number,ofy:Number):#définition de la méthode pour dessiner le buisson et ses fruits
            surf.blit(self.type.current_img,(self.rect.left*zoom-ofx,self.rect.top*zoom-ofy))#le buisson
            for fruit in self.fruits_list:
                if simparams.time-fruit["last_eaten"]>self.type.regen_frames or fruit["last_eaten"]==-1:#si le fuit n'a pas été magé ou si le fruit à eu le temps de se regénérer
                    surf.blit(self.type.current_fruit_img,(fruit['rect'].left*zoom-ofx,fruit['rect'].top*zoom-ofy))#les fruits
    
    def _eat_meat(self):#définition de la méthode pour manger une viande
        Food.instances.remove(self)
        self.on_map=False
        return self.base_energy
    
    def _draw_meat(self,surf:pygame.Surface,zoom:float,ofx:Number,ofy:Number):#définition de la méthode pour dessiner une viande
        surf.blit(self.type.current_img,(self.rect.left*zoom-ofx,self.rect.top*zoom-ofy))

    def __init_type(self,type:Union[type[FruitType],type[MeatType]]):
        if type==FruitType:#plus rapide que isinstance (qui n'est pas plus uttil dans ce cas puisque FruitType n'as pas de sous classe)
            self.fruits_list = [ {"rect":self.type.current_fruit_img.get_rect(center=self.rect.topleft+Movement(*pos)),#calcul de la position du fruit
                                 "last_eaten":-1,
                                 } for pos in self.type.fruit_pos]#dernière fois que ce fruit a été mangé: à -1 pour indiquer qu'il n'a pas été mangé
            #transformation des def en méthode de l'instance
            self.eat = self._eat_fruit #méthode self.eat()
            self.draw = self._draw_fruit #méthode self.draw()
        elif type==MeatType:
            self.base_energy : int
            #transformation des def en méthode de l'instance
            self.eat = self._eat_meat #méthode self.eat()
            self.draw = self._draw_meat #méthode self.draw()
        elif type == OtherFoodType:
            self.base_energy=self.type.base_energy
            self.eat = self._eat_meat #méthode self.eat()
            self.draw = self._draw_meat #méthode self.draw()
        else:
            raise TypeError(type)#sinon il y a une erreur
    
    def can_eat(self):return (isinstance(self.type,FruitType) and self.available_fruits_amount>0) or (isinstance(self.type,(MeatType,OtherFoodType)) and self.on_map)

    @property #transforme une méthode en attribut
    def available_fruits_amount(self):
        no=0
        for fruit in self.fruits_list:
            if simparams.time-fruit["last_eaten"]>self.type.regen_frames or fruit["last_eaten"]==-1:
                no+=1
        return no

    @staticmethod # quand une méthode n'a pas besoin de self pour fonctioner
    def generate(kind:str):
        if (type(kind)==str and FoodType.instances[kind].spawns_in_water) or (type(kind)==FoodType and kind.spawn_in_water):
            for _ in range(10):
                x,y=random()*world.width,random()*world.height
                if simparams.point_in_water((x,y)):
                    Food(x,y,kind)
                    return
            devprint("Spawn de poissonon échoué")
        else:
            Food(random()*world.width,random()*world.height,kind)

    def _pack_for_pickle(self):
        self.type=self.type.name
        self.packed=True
    
    def _unpack_from_pickle(self):
        self.type=FoodType.instances[self.type]
        self.packed=False


class _SexParameters:

    sprite_placeholder = pygame.image.load("data/assets/placeholders/placeholder_animaux.png")

    def __init__(self,
                    name:str,
                    name_shortcut:str,
                    maturity_days:float,
                    reproduction_stamina:int,
                    avg_speed:float,
                    sprint_speed:float,
                    sprint_time:float,
                    energy_per_m_walk_kJ:float,
                    energy_24h_kJ:float,
                    energy_reproduction_kJ:float,
                    energy_max_kJ:float,
                    avg_size:Number,
                    avg_mass:Number,
                    life_expectancy_days:int,
                    **upper_versions_args
                    ):
        _check_version_compatibility(upper_versions_args)
        
        self.name=name
        self.name_shortcut = name_shortcut

        try:
            self._img = pygame.image.load("data/assets/animals/"+name_shortcut+"/"+name+"_Idle_1_V2.png").convert_alpha()
        except FileNotFoundError:
            print(f"Sprite manquant pour {name}")
            self._img = _SexParameters.sprite_placeholder.copy()
            file_loader.create_animal_dir(name_shortcut,name)
        try:
            self._baby_img = pygame.image.load("data/assets/animals/"+name_shortcut+"/"+name+"_Baby_Idle_1_V2.png").convert_alpha()
        except FileNotFoundError:
            print(f"Sprite manquant pour {name} (bébé)")
            self._baby_img = _SexParameters.sprite_placeholder.copy()
            file_loader.create_animal_dir(name_shortcut,name+"_Baby")

        self.current_img = self._img
        self.current_baby_img = self._baby_img

        self.maturity_frames = scale.convert(maturity_days*86400,"seconds","frames")
        self.reproduction_stamina_cost = reproduction_stamina

        self.avg_speed = avg_speed
        self.sprint_speed = sprint_speed
        self.sprint_speed_sqr=sprint_speed*sprint_speed
        self.sprint_time = sprint_time

        # énergie dépensée par mètre (en kJ/m)
        self.energy_per_m_walk_kJ = energy_per_m_walk_kJ

        # besoin énergétique métabollique sur 24h (en kJ)
        self.energy_24h_kJ = energy_24h_kJ * 50

        # énrgie de reproduction (en kJ)
        self.energy_reproduction_kJ = energy_reproduction_kJ

        # capacité max énergétique (en kJ)
        self.energy_max_kJ = energy_max_kJ

        self.size,self.mass=avg_size,avg_mass
        self.life_expectancy=life_expectancy_days
    

class AnimalType:
    instances_dict:dict[str,Self] = dict()
    @staticmethod
    def get(name)->Self:
        return AnimalType.instances_dict[name]

    @staticmethod
    def _clear_dict():
        AnimalType.instances_dict=dict()
    
    @staticmethod
    def _load_list(new_list:list[Self]):
        AnimalType._clear_dict()
        for animaltype in new_list:
            AnimalType.instances_dict[animaltype.name_shortcut]=animaltype
    
    def __init__(self,name:str):
        self.__assign(**load_species(name))
        self.packed=False

    def __assign(self,
                 scientific_name:str,
                 name_shortcut:str,
                 max_stamina:int,
                 max_food_reserve:int,
                 max_hp:int,
                 fov:int,
                 view_dist:int,
                 scout_pattern:ScoutingPattern,
                 personnality:dict[str,float],
                 predators:list[str],
                 foods:list[str],
                 diet:str,
                 has_meat:bool,
                 stamina_recovery_rate:float,
                 hitbox:list[list[list[float|int]]],
                 reduced_to_point_color:Color,
                 male:dict,
                 female:dict,
                 **upper_versions_args
                 ):
        _check_version_compatibility(upper_versions_args)
        self.scientific_name=scientific_name
        self.name_shortcut = name_shortcut
        self.max_stamina = max_stamina
        self.max_metabolic_energy_kJ = max_food_reserve
        self.max_hp = max_hp
        self.fov = eval(fov,{"pi":math.pi})
        self.view_dist = view_dist
        self.personnality = personnality
        self.predators,self.foods= set(predators),set(foods)
        self.diet=diet
        self.pattern = scout_pattern
        self.has_meat=has_meat
        if has_meat:
            self.food_type:FoodType = FoodType.from_file("meat_generic")
            self.food_type.change_name(name_shortcut)
        else:
            self.food_type = None

        # récupération de stamina
        self.stamina_recovery_rate = stamina_recovery_rate
        
        self.f_params=_SexParameters(**female)
        self.m_params=_SexParameters(**male)
        self.sex_params = {0:self.f_params,
                           1:self.m_params,
                           }
        
        self.hitbox:list[Triangle]=list()
        for points in hitbox:
            self.hitbox.append(Triangle(*points))

        self.reduced_to_point_color = reduced_to_point_color

        self.last_gen = 0

        if AnimalType.instances_dict.__contains__(name_shortcut):
            raise NameError(f"Deux espèces partagent le nom {name_shortcut}.")

        AnimalType.instances_dict[name_shortcut] = self
    
    def _pack_for_pickle(self):
        self.f_params._img=self.m_params._img=None
        self.f_params._baby_img=self.m_params._baby_img=None
        self.f_params.current_img=self.m_params.current_img=None
        self.f_params.current_baby_img=self.m_params.current_baby_img=None

        if self.has_meat:
            self.food_type=self.food_type.name
        self.packed=True
    
    def _unpack_from_pickle(self,m_img,f_img,m_baby_img,f_baby_img):
        self.f_params._img,self.m_params._img=f_img,m_img
        self.f_params._baby_img,self.m_params._baby_img=f_baby_img,m_baby_img
        self.f_params.current_img,self.m_params.current_img=f_img,m_img
        self.f_params.current_baby_img,self.m_params.current_baby_img=f_baby_img,m_baby_img
        if self.has_meat:
            self.food_type=FoodType.instances[self.food_type]
        self.packed=False
    
    def scale_sprites(self,new_zoom):
        self.f_params.current_img = pygame.transform.scale_by(self.f_params._img,new_zoom)
        self.m_params.current_img = pygame.transform.scale_by(self.m_params._img,new_zoom)
        self.f_params.current_baby_img = pygame.transform.scale_by(self.f_params._baby_img,new_zoom)
        self.m_params.current_baby_img = pygame.transform.scale_by(self.m_params._baby_img,new_zoom)


class Memory:
    def __init__(self):
        self.food_spots : set[Food] = set()
        self.seen_predators : set[tuple[Animal,int]] = set() #int:dernière fois qu'il a été vu
        self.seen_preys : set[tuple[Animal,int]] = set()
        self.affinities : dict[int,tuple[int,int]] = dict() #int:niveau d'affinité entre -2 et 3,int:dèrnière fois qua ça augmenté

class Animal:

    instances:list[Self] = list() #list contenant tout les animaux vivants
    next_available_id:int = 0
    id_dict:dict[int,Self] = dict()

    @staticmethod
    def _clear_list():
        Animal.instances=list()
        Animal.next_available_id = 0
        Animal.id_dict=dict()
    
    @staticmethod
    def _load_list(new_list:list[Self]):
        Animal._clear_list()
        for animal in new_list:
            Animal.id_dict[animal.id]=animal
            Animal.next_available_id=max(animal.id+1,Animal.next_available_id)
            Animal.instances.append(animal)
    
    @staticmethod
    def generate(type:str):
        Animal((random()*world.width,random()*world.height),AnimalType.get(type))

    mutation_rate:float = 1.0
    mutation_strength:float = .2
    acceleration = 0.1 #Pourcentage de la vitesse maximale de l'animal qu'il peut modifier en 1 tick
    turn = math.pi/300 #Angle en radian maximal que l'animal peut modifier en 1 tick
    water_mult=0.8
    rest_length=360

    different_moves = []

    @overload #permet d'init de plusieurs façons (affichage)
    def __init__(self,start_pos:tuple[Number,Number],animaltype:AnimalType):...

    @overload
    def __init__(self,parent1:Self,parent2:Self,/):...#"/" signifie qu'on ne peut pas entrer les arguments sous forme de kwarg

    def __init__(self,*args,**kwargs):

        self.last_move:Movement = Movement(length=1,direction=random()*math.pi*2)
        self.dead = False
        self.deg = self.last_move.direction_deg
        self.rad = self.last_move.direction_rad
        self.speed = 0
        self.sex = random()<0.5

        if all([isinstance(arg,Animal) for arg in args]) and kwargs == dict():#vérifie que tout les arguments sont des instances de la classe Animal et qu'il n'y a pas de key word arguments (ex: func(k=7); k=7 est un key word argument ou kwarg)
            self.__init_parents__(*args)
        elif (len(args)==2 and len(kwargs)==0 and type(args[1])==AnimalType and type(args[0])==tuple):
            self.__init_type__(args[1],args[0])
        elif (len(args)==0 and len(kwargs)==2 and type(kwargs.items()[1])==AnimalType and type(kwargs.items()[0])==tuple and kwargs.__contains__("animaltype") and kwargs.__contains__("start_pos")):
            self.__init_type__(kwargs["animaltype"],kwargs["start_pos"])
        else:
            raise TypeError()

        self.sex_params = self.species.sex_params[self.sex]

        # initialisation pr l'énergie réaliste
        self._init_energy_parameters()
        self.stamina = self.max_stamina
        self.metabolic_energy_kJ = self.max_metabolic_energy_kJ
        self.hp = self.max_hp
        self.objectives:list[Objective] = [Find(list(self.species.foods)),Reproduce_o(),MakeAffinities(),Rest()]
        self.scouting_objective = Scout(self.get_scout_path())
        self.current_objective = None
        self.memory = Memory()
        self.hitbox=self.get_hitbox()
        self.meat=None
        self.time_resting = 0
        self._circle_diameter = 2/Animal.turn*self.max_speed #Circonférence = 2 pi/turn * max_speed. Diamètre = Circonférence/pi
        self.packed=False
        self.id = Animal.next_available_id

        Animal.id_dict[self.id] = self
        Animal.next_available_id += 1
        Animal.instances.append(self)
        Data.animals_born[self.id]=[self,simparams.time]

    def __init_positions__(self): #Définit les différents points de l'animal pour le déplacement et le sprite
        self.center_head_dist = self.sex_params._img.get_height()//2

    def __init_parents__(self,parent1:Self,parent2:Self):
        def get_mutation(val1,val2)->float:return (val1+val2)/2*(1+test_random(Animal.mutation_rate)*Animal.mutation_strength*(-1**test_random(.5)))
        self.species=parent1.species
        self.pos = parent1.pos+Vect(point_1=parent1.pos,point_2=parent2.pos)
        self.max_stamina = get_mutation(parent1.stamina,parent2.stamina)
        self.max_metabolic_energy_kJ = get_mutation(parent1.max_metabolic_energy_kJ,parent2.max_metabolic_energy_kJ)
        self.max_hp = get_mutation(parent1.max_hp,parent2.max_hp)
        self.max_speed = get_mutation(parent1.max_speed,parent2.max_speed)
        self.sprint_speed = get_mutation(parent1.sprint_speed,parent2.sprint_speed)
        self.fov = self.species.fov
        self.view_dist = get_mutation(parent1.view_dist,parent2.view_dist)
        self.sqr_view_dist= self.view_dist*self.view_dist
        self.scout_pattern = []
        if test_random(.5):
            pattern = parent1.scout_pattern
        else:
            pattern = parent2.scout_pattern
        for angle in pattern:
            self.scout_pattern.append(angle+(-1**test_random(.5))*random()*Animal.mutation_strength)
        if test_random(Animal.mutation_rate):
            if test_random(.5):
                self.scout_pattern.append(self.scout_pattern[-1]+(-1**test_random(.5))*random()*Animal.mutation_strength)
            elif len(self.scout_pattern)>1:
                self.scout_pattern.pop()
        
        self.personnality = dict()
        for trait in parent1.personnality.keys():
            if test_random(.5):
                self.personnality[trait] = min(max(parent1.personnality[trait]+(-1**test_random(.5))*random()*Animal.mutation_strength,0),1)
            else:
                self.personnality[trait] = min(max(parent2.personnality[trait]+(-1**test_random(.5))*random()*Animal.mutation_strength,0),1)
        self.gen = max(parent1.gen,parent2.gen)+1
        self.species.last_gen = max(self.species.last_gen,self.gen)
        self.age = simparams.time
        self.juvenile = True

    def __init_type__(self,type:AnimalType,start_pos:tuple[Number,Number]):
        self.pos:Point = start_pos
        self.max_stamina = type.max_stamina # vigueur max que l'animal peut avoir (y'a pas d'unité)
        self.max_metabolic_energy_kJ = type.max_metabolic_energy_kJ # réserve énergétique métabolique max de l'animal (en kJ)
        self.max_hp = type.max_hp
        self.max_speed=type.sex_params[self.sex].avg_speed
        self.sprint_speed=type.sex_params[self.sex].sprint_speed
        self.fov = type.fov
        self.view_dist = type.view_dist
        self.sqr_view_dist = type.view_dist*type.view_dist
        self.scout_pattern = type.pattern
        self.personnality = type.personnality
        self.species = type
        self.gen = 1
        self.age = -type.sex_params[self.sex].maturity_frames
        self.juvenile = False

    #### ci-dessous les nouvelles fonctions pr le sytème de calcul d'énergie :

    def _init_energy_parameters(self):
        """
        Initialise les paramètres d'énergie réaliste à partir des données du type d'animal.
        Convertit les valeurs réelles en valeurs de simulation.
        """
        # énergie dépensée par unité de distance parcourue (en kJ/unité)
        # 1 mètre = UNITS_PER_METER unités
        params = self.species.sex_params[self.sex]

        self.energy_per_unit_walk = params.energy_per_m_walk_kJ / UNITS_PER_METER

        # coup métabollique pour la reproduction (en kJ)
        self.energy_reproduction = params.energy_reproduction_kJ

        # besoin quotidien énergétique réparti sur toutes les frames (donc en kJ/frame)
        self.base_energy_per_frame = params.energy_24h_kJ / FRAMES_PER_DAY_REAL

        # énergie max stockable (en kJ)
        self.energy_max_kJ = params.energy_max_kJ

        # seuil de faim critique, si l'énergie de l'animal descend en dessous du seuil, il crève :)
        self.starvation_threshold = self.max_metabolic_energy_kJ * 0.1
    
    def _pack_for_pickle(self):
        self.species=self.species.name_shortcut
        self.age=simparams.time-self.age
        #self.in_view_animals=self.in_view_foods = list()
        self.packed=True

    def _unpack_from_pickle(self):
        self.species = AnimalType.instances_dict[self.species]
        self.age=simparams.time-self.age
        self.packed=False
    
    def get_hitbox(self):
        triangles:list[Triangle]=list()
        for triangle in self.species.hitbox:
            new = list()
            for point in triangle.points:
                v=Movement(*point)
                v.direction_rad+=self.rad
                new.append(self.pos+v)
            triangles.append(Triangle(*new))
        return triangles
    
    def collide(self,hitbox:list[Triangle]):
        for own_triangle in self.hitbox:
            for other_triangle in hitbox:
                if own_triangle.collidetriangle(other_triangle):
                    return True
        return False
    
    def move(self,move:Vect,update_vars:bool=True):
            
            if self.in_water():move*=Animal.water_mult

            if move.length > 0.01:
                if update_vars:
                    self.deg = move.direction_deg
                    self.rad = move.direction_rad
                speed_ratio = move.length / self.max_speed # détermine si l'animal est en train de sprint ou pas
                if speed_ratio == 1.0 :
                    metabolic_cost = move.length * 1.5 * self.energy_per_unit_walk # cout métabolique plus élevé (puisque l'animal sprint)
                    stamina_cost = move.length * 0.25 * speed_ratio # cout de stamina plus élevé (puisque l'animal sprint)
                    self.metabolic_energy_kJ -= metabolic_cost
                    self.stamina -= stamina_cost
                else :
                    metabolic_cost = move.length * self.energy_per_unit_walk
                    stamina_cost = move.length * 0.05 * speed_ratio
                    self.metabolic_energy_kJ -= metabolic_cost
                    self.stamina -= stamina_cost
            self.pos = world.block_coords(self.pos + move)
            if update_vars:
                self.last_move = move
                self.speed = move.length
    
    def move_turn(self,direction:float):
            length = max(0,self.speed-Animal.acceleration*self.max_speed)
            if length > 0.1:
                move = Movement(length=length,direction=direction)
                self.last_move = move
                self.speed = length
            else:
                if self.last_move.length < 0.1:
                    self.last_move.length = 0.1
                self.last_move.direction_rad = direction
            self.deg = self.last_move.direction_deg
            self.rad = direction



    def update(self,action:Action):
        """
        Met à jour les variables de l'animal en fonction de son action actuelle.
        """

        # même immobile, l'aniaml consomme de l'énergie (toutes les frames)
        self.metabolic_energy_kJ = max(0, self.metabolic_energy_kJ - self.base_energy_per_frame)

        if self.juvenile and self.get_age()>=self.sex_params.maturity_frames:
            self.juvenile=False
        elif self.get_age()//86400>=self.sex_params.life_expectancy:self.kill()

        # l'animal récupère de la stamina s'il n'est pas à son maximum (inférieur à 70% de sa stamina max) et qu'il ne fait rien
        if action.type == "none":
            self.move(self.last_move,update_vars=False)

        elif action.type == "move":
            if self.current_objective.type == "reproduce" and self.sex==0 and self.current_objective.current_subobjective!=None and self.current_objective.current_subobjective.type=="goto":
                self.move_turn(self.rad-action.movement.direction)
            self.move(action.movement)
            
        elif action.type == "turn":
            self.move_turn(self.rad+Animal.turn*action.angle_mod)

        elif action.type == "eat":
            food:Food = action.food
            if food in Food.instances:
                if isinstance(food.type,FruitType):
                    while (self.metabolic_energy_kJ < self.max_metabolic_energy_kJ and self.stamina < self.max_stamina and food.available_fruits_amount > 0) :
                        nutrients_kJ = food.eat()
                        self.metabolic_energy_kJ = min(self.max_metabolic_energy_kJ, self.metabolic_energy_kJ + nutrients_kJ)
                        self.stamina = min(self.max_stamina, self.stamina + nutrients_kJ)
                else:
                    nutrients_kJ = food.eat()
                    self.metabolic_energy_kJ = min(self.max_metabolic_energy_kJ, self.metabolic_energy_kJ + nutrients_kJ)
                    self.stamina = min(self.max_stamina, self.stamina + nutrients_kJ)
            self.speed = 0

        elif action.type == "socialize":
            for animal in action.animals:
                id = animal.id
                if animal.id in self.memory.affinities.keys():
                    self.memory.affinities[id] = (min(self.memory.affinities[id][0] + 1, 2), ticks())
                else:
                    self.memory.affinities[id] = (1, ticks())
            self.move(self.last_move,update_vars=False)

        elif action.type == "reproduce":
            if (self.metabolic_energy_kJ > self.sex_params.energy_reproduction_kJ and self.stamina > self.sex_params.reproduction_stamina_cost): # vérifie que l'énergie et la stamina sont suffisantes pour que l'animal puisse se reproduire
                self.reproduce(action.animal)
                self.speed = 0
        
        elif action.type == "attack":
            self.attack(action.animal)
            self.move(self.last_move,update_vars=False)
        
        elif action.type=="rest":
            self.time_resting +=1
            move_length = self.last_move.length-self.max_speed*Animal.acceleration
            if move_length > 0:
                self.last_move.length=max(0,self.last_move.length-self.max_speed*Animal.acceleration)
                self.move(self.last_move,False)
            if self.time_resting>=Animal.rest_length:
                self.stamina=min(self.max_stamina,self.stamina+self.species.stamina_recovery_rate*self.time_resting)
                self.hp=min(self.max_hp,self.hp+self.species.stamina_recovery_rate*self.time_resting)
                self.time_resting=0

        else:
            raise TypeError(action.type)
        
        if self.stamina <= 0:
            self.speed *= 0.8
            self.hp -= 10 # l'animal perd de la vie si sa stamina est <= à 0
            self.stamina+=10
            if self.hp<=0:
                #print(f"{self.sex_params.name} est mort de fatigue !")
                self.kill()
        elif self.metabolic_energy_kJ <= self.starvation_threshold :
            #print(f"{self.sex_params.name} est mort de faim !")
            self.kill()
        elif self.hp <= 0:
            #print(f"{self.sex_params.name} est mort de ses blessures !")
            self.kill()
            #print(simulationGraphParam.life)
        self.hp=min(self.hp+0.1,self.max_hp)
    
    def update_hitbox(self):
        self.hitbox = self.get_hitbox()

    def _get_in_view_animals(self)->list[Self]:#Version extrêmement optimisée car fonction appelée souvent
        """
        NE PAS CALL
        """
        results = list()
        for animal in Animal.instances:
            dx,dy=(self.pos[0]-animal.pos[0]),(self.pos[1]-animal.pos[1])
            dist_carre=dx*dx+dy*dy
            if self.view_dist*self.view_dist<dist_carre or dist_carre<1 or animal is self:continue
            d1=self.rad
            d2=math.atan2(dy,dx)
            angle_diff=(d2-d1+math.pi)%(2*math.pi)
            if angle_diff<=self.fov/2 or math.pi*2-self.fov/2<=angle_diff:
                results.append(animal)

        return results

    def _get_in_view_foods(self)->list[Food]:#Version extrêmement optimisée car fonction appelée souvent
        """
        NE PAS CALL
        """
        results = list()
        for food in Food.instances:
            if not food.type.name in self.species.foods:continue
            dx,dy=(self.pos[0]-food.pos[0]),(self.pos[1]-food.pos[1])
            if dx>self.view_dist or dy>self.view_dist:continue
            dist_carre=dx*dx+dy*dy
            if self.view_dist*self.view_dist<dist_carre or dist_carre<1:continue
            d1=self.rad
            d2=math.atan2(dy,dx)
            angle_diff=(d2-d1+math.pi)%(2*math.pi)
            if angle_diff<=self.fov/2 or math.pi*2-self.fov/2<=angle_diff:
                results.append(food)
                self.memory.food_spots.add(food)
        return results

    @property
    def reproduction_will(self)->float:
        for objective in self.objectives:
            if objective.type == "reproduce":
                return objective.importance
        raise AttributeError("Cet animal n'a pas d'objectif reproduce")

    def draw(self,surface:pygame.Surface,zoom:float,ofx:Number,ofy:Number):
        if self.juvenile:
            rotated = pygame.transform.rotate(self.sex_params.current_baby_img,self.deg)
        else:
            rotated = pygame.transform.rotate(self.sex_params.current_img,self.deg)
        rect=rotated.get_rect(center=(self.pos[0]*zoom-ofx,self.pos[1]*zoom-ofy))
        surface.blit(rotated,rect)

    def get_scout_path(self):
        points = []
        last_point=self.pos
        for mod in self.scout_pattern:
            new_point = world.block_coords(last_point + Movement(length=500,direction=math.pi*2*mod+self.rad))
            points.append(new_point)
            last_point=new_point
        return points

    def hit(self,damage:int):
        self.hp-=damage
        if self.hp<=0:
            self.kill()

    def kill(self):
        Animal.instances.remove(self)
        Animal.id_dict.pop(self.id)
        self.count_death()
        Data.animals_dead[self.id]=[self,simparams.time]
        self.dead=True
        if self.species.has_meat:
            self.meat=Food(*self.pos,self.species.food_type)
            self.meat.base_energy = int(self.metabolic_energy_kJ)

    def __eq__(self,other):return other is self or (self.dead and other==None)

    def reproduce(self,other_animal:Self):
        #print(f"{self.sex_params.name} s'est reproduit !")
        self.stamina -= self.sex_params.reproduction_stamina_cost
        self.metabolic_energy_kJ -= self.sex_params.energy_reproduction_kJ
        other_animal.stamina -= self.sex_params.reproduction_stamina_cost
        other_animal.metabolic_energy_kJ -= self.sex_params.energy_reproduction_kJ
        Animal(self,other_animal)

    def attack (self,animal:Self):
        #Mettre un calcul de dégats ici
        animal.hp-=10
    
    def get_sex_name(self):
        if self.sex:return "Male"
        return "Femelle"

    def get_age(self)->int:...
    def count_death(self)->None:...
    def in_water(self)->bool:...