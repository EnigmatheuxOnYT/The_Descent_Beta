#Projet : The Descent
#Auteurs : Ahmed-Adam REZKALLAH, Noé SAMUEL

from utils import *
if os_name == "Windows":
        from loading_screen_win import LoadingScreen
        LoadingScreen([LOADING_MENU]).run()
elif os_name == "Darwin":
    from loading_screen_mac import *
from menu import Menu
from sim_recap import SimRecap
from simulation import Simulation
from file_type_manager import FileTypeAssignScreen
#importation des modules pythons

class Main(Runable): #Classe générale du simulateur 
    
    def __init__ (self): #Déclaration des variables générales de la classe
        self.menu=Menu()
        self.simulation = Simulation()
        self.sim_recap = SimRecap()
        self.state = LOADING_MENU

    def update (self): #Mise à jour des variables et de l'etat du simulateur
        if self.state in MENU_STATES:
            self.menu.run()
        elif self.state in SIMULATION_STATES:
            self.simulation.run()
        elif self.state in GENERIC_RUNNING_STATES:
            if self.state == IN_SIM_RECAP:
                self.sim_recap.run()
            else:
                print(self.state)
                print(f"Etat {self.state} non pris en compte, redémarrage au menu.")
                self.state = LOADING_MENU
    
    def run(self): #Lancement de la boucle principale du jeu
        ftas = FileTypeAssignScreen()
        self.state = FILETYPES_ASSIGNATION
        ftas.run(auto_open=True)

        if os_name == "Darwin":
            stop_event.set() #pr l'écran de chargement
            loader.join()

        self.run_fcts(RUNNING_STATES,self.update)
        quit()


if __name__ == "__main__":
    if os_name == "Darwin":
        #à mettre avant le code qu'on veut run en background
        mp.set_start_method("spawn",force=True)
        stop_event = mp.Event() #stop_event.is_set <=> False
        loader = mp.Process(target=loading_process,args=tuple([stop_event]),daemon=True) #pcq args veut un tuple; l'autre option c (stop_event,) mais je trouve moins compréhensible
        loader.start() #on lance la fenêtre pygame de chargement
        #puisque le tmps de chargement au dépard est méga court sur mac on voit juste la fen^tre qui s'ouvre et ce ferme avant le deb mais si vous rajoutez un truc lent on le voit bien (par ex le time.sleep(30) que j'ai mis en comm.)

    simulateur = Main()
    simulateur.run()