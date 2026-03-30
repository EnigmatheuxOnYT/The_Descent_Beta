#Projet : The Descent
#Auteurs : Ahmed-Adam REZKALLAH, Noé SAMUEL


#importation des modules pythons
from utils import *
from random import random
import environnement.world as world
from environnement.objects import AnimalType,FoodType,Animal,Food,get_simparams,JsonHitbox,FruitType
from environnement.ia.main import simulate_action,update_behaviour
from environnement.geometry import Triangle,Hitbox


class Environnement:
    """
    Génère la nourriture, les animaux et la carte
    """

    placeholder_bg = pygame.image.load("data/assets/placeholders/placeholder_sim_bg.png")

    def __init__(self):
        self.width:int
        self.height:int
        self.water:list[Hitbox]
        self.foods:dict
        self.animals:dict
        self.loaded = False

        self.reduce_animals_n_foods = False
        self.animal_point_size = 5
        self.food_point_size=3

        self.ticks_passed = 0
        self.dead_animals = 0
        self.alive_animals = 0
        
        self._surface_bg:pygame.Surface

        self.current_surf:pygame.Surface
        Environnement.reset_entities()
        get_simparams(self)

        def count_death(animal):
            self.dead_animals+=1
            self.alive_animals-=1
        Animal.count_death=count_death

        def in_water(animal:Animal):
            return animal.collide(self.water)
        Animal.in_water=in_water

    def load_params(self):

        if not world.has_data:raise RuntimeError("Chargement de paramètres de simulation avant assignation")
        Environnement.reset_entities()
        self._assign_world_params(**world.params)
        self.generate_food()
        self.generate_animals()
        get_simparams(self)
        self.loaded=True

    def _assign_world_params(self,
                            width:int,
                            height:int,
                            bg:str,
                            water:JsonHitbox,
                            foods:dict[str,int],
                            animals:dict[str,int],
                            **upper_versions_args):
        self.width=width
        self.height=height
        self.foods=foods
        self.animals=animals
        try:
            self._surface_bg = pygame.image.load(f"data/assets/sim_bgs/{bg}.png")
            if not self._surface_bg.get_size()==(width,height):
                print("Sprite de taille incorrecte, utilisation d'un fond placeholder")
                self._surface_bg=pygame.transform.scale(self._surface_bg,(width,height))
        except FileNotFoundError:
            print("Sprite manquant pour le fond de simulation")
            self._surface_bg=pygame.transform.scale(Environnement.placeholder_bg,(width,height))
        self.current_surf=self._surface_bg.copy()
        self.water=list()
        for points in water:
            self.water.append(Triangle(*points))
        self.water = water
    
    @staticmethod
    def reset_entities():
        FoodType._clear_dict()
        Food._clear_list()
        AnimalType._clear_dict()
        Animal._clear_list()

    def generate_food(self):#crée les instances de nourriture
        food_types = list(self.foods.keys())
        for _food_type in food_types:
            FoodType.from_file(_food_type)
            for _ in range(self.foods[_food_type]):Food.generate(_food_type)
    
    def generate_animals(self):#crée les instances animal
        animal_types = list(self.animals.keys())
        for _animal_type in animal_types:
            AnimalType(_animal_type)
            for _ in range(self.animals[_animal_type]):Animal.generate(_animal_type)

    def update(self):#permet de faire avancer la simulation
        
        for animal in Animal.instances:
            update_behaviour(animal)
            animal.update(simulate_action(animal))

    
    def draw(self,screen:pygame.Surface,camx:Number,camy:Number,cam_rect:pygame.Rect,zoom):
        self.draw_bg(screen,camx,camy)
        if self.reduce_animals_n_foods:
            f_point_size = self.food_point_size
            a_point_size = self.animal_point_size
            for food in Food.instances:
                if cam_rect.collidepoint(food.pos):
                    newpos=(food.pos[0]*zoom-camx,food.pos[1]*zoom-camy)
                    pygame.draw.circle(screen,food.type.reduced_to_point_color,newpos,f_point_size)
            for animal in Animal.instances:
                if cam_rect.collidepoint(animal.pos):
                    newpos=(animal.pos[0]*zoom-camx,animal.pos[1]*zoom-camy)
                    pygame.draw.circle(screen,animal.species.reduced_to_point_color,newpos,a_point_size)
        else:
            for food in Food.instances:
                if cam_rect.collidepoint(food.pos):
                    food.draw(screen,zoom,camx,camy)#dessine la nourriture
            for animal in Animal.instances:
                if cam_rect.collidepoint(animal.pos):
                    animal.draw(screen,zoom,camx,camy)#dessine les animaux
    
    def rescale_surf(self,new_zoom):
        self.current_surf = pygame.transform.scale_by(self._surface_bg,new_zoom)
    
    def draw_bg(self,screen:pygame.Surface,camx,camy):
        screen.blit(self.current_surf,(-camx,-camy))
    
    def point_in_water(self,p:Point):
        for hb in self.water:
            for t in hb:
                if t.collidepoint(p):return True
        return False
    
    def _pack_for_pickle(self):
        self._surface_bg=None
        self.current_surf=None

    def _unpack_from_pickle(self,bg):
        self._surface_bg = bg
        self.current_surf = bg
        get_simparams(self)
    
    def _reassign_world_vars(self):
        world.width,world.height = self.width,self.height
    
    def _reassign_objects_funcs(self):
        get_simparams(self)

        def count_death(animal):
            self.dead_animals+=1
            self.alive_animals-=1
        Animal.count_death=count_death

        def in_water(animal:Animal):
            return animal.collide(self.water)
        Animal.in_water=in_water
    
    @property
    def time(self):return self.ticks_passed
    @time.setter
    def time(self,value):self.ticks_passed=value