#Projet : The Descent
#Auteurs : Ahmed-Adam REZKALLAH, Noé SAMUEL

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import csv
from environnement.scale import*
from typing import Union
import os,shutil,time

class Data:
    species_display = {
        "Meles meles":"blaireau",
        "Cervus elaphus":"cerf",
        "Gallus gallus domesticus":"coq",
        "Alces alces":"elan",
        "Oryctolagus cuniculus":"lapin",
        "Canis lupus lupus":"loup",
        "Ursus arctos":"ours",
        "Vulpes vulpes":"renard",
        "Sus scrofa":"sanglier"
    }
    time = 0
    sim_type = "Par Défaut"
    animals_born:dict[int,list[object,int]] = {}
    animals_dead:dict[int,list[object,int]] = {}
    colors = ["darkgreen", "darkgray", "brown", "gold","yellow","lightgray", "saddlebrown", "maroon", "orange"]

    @staticmethod
    def display_name(specie:str) -> str:
        return Data.species_display.get(specie,specie)

    @staticmethod
    def species_counts_all_time(data:list[dict[str,object]],species:list[str]) -> dict[str,int]:
        counts = {specie:sum([1 for e in data if e["specie"]==specie]) for specie in species}
        return counts
    
    @staticmethod
    def get_percent(d:dict[str,int])->dict[str:float]:
        tot = sum(d.values())
        
        perc = {c:d[c]*100/tot for c in d}
        return  perc
    
    def global_pie_of_specie(data:list[dict[str,object]],species:list[str],path,title="Proportion des espèces"):
        count = Data.get_percent(Data.species_counts_all_time(data,species))
        res = [[],[]]
        for s in count:
            res[0].append(Data.display_name(s))
            res[1].append(count[s])
            
        Data.draw_species_pie(res[0],res[1],title,path)



    @staticmethod
    def mid_v_per_specie(data,v,species,path):
        values_by_specie = {specie:[] for specie in species}
        for e in data:
            if e["specie"] in species and e[v] not in (None,'','---'):
                try:
                    values_by_specie[e["specie"]].append(float(e[v]))
                except ValueError:
                    pass  #valeurs non numérique ignoré

        means = [sum(vs)/len(vs) if len(vs) > 0 else 0 for vs in values_by_specie.values()]
        labels = [Data.display_name(s) for s in values_by_specie.keys()]
        Data.drawHist(path,"Espèce",f"Moyenne de {v}",labels,means)
        

    @staticmethod
    def assemble_info_by_cat(data:list[dict[str,object]])->dict[str,list[object]]:
        res = {}

        for key in data[0]:
            res[key]=[]
        
        for e in data:
            for key in res:
                res[key].append(e[key])

        return res
    
    @staticmethod
    def get_existence_through_time(data:list[dict[str,object]]):
        return [[True if int(e["birth_time"])<=t and (e["death_time"]=="---" or t<=int(e["death_time"])) else False for e in data] for t in range(Data.time)]

    def get_existence_through_time_by_specie(data:list[dict[str,object]],species:list[str]):
        existence = Data.get_existence_through_time(data)
        res = []
        for i,l in enumerate(existence):
            
            res.append({})
            for specie in species: res[i][specie]=[]
            for animal,exists in zip(data,l):
                if animal["specie"] in species and exists: res[i][animal["specie"]].append(True)
        r = {}
        for specie in species: r[specie]=[]
        for l in res:
            for specie in species:
                r[specie].append(sum(l[specie]))
        return r

    def population_through_time_graph(data:list[dict[str,object]],path):
        d = [sum(e) for e in Data.get_existence_through_time(data)]
        t = [convert(i,"frames","seconds")/(24*3600) for i in range(Data.time)]
        Data.drawGraphs(path,"Temps (jours)","Population",t,(d,"r","population"))

    def spe_population_through_time_graph(pop,path):
        t = [convert(i,"frames","seconds")/(24*3600) for i in range(Data.time)]
        courbes = []
        colors = [c for c in Data.colors]
        for specie in pop:
            label = Data.display_name(specie)
            courbes.append((pop[specie],colors[0],specie))
            colors.append(colors.pop(0))
        Data.drawGraphs(path,"Temps (jours)","Population",t,*courbes)

    @staticmethod
    def draw_all_spe_graph(path):
        tempdir=os.path.abspath(os.sep.join(["data","simulations","csv","temp"]))

        if os.path.isdir(tempdir):
            raise FileExistsError("Impossible d'extraire le fichier, le dossier de stockage temporaire est déjà en cours d'utilisation !")

        os.makedirs(tempdir)
        
        header,data = import_data(path)

        Data.population_through_time_graph(data,os.sep.join([tempdir,"pop_through_time.png"]))
        species = list(set([e["specie"] for e in data]))
        d = Data.get_existence_through_time_by_specie(data,species)
        Data.spe_population_through_time_graph(d,os.sep.join([tempdir,"spe_population_through_time_graph.png"]))

        for param in ["max_energie"]:
            Data.mid_v_per_specie(data,param,species,os.sep.join([tempdir,param+".png"]))
        Data.global_pie_of_specie(data,species,os.sep.join([tempdir,"global_pie_of_specie.png"]))

        Data.birth_death_rate_graph(data, os.sep.join([tempdir,"birth_death.png"]))
        Data.age_distribution(data, os.sep.join([tempdir,"age_distribution.png"]))
        Data.speed_vs_energy(data, os.sep.join([tempdir,"speed_energy.png"]))
        Data.survival_curve(data, os.sep.join([tempdir,"survival.png"]))

        for trait in ["fearful","patient","eater","reproductive","sociable"]:
            Data.personality_distribution(data, trait, os.sep.join([tempdir,f"{trait}.png"]))

    def erase_memory():
        tempdir=os.path.abspath(os.sep.join(["data","simulations","csv","temp"]))

        if os.path.exists(tempdir):
                shutil.rmtree(tempdir)

    @staticmethod
    def draw_species_pie(labels:list[str],v:list[float],title:str,path):
        if sum(v) == 0:
            print("Vide, veuillez mettre des valeurs")
            return

        colors = [Data.colors[i] for i in range(len(labels))]

        plt.figure()
        plt.pie(v,labels=labels,colors=colors,autopct=lambda p:f"{p:.1f}%",startangle=90)
        plt.axis("equal")
        if title:
            plt.title(title)
        if path:
            plt.savefig(path, bbox_inches="tight")
            plt.close()

    @staticmethod
    def birth_death_rate_graph(data, path):
        births = [0]*Data.time
        deaths = [0]*Data.time

        for e in data:
            b = int(e["birth_time"])
            if b < Data.time:
                births[b] += 1
            if e["death_time"] != "---":
                d = int(e["death_time"])
                if d < Data.time:
                    deaths[d] += 1

        t = [convert(i,"frames","seconds")/(24*3600) for i in range(Data.time)]
        Data.drawGraphs(path,"Temps (jours)","Nombre",t,(births,"g","naissances"),(deaths,"r","morts"))

    @staticmethod
    def age_distribution(data, path):
        ages = []
        for e in data:
            try:
                ages.append(float(e["age"]))
            except:
                pass

        plt.figure()
        plt.hist(ages, bins=20, edgecolor="black")
        plt.title("Distribution des âges")
        plt.xlabel("Âge")
        plt.ylabel("Nombre")
        plt.savefig(path)
        plt.close()
    
    @staticmethod
    def speed_vs_energy(data, path):
        speeds = []
        energies = []

        for e in data:
            try:
                speeds.append(float(e["max_speed"]))
                energies.append(float(e["max_energie"]))
            except:
                pass

        plt.figure()
        plt.scatter(speeds, energies, alpha=0.5)
        plt.xlabel("Vitesse max")
        plt.ylabel("Énergie max")
        plt.title("Corrélation vitesse/énergie")
        plt.savefig(path)
        plt.close()

    @staticmethod
    def personality_distribution(data, trait, path):
        values = []
        for e in data:
            try:
                values.append(float(e[trait]))
            except:
                pass

        plt.figure()
        plt.hist(values, bins=20, edgecolor="black")
        plt.title(f"Distribution du trait : {trait}")
        plt.xlabel(trait)
        plt.ylabel("Nombre")
        plt.savefig(path)
        plt.close()

    @staticmethod
    def survival_curve(data, path):
        lifetimes = []

        for e in data:
            try:
                if e["death_time"] != "---":
                    lifetimes.append(int(e["death_time"]) - int(e["birth_time"]))
            except:
                pass

        lifetimes.sort()
        survival = [1 - i/len(lifetimes) for i in range(len(lifetimes))]

        plt.figure()
        plt.plot(lifetimes, survival)
        plt.xlabel("Temps de vie")
        plt.ylabel("Survie (%)")
        plt.title("Courbe de survie")
        plt.savefig(path)
        plt.close()

    @staticmethod
    def trophic_levels_pie(data, categories, path):
        counts = {k:0 for k in categories}

        for e in data:
            specie = e["specie"]
            for cat in categories:
                if specie in categories[cat]:
                    counts[cat]+=1

        labels = list(counts.keys())
        values = list(counts.values())

        Data.draw_species_pie(labels,values,"Niveaux trophiques",path)

    @staticmethod
    def drawHist(fname,x_label,y_label,species,means):
        """
        Crée un histogramme des valeurs moyennes par espèce.
        """
        plt.figure()
        plt.bar(species,means,color=[Data.colors[i] for i in range(len(species))],edgecolor="black")
        plt.title("Moyenne des types par espèce")
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.xticks(rotation=45,ha='right')
        plt.tight_layout()
        plt.savefig(fname)
        plt.close()

    @staticmethod
    def drawGraphs(fname,x_label:str,y_label:str,x_axis:list[int],*graphs:tuple[list[int],str,str]):
        """
        Crée un graph avec plusieurs courbes
        x_axis = valeurs en x (axe des absyces)
        graph = tuple(valeur_de_la_courbe:list,matplotlib_color:str,label_de_la_courbe:str)
        """
        plt.figure()
        for graph in graphs:
            plt.plot(x_axis,graph[0],graph[1],label=graph[2])
        plt.title("Population en fonction du temps")
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.legend(loc='best')
        plt.savefig(fname)
        plt.close()

    @staticmethod
    def shutil_to_permanent():
        tempdir = os.path.abspath(os.path.join("data","simulations","csv","temp"))
        csv_dir = os.path.abspath(os.path.join("data","simulations","csv"))

        if not os.path.exists(tempdir):
            print("temp directory does not exist.")
            return

        permanent_dir = os.path.join(csv_dir,f"sim_export")
        counter = 1
        while os.path.exists(permanent_dir):
            permanent_dir = os.path.join(csv_dir,f"sim_export_{counter}")
            counter += 1

        shutil.copytree(tempdir,permanent_dir)
        print(f"temp copied to: {permanent_dir}")

    @staticmethod
    def export_data(path="data/simulations/csv/Donnees_Derniere_Simu_Analysee.csv"):
        header = ["specie","sex","birth_time","death_time","age","max_stamina","max_energie",'max_health',"max_speed","view_dist","scout_pattern","generation","fearful","patient","eater","reproductive","sociable"]
        animals = []

        for id, l in Data.animals_born.items():
            a = l[0]
            b_time = l[1]

            if id in Data.animals_dead:
                d_time = Data.animals_dead[id][1]

                animals.append({"specie":a.species.scientific_name,
                                "sex":a.get_sex_name(),
                                "birth_time":b_time,
                                "death_time":d_time,
                                "age":d_time-b_time,
                                "max_stamina":a.max_stamina,
                                "max_energie":a.max_metabolic_energy_kJ,
                                'max_health':a.max_hp,
                                "max_speed":a.max_speed,
                                "view_dist":a.view_dist,
                                "scout_pattern":a.scout_pattern,
                                "generation":a.gen,
                                "fearful":a.personnality["fearful"],
                                "patient":a.personnality["patient"],
                                "eater":a.personnality["eater"],
                                "reproductive":a.personnality["reproductive"],
                                "sociable":a.personnality["sociable"]})
            else:
                animals.append({"specie":a.species.scientific_name,
                                "sex":a.get_sex_name(),
                                "birth_time":b_time,
                                "death_time":"---",
                                "age":Data.time-b_time,
                                "max_stamina":a.max_stamina,
                                "max_energie":a.max_metabolic_energy_kJ,
                                'max_health':a.max_hp,
                                "max_speed":a.max_speed,
                                "view_dist":a.view_dist,
                                "scout_pattern":a.scout_pattern,
                                "generation":a.gen,
                                "fearful":a.personnality["fearful"],
                                "patient":a.personnality["patient"],
                                "eater":a.personnality["eater"],
                                "reproductive":a.personnality["reproductive"],
                                "sociable":a.personnality["sociable"]})
        export_data(path,header,animals)


def export_data(path:str,header:list[str],data:list[dict[str,object]]):
    with open(path,"w",newline="") as f:
        write = csv.DictWriter(f,fieldnames=header,delimiter=";")
        write.writeheader()
        write.writerows(data)

def import_data(path,delimiter=";")->tuple[list[str],list[list[str]]]:
    with open(path,"r") as f:
        csv_reader = csv.DictReader(f,delimiter=delimiter)
        header = csv_reader.fieldnames
        data = [row for row in csv_reader]

        return [header,data]

def list_of_dict_to_list(ld):return [[d[k] for k in d] for d in ld]

if __name__ == '__main__':
    name = "truc"
    path = f"data/simulations/csv/{name}.csv"
    header,data = import_data(path)
    Data.time = 10000
    Data.population_through_time_graph(data,"data/simulations/csv.png")
    species = sorted(list(set([e["specie"] for e in data])))
    print(species)
    d = Data.get_existence_through_time_by_specie(data,species)
    Data.spe_population_through_time_graph(d,"data/simulations/csv.png")
    Data.mid_v_per_specie(data,"max_energie",species)
    Data.global_pie_of_specie(data,species)