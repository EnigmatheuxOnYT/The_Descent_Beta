#Projet : The Descent
#Auteurs : Ahmed-Adam REZKALLAH, Noé SAMUEL

"""
Module gérant les interactions avec les fichiers externes
"""
from utils import pygame,Global,get_path
from utils import version as _app_version
app_version = _app_version[:3]
del _app_version
import traceback
from csv_export import Data
from file_dialog import PROJECT_ROOT,Path

loaded_file = None
is_loaded_file_version_compatible = None

import json

def add_path(info:dict):
    path=get_path("data/simulations/info_sim_hist.json")
    f:dict[list[dict]]=load_sim_env(path)
    f["save_files"].append(info)
    with open(path,'w') as n:
        json.dump(f,n)

def load_sim_env(path:str)->dict[str,int]:
    with open(get_path(path)) as f:
        return json.load(f)
    
def make_simstat(name:str,params:dict[str,dict|int]):
    file = {
        "app_version":list(app_version),
        "params":params
    }
    path="data/simulations/simstat/"+name+".simstat"
    with open(get_path(path),"w") as f:
        return json.dump(file,f)

import pickle

def make_pickle(obj,file):
    with open(get_path(file), 'wb') as f:
        pickle.dump(obj,f)
        f.close()

def read_pickle(file):
    with open(get_path(file), 'rb') as f:
        try:
            obj= pickle.load(f)
        except Exception as e:print(e)
    return obj


def test_sim_path(path:str):
        expected_keys1 = ["width","height","food_amount","animal_amount"]
        expected_keys2 = ["app_version","params"]
        if not ((len(path)>=8 and path[-8:]==".simstat") or (len(path)>=5 and path[-5:]==".json")) :return False
        content = load_sim_env(path)
        return isinstance(content,dict) and (set(expected_keys1).intersection(content.keys())==set(content.keys()) or set(expected_keys2).intersection(content.keys())==set(content.keys()))

import environnement.world as world

def load_json_file(filename):
    global loaded_file
    if test_sim_path(filename):
        world.load_sim_params(load_sim_env(filename))
        world.loaded_data = None
        loaded_file = None
        return True
    if Global.devmode:
        print("LE FICHIER CHARGE EST INCORRECT ! TU T TROMPE DE FICHIER OU DE METHODE DE CHARGEMENT !")
    return False

def load_default_sim():
    global loaded_file
    world.load_sim_params(load_sim_env(os.sep.join(["data","simulations","default","default_sim.json"])))
    world.loaded_data = None
    loaded_file = None


import time,os,zipfile,shutil
tempdir=os.path.abspath(os.sep.join(["data","simulations","temp"]))
envdir=os.path.join(tempdir,"env")
foodtypesdir=os.path.join(tempdir,"foodtypes")
animaltypesdir=os.path.join(tempdir,"animaltypes")
animalsdir=os.path.join(tempdir,"animals")
csv_memory_dir=os.path.join(tempdir,"csv_memory")


def save_sim_file(env,
                  foodtypes:list,
                  foods:list,
                  animaltypes:list,
                  animals:list,
                  name=None,
                  ):
    Data.export_data()

    if os.path.isdir(tempdir):
        raise FileExistsError("Impossible d'enregistrer le fichier, le dossier de stockage temporaire est déjà en cours d'utilisation !")

    global loaded_file
    if loaded_file:zipname=loaded_file
    else:
        if not name:
            now = time.gmtime(time.time()-time.timezone)
            name = "Simulation du "+str(now.tm_mday)+"-"+str(now.tm_mon)+"-"+str(now.tm_year)+", "+str(now.tm_hour)+"h"+str(now.tm_min)
        path=os.path.abspath(os.sep.join(["data","simulations","sim"]))
        zipname= os.sep.join([path,name+".sim"])
    
    sucess = False

    def find_type(obj, target_type, path="root", seen=None):
        """
        Généré par ia pour régler les surfaces
        """
        if seen is None:
            seen = set()

        oid = id(obj)
        if oid in seen:
            return
        seen.add(oid)

        if isinstance(obj, target_type):
            raise TypeError(f"Type non pickleable {target_type} à {path}")

        # Containers
        if isinstance(obj, dict):
            for k, v in obj.items():
                find_type(k, target_type, f"{path}[key={repr(k)}]", seen)
                find_type(v, target_type, f"{path}[{repr(k)}]", seen)

        elif isinstance(obj, (list, tuple, set, frozenset)):
            for i, v in enumerate(obj):
                find_type(v, target_type, f"{path}[{i}]", seen)

        # Objects
        elif hasattr(obj, "__dict__"):
            for attr, val in obj.__dict__.items():
                find_type(val, target_type, f"{path}.{attr}", seen)

        # Slots
        if hasattr(type(obj), "__slots__"):
            for cls in type(obj).__mro__:
                if hasattr(cls, "__slots__"):
                    slots = cls.__slots__
                    if isinstance(slots, str):
                        slots = [slots]
                    for slot in slots:
                        if hasattr(obj, slot):
                            find_type(getattr(obj, slot), target_type, f"{path}.{slot}", seen)

    try:
        os.makedirs(foodtypesdir)
        os.mkdir(envdir)
        os.mkdir(animaltypesdir)
        os.mkdir(animalsdir)
        os.mkdir(csv_memory_dir)


        pygame.image.save(env._surface_bg,os.path.join(envdir,"bg.png"))
        env._pack_for_pickle()
        find_type(env,pygame.Surface)

        for foodtype in foodtypes:
            img_dir=os.path.join(foodtypesdir,foodtype.name+".png")
            pygame.image.save(foodtype._img,img_dir)
            if hasattr(foodtype,"_fruit_img"):
                fruit_img_dir=os.path.join(foodtypesdir,foodtype.name+"-fruit"+".png")
                pygame.image.save(foodtype._fruit_img,fruit_img_dir)
            foodtype._pack_for_pickle()
            find_type(foodtype,pygame.Surface)

        for food in foods:
            food._pack_for_pickle()
            find_type(food,pygame.Surface)

        for animaltype in animaltypes:
            img_dir=os.path.join(animaltypesdir,animaltype.name_shortcut)
            pygame.image.save(animaltype.f_params._img,img_dir+"-female.png")
            pygame.image.save(animaltype.m_params._img,img_dir+"-male.png")
            pygame.image.save(animaltype.f_params._baby_img,img_dir+"-female-baby.png")
            pygame.image.save(animaltype.m_params._baby_img,img_dir+"-male-baby.png")
            animaltype._pack_for_pickle()
            find_type(animaltype,pygame.Surface)

        for animal in animals:
            animal._pack_for_pickle()
            find_type(animal,pygame.Surface)

        for animal_id in Data.animals_dead:
            Data.animals_dead[animal_id][0]._pack_for_pickle()
            try:
                find_type({animal_id:Data.animals_dead[animal_id][0]},pygame.Surface)
            except Exception as e:
                print("-----------------------------------------")
                print()
                print("Envoyez ça sur le discord svp :")
                print(Data.animals_dead[animal_id][0].sex_params.name)
                print()
                print("------------------------------------------")
                raise e
                    
        data={
            "app_version":app_version,
            "environnement":env,
            "foodtypes":foodtypes,
            "foods":foods,
            "animaltypes":animaltypes,
            "animals":animals,
            "csv_memory":{
                "live":Data.animals_born,
                "dead":Data.animals_dead,
                "type":Data.sim_type
            },
        }
        make_pickle(data,os.path.join(tempdir,"pickle_data.pkl"))

        with zipfile.ZipFile(zipname,"w") as file:
            for dirname, subdirs, files in os.walk(tempdir):
                for filename in files:
                    file.write(os.path.join(dirname, filename),os.path.relpath(os.path.join(dirname, filename),tempdir))
        sucess = True
        relative_path = Path(zipname).relative_to(PROJECT_ROOT)
        add_path({"path":relative_path.as_posix(),
                  "name":name,"Nombre d'animaux":len(animals),
                  "Nombre d'espèces":len({animal.species for animal in animals}),
                  "Temps (j)":Data.time,
                  "Type de simulation":Data.sim_type})
        
    except Exception as e:
        if Global.devmode:
            print(traceback.format_exc())
    finally:
        shutil.rmtree(tempdir)
    return sucess

def read_sim_file(filename:str):
    if os.path.isdir(tempdir):
        raise FileExistsError("Impossible d'extraire le fichier, le dossier de stockage temporaire est déjà en cours d'utilisation !")
    
    global loaded_file,is_loaded_file_version_compatible
    loaded_file=os.path.abspath(filename)
    try:
        with zipfile.ZipFile(filename,"r") as file:
            file.extractall(tempdir)
        return read_pickle(os.path.join(tempdir,"pickle_data.pkl"))
    except Exception as e:
        if Global.devmode:
            print("LE FICHIER CHARGE EST INCORRECT ! Erreur précise :")
            print(e.__class__.__name__,e)
        return False
    finally:
        if os.path.exists(tempdir):
            shutil.rmtree(tempdir)

def load_sim_file(filename:str):
    if os.path.isdir(tempdir):
        raise FileExistsError("Impossible d'extraire le fichier, le dossier de stockage temporaire est déjà en cours d'utilisation !")
    
    global loaded_file,is_loaded_file_version_compatible
    loaded_file=os.path.abspath(filename)
    try:
        with zipfile.ZipFile(filename,"r") as file:
            file.extractall(tempdir)
        
        pickle_data = read_pickle(os.path.join(tempdir,"pickle_data.pkl"))
        env=pickle_data["environnement"]
        foodtypes=pickle_data["foodtypes"]
        foods=pickle_data["foods"]
        animaltypes=pickle_data["animaltypes"]
        animals=pickle_data["animals"]
        try:
            born_animals=pickle_data["csv_memory"]["live"]
            dead_animals=pickle_data["csv_memory"]["dead"]
        except Exception as e:
            born_animals={}
            dead_animals={}
            print("Une erreur s'est produite dans la récupération des informations csv.")
            print(e)

        try:
            comming_version=pickle_data["app_version"][:3]
            if app_version == comming_version:
                is_loaded_file_version_compatible = True
            elif app_version > comming_version:
                print("Fichier prevenant d'une ancienne version, récupération incertaine...")
                is_loaded_file_version_compatible = False
            elif app_version < comming_version:
                print("Fichier prevenant d'une version postérieure, récupération incertaine...")
                is_loaded_file_version_compatible = False
        except:
            print("Fichier prevenant d'une ancienne version, récupération incertaine...")
            is_loaded_file_version_compatible = False
        
        env_bg = pygame.image.load(os.path.join(envdir,"bg.png")).convert_alpha()
        env._unpack_from_pickle(env_bg)

        for foodtype in foodtypes:
            img=pygame.image.load(os.path.join(foodtypesdir,foodtype.name+".png")).convert_alpha()
            if hasattr(foodtype,"_fruit_img"):
                fruit_img=pygame.image.load(os.path.join(foodtypesdir,foodtype.name+"-fruit"+".png")).convert_alpha()
                foodtype._unpack_from_pickle(img,fruit_img)
            else:
                foodtype._unpack_from_pickle(img)
        foodtype.__class__._load_list(foodtypes) #Fix de niveau "crime contre le codage"

        for food in foods:
            food._unpack_from_pickle()
        
        for animaltype in animaltypes:
            f_img = pygame.image.load(os.path.join(animaltypesdir,animaltype.name_shortcut+"-female.png")).convert_alpha()
            m_img=pygame.image.load(os.path.join(animaltypesdir,animaltype.name_shortcut+"-male.png")).convert_alpha()
            fb_img = pygame.image.load(os.path.join(animaltypesdir,animaltype.name_shortcut+"-female-baby.png")).convert_alpha()
            mb_img=pygame.image.load(os.path.join(animaltypesdir,animaltype.name_shortcut+"-male-baby.png")).convert_alpha()
            animaltype._unpack_from_pickle(m_img,f_img,mb_img,fb_img)
        animaltype.__class__._load_list(animaltypes) #Fix criminel : le retour

        for animal in animals:
            animal._unpack_from_pickle()
        for animal_id in dead_animals:
            dead_animals[animal_id][0]._unpack_from_pickle()

        world.loaded_data = {"env":env,
                             "foodtypes":foodtypes,
                             "foods":foods,
                             "animaltypes":animaltypes,
                             "animals":animals
                             }
        Data.animals_born=born_animals
        Data.animals_dead=dead_animals
        Data.sim_type = pickle_data["csv_memory"]["type"]
        return True
    except Exception as e:
        world.loaded_data=None
        if Global.devmode:
            print("LE FICHIER CHARGE EST INCORRECT ! Erreur précise :")
            print(e.__class__.__name__,e)
        return False
    finally:
        if os.path.exists(tempdir):
            shutil.rmtree(tempdir)


def is_correct_file_name(txt:str)->bool:
    if len(txt)>50 or len(txt)<2 or txt[0]==" ":return False
    for char in txt:
        if char not in "azertyuiopqsdfghjklmwxcvbnAZERTYUIOPQSDFGHJKLMWXCVBN1234567890_ ":
            return False
    return True

def create_animal_dir(folder_name:str,file_name:str)->bool:
    placeholder = pygame.image.load("data/assets/placeholders/placeholder_animaux.png")
    folder=os.sep.join(["data","assets","animals",folder_name])
    if os.path.exists(folder):
        print(f"Création de placeholder pour {file_name} échouée, dossier déjà occupé")
        return False
    os.mkdir(folder)
    pygame.image.save(placeholder,os.sep.join([folder,file_name+"_Idle_1_V2.png"]))
    print(f"Placeholder pour {file_name} créé.")
    return True

if __name__=="__main__":
    pass
