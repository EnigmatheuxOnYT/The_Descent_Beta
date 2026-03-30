#Projet : The Descent
#Auteurs : Ahmed-Adam REZKALLAH, Noé SAMUEL, Clément Roux--Bénabou

#importation des modules pythons
from utils import *
from environnement.main import Environnement,Animal,Food,FoodType,AnimalType,FruitType
import environnement.world as world
#from graph import *
from file_loader import is_correct_file_name,save_sim_file,load_default_sim,Data
import file_loader as f_ld
from text_input import TextInput
from environnement.scale import*
from environnement.ia.main import update_behaviour,simulate_action

class Simulation(Runable):
    """
    Gère la simulation
    """
    
    point_reduced_zoom = 0.2 #Zoom minimal avant que les animaux et plantes soient transformés en points
    max_zoom = 1.5 #Zoom maximal
    speed = 1 #Vitesse de la simulation (une vitesse trop élevée peut causer des soucis d'optimisation)
    playing = True #0 si pause sinon 1

    def __init__(self):
        """
        Initialise la simulation
        """
        def pause_unpause():
            Simulation.playing = not Simulation.playing
        def save():
            Data.time = self.env.ticks_passed
            foodtypes_lst=list(FoodType.instances.values())
            animaltypes_lst=list(AnimalType.instances_dict.values())
            
            if not f_ld.loaded_file:
                name = TextInput("",is_correct_file_name)
                if not name:
                    return
                newname = ""
                for char in name:
                    if char == " ":
                        newname = newname+"_"
                    else:
                        newname = newname+char
                name=newname
            else:name=f_ld.loaded_file
            sucess = save_sim_file(self.env,foodtypes_lst,Food.instances,animaltypes_lst,Animal.instances,name)
            if not sucess:
                print("Une erreur s'est produite durant la sauvegarde...")
            quit_sim()
                
        def quit_sim():
            self.state=LOADING_MENU
        def cancel_exit():
            self.state=IN_SIMULATION
        
        hide_infos_surf = fonts.F20(f"Appuyer sur {get_btn_name(self.keybinds['switch_overlay']).capitalize()} pour cacher l'affichage")
        self.hide_infos_display = SurfDisplay(hide_infos_surf,(640,680))

        followed_animal_surf_bg = SurfDisplay("menu/Fond_Affichage_Infos_Animal",(1050,400))
        followed_fruit_surf_bg = SurfDisplay("menu/Fond_Affichage_Infos_Plante",(1050,400))
        
        time_bg = pygame.image.load("data/assets/menu/Bouton_Menu_JourEtHeure.png").convert_alpha()
        time_disp = SurfDisplay(time_bg,time_bg.get_rect(topleft=(12,22)))
        time_rect=pygame.Rect(26,39,0,0)



        self.to_update = list()
        self.to_update_len = 0
        self.to_update_index=0
        self.to_update_amount = 0

        def get_current_surfs():
            total = list()
            if self.state == IN_SIMULATION and self.display_overlay:
                total.append(time_disp)
                total.append(SurfDisplay(self.get_time_info_surf(),time_rect))
                w = convert(self.env.ticks_passed,"frames","time_format")
                h=w["h"]
                if h<7 or h>=22:
                    total.append(self.night_disp)
                else:
                    total.append(self.day_disp)
                if self.state == IN_SIMULATION:
                    total.append(self.hide_infos_display)
                    if self.show_followed_obj_info:
                        if self.followed_type == 1:
                            total.append(followed_animal_surf_bg)
                            total = total + self.followed_animal_info_displays
                        elif self.followed_type == 2 and type(self.followed_obj.type) == FruitType:
                            total.append(followed_fruit_surf_bg)
                            total = total+self.followed_food_info_displays
            if self.state in PANEL_STATES:
                total.append(self.panel_bgs[self.state])
                if self.state == IN_PANEL_SETTINGS:
                    if self.currently_rebinding!=None:
                        total.append(self.settings_rebind_hover_displays[self.currently_rebinding][1])
                    else:
                        for keybind in self.settings_rebind_rects:
                            if keybind[1].collidepoint(pygame.mouse.get_pos()):
                                total.append(self.settings_rebind_hover_displays[keybind[0]][0])
                total = total + self.panel_displays[self.state]
                total.append(time_disp)
                total.append(SurfDisplay(self.get_time_info_surf(),time_rect))
                w = convert(self.env.ticks_passed,"frames","time_format")
                h=w["h"]
                if h<7 or h>=22:
                    total.append(self.night_disp)
                else:
                    total.append(self.day_disp)
            return total

        def get_current_buttons():
            total = list()
            if self.display_overlay and self.state == IN_SIMULATION:
                if not Simulation.playing:
                    total.append(speed_btns_clicked[0])
                    total.append(speed_btns_normal[1])
                    total.append(speed_btns_normal[2])
                    total.append(speed_btns_normal[5])
                    total.append(speed_btns_normal[10])
                else:
                    total.append(speed_btns_normal[0])
                    if Simulation.speed == 1:
                        total.append(speed_btns_clicked[1])
                    else:
                        total.append(speed_btns_normal[1])
                    if Simulation.speed == 2:
                        total.append(speed_btns_clicked[2])
                    else:
                        total.append(speed_btns_normal[2])
                    if Simulation.speed == 5:
                        total.append(speed_btns_clicked[5])
                    else:
                        total.append(speed_btns_normal[5])
                    if Simulation.speed == 10:
                        total.append(speed_btns_clicked[10])
                    else:
                        total.append(speed_btns_normal[10])
                if self.followed_type==1 or (self.followed_type==2 and type(self.followed_obj.type)==FruitType):
                    total.append(self.close_info_button)
                total.append(config_panel_button)
            if self.state in PANEL_STATES:
                total+=self.panel_buttons[self.state]
            return total
                

        speed_btns_normal = {
            0:Button((47.5,662.5),"menu/Bouton_Menu_VitesseStop",pause_unpause),
            1:Button((112.5,662.5),"menu/Bouton_Menu_VitesseX1",lambda:Simulation.change_speed(1)),
            2:Button((177.5,662.5),"menu/Bouton_Menu_VitesseX2",lambda:Simulation.change_speed(2)),
            5:Button((242.5,662.5),"menu/Bouton_Menu_VitesseX5",lambda:Simulation.change_speed(5)),
            10:Button((312.5,662.5),"menu/Bouton_Menu_VitesseX10",lambda:Simulation.change_speed(10))
        }
        speed_btns_clicked = {
            0:Button((47.5,667.5),"menu/Bouton_Menu_VitesseStop_Clique",pause_unpause),
            1:Button((112.5,667.5),"menu/Bouton_Menu_VitesseX1_Clique",lambda:Simulation.change_speed(1)),
            2:Button((177.5,667.5),"menu/Bouton_Menu_VitesseX2_Clique",lambda:Simulation.change_speed(2)),
            5:Button((242.5,667.5),"menu/Bouton_Menu_VitesseX5_Clique",lambda:Simulation.change_speed(5)),
            10:Button((312.5,667.5),"menu/Bouton_Menu_VitesseX10_Clique",lambda:Simulation.change_speed(10))
        }

        def change_to(state):
            def func():self.state = state
            return func

        def change_to_panel_settings():
            self.state=IN_PANEL_STATS
            self.update_panel_stats()
        
        def toggle_hitbox():
            Settings.advanced_display["hitbox"] = not Settings.advanced_display["hitbox"]
            Settings.save()
        def toggle_path():
            Settings.advanced_display["path"] = not Settings.advanced_display["path"]
            Settings.save()
        def toggle_speed_vect():
            Settings.advanced_display["speed_vect"] = not Settings.advanced_display["speed_vect"]
            Settings.save()
        def toggle_fov():
            Settings.advanced_display["fov"] = not Settings.advanced_display["fov"]
            Settings.save()
        
        config_panel_button = Button((1220,60),"menu/Bouton_Menu_Options",change_to(IN_PANEL_MAIN))
        panel_back_button = Button((640,570),"menu/Bouton_Menu_Retour",change_to(IN_PANEL_MAIN))

        self.panel_bgs:dict[GameState,SurfDisplay]={
            IN_PANEL_MAIN:SurfDisplay("menu/Fond_Menu_General",(640,375)),
            IN_PANEL_ADV:SurfDisplay("menu/Fond_Menu_AffichageAvance",(640,375)),
            IN_PANEL_STATS:SurfDisplay("menu/Fond_Menu_Statistiques",(640,375)),
            IN_PANEL_SETTINGS:SurfDisplay("menu/Fond_Menu_Parametres",(640,375)),
            IN_PANEL_QUIT:SurfDisplay("menu/Fond_Menu_PopUpSauvegarde",(640,360)),
            IN_PANEL_END:SurfDisplay("menu/Fond_Menu_PopUpResultatsSimu",(640,360)),
        }

        self.env = Environnement()
        self.env.ticks_passed=0
        def special_change_to(state):
            def func():
                Data.time = self.env.ticks_passed
                Data.export_data()
                change_to(state)()
            return func

        self.panel_buttons:dict[GameState,list[Button]] = {
            IN_PANEL_MAIN:[
                Button((640,240),"menu/Bouton_Menu_AffichageAvance",change_to(IN_PANEL_ADV)),
                Button((640,323),"menu/Bouton_Menu_Statistiques",change_to_panel_settings),
                Button((640,406),"menu/Bouton_Menu_Parametres",change_to(IN_PANEL_SETTINGS)),
                Button((640,489),"menu/Bouton_Menu_AnalyserSimulation",change_to(IN_PANEL_END)),
                Button((640,570),"menu/Bouton_Menu_MenuPrincipal",change_to(IN_PANEL_QUIT)),
                Button((775,160),"menu/Bouton_Menu_Croix",change_to(IN_SIMULATION))
            ],
            IN_PANEL_ADV:[
                panel_back_button,
                Checkbox((520,313),toggle_hitbox,pygame.Rect(485,283,275,57),starting_status=Settings.advanced_display["hitbox"]),
                Checkbox((520,370),toggle_path,pygame.Rect(485,340,275,57),starting_status=Settings.advanced_display["path"]),
                Checkbox((520,427),toggle_speed_vect,pygame.Rect(485,397,275,57),starting_status=Settings.advanced_display["speed_vect"]),
                Checkbox((520,484),toggle_fov,pygame.Rect(485,454,275,57),starting_status=Settings.advanced_display["fov"])
            ],
            IN_PANEL_STATS:[
                panel_back_button
            ],
            IN_PANEL_SETTINGS:[
                panel_back_button
            ],
            IN_PANEL_QUIT:[
                Button((640,345),"menu/Bouton_Menu_Sauvegarder",save),
                Button((640,425),"menu/Bouton_Menu_NePasSauvegarder",quit_sim),
                Button((640,505),"menu/Bouton_Menu_Annuler",change_to(IN_PANEL_MAIN))
            ],
            IN_PANEL_END:[
                Button((640,390),"menu/Bouton_Menu_Oui",special_change_to(IN_SIM_RECAP)),
                Button((640,480),"menu/Bouton_Menu_Non",change_to(IN_PANEL_MAIN))
            ]
        }

        self.panel_displays:dict[GameState,list[SurfDisplay]] = {
            IN_PANEL_MAIN:[
            ],
            IN_PANEL_ADV:[
            ],
            IN_PANEL_STATS:[
                SurfDisplay(fonts.F20("Nombre d'animaux en vie : 0"),pygame.Rect(490,270,0,0)),
                SurfDisplay(fonts.F20("Nombre d'animaux morts : 0"),pygame.Rect(490,320,0,0)),
                SurfDisplay(fonts.F20("Nombre d'espèces : 0"),pygame.Rect(490,370,0,0)),
                SurfDisplay(fonts.F20("Temps simulé : 0"),pygame.Rect(490,420,0,0)),
                SurfDisplay(fonts.F20("Espèce la plus développée : 0"),pygame.Rect(490,470,0,0)),
            ],
            IN_PANEL_SETTINGS:[
                SurfDisplay(fonts.F20(get_btn_name(self.keybinds["quit"])),pygame.Rect(733,282,0,0)),
                SurfDisplay(fonts.F20(get_btn_name(self.keybinds["fullscreen"])),pygame.Rect(700,339,0,0)),
                SurfDisplay(fonts.F20(get_btn_name(self.keybinds["switch_overlay"])),pygame.Rect(684,403,0,0)),
                SurfDisplay(fonts.F20(get_btn_name(self.keybinds["pause"])),pygame.Rect(694,464,0,0))
            ],
            IN_PANEL_QUIT:[
            ],
            IN_PANEL_END:[
            ]
        }

        self.settings_rebind_rects = [
            ("quit",pygame.Rect(730,280,70,25)),
            ("fullscreen",pygame.Rect(697,336,70,25)),
            ("switch_overlay",pygame.Rect(681,400,70,25)),
            ("pause",pygame.Rect(691,461,70,25))
        ]
        self.settings_rebind_hover_displays:dict[str,tuple[SurfDisplay,SurfDisplay]] = dict()
        for keybind in self.settings_rebind_rects:
            self.settings_rebind_hover_displays[keybind[0]]=(SurfDisplay(pygame.Surface(keybind[1].size),keybind[1]),SurfDisplay(pygame.Surface(keybind[1].size),keybind[1]))
            self.settings_rebind_hover_displays[keybind[0]][0].surf.fill((180,180,180))
            self.settings_rebind_hover_displays[keybind[0]][1].surf.fill((200,200,200))
        self.currently_rebinding = None
        
        self.display_mgr = DisplayManager(btn_getter=get_current_buttons,surf_getter=get_current_surfs)
        self.display_mgr_states = [IN_SIMULATION]+PANEL_STATES

        #Surface pour afficher les graphs
        self.stat_surf = pygame.Surface((100,100))
        self.stat_surf.fill((255,255,255))
        self.stat_refresh_delay = 5
        self.stat_clock = 0
        
        if os_name=="Windows":
            self.night_overlay = pygame.Surface(self.screen.get_size())
            self.night_overlay.fill((0,0,80))
        day_surf = pygame.image.load("data/assets/menu/Bouton_Menu_JOUR.png").convert_alpha()
        night_surf = pygame.image.load("data/assets/menu/Bouton_Menu_NUIT.png").convert_alpha()
        self.day_disp,self.night_disp = SurfDisplay(day_surf,day_surf.get_rect(topleft=(12,77))),SurfDisplay(night_surf,night_surf.get_rect(topleft=(12,77)))

        #Variables pour le suivi d'animal
        def l():self.show_followed_obj_info=not self.show_followed_obj_info # fonction pour le bouton montrer ou non les infos de l'animal suivi
        self.close_info_button=Button((40,590),"menu/Icone_Menu_Informations_Animal",l)

        self.display_overlay = True

        #Variables pour l'optimisation
        self.last_bhv_update = 0
        
        def get_aniaml_age(self_animal:Animal):return self.env.ticks_passed-self_animal.age
        Animal.get_age = get_aniaml_age
    
    def _reload_keybinds_displays(self):
        self.panel_displays[IN_PANEL_SETTINGS]=[
            SurfDisplay(fonts.F20(get_btn_name(self.keybinds["quit"])),pygame.Rect(733,282,0,0)),
            SurfDisplay(fonts.F20(get_btn_name(self.keybinds["fullscreen"])),pygame.Rect(700,339,0,0)),
            SurfDisplay(fonts.F20(get_btn_name(self.keybinds["switch_overlay"])),pygame.Rect(684,403,0,0)),
            SurfDisplay(fonts.F20(get_btn_name(self.keybinds["pause"])),pygame.Rect(694,464,0,0))
        ]
        self.hide_infos_display.surf=fonts.F20(f"Appuyer sur {get_btn_name(self.keybinds['switch_overlay']).capitalize()} pour cacher l'affichage")
        self.hide_infos_display.reload_center()

    def reset_vars(self): #Met les variables à leur état de départ
        self.env_tick_counter = 0 #compteur pour gérer le temps de l’environnement
        self.stat_refresh_delay = 5
        self.stat_clock = 0

        self.cam_pos = (self.env.width/2,self.env.height/2) #position de la caméra et niveau de zoom initial
        self.zoom = 1 #zoom de départ
        screensize = self.screen.get_size()
        self.zoom_range = (max(screensize[0]/self.env.width,screensize[1]/self.env.height),Simulation.max_zoom)
        
        #Variables de gestion du clic
        self.click_wait = False
        self.click_hold = False
        self.click_hold_coords_diff = (0,0)
        self.last_click_pos = (0,0)
        self.last_click_time = 0

        ph = fonts.F20("0")

        self.followed_animal_info_displays:list[SurfDisplay] = [
            SurfDisplay(ph,pygame.Rect((910,193),(0,0))),  # 0  - Nom
            SurfDisplay(ph,pygame.Rect((1030,229),(0,0))), # 1  - Nom Scientifique
            SurfDisplay(ph,pygame.Rect((910,266),(0,0))),  # 2  - Sexe
            SurfDisplay(ph,pygame.Rect((920,304),(0,0))),  # 3  - Taille
            SurfDisplay(ph,pygame.Rect((918,341),(0,0))),  # 4  - Poids
            SurfDisplay(ph,pygame.Rect((1057,375),(0,0))), # 5  - Régime Alimentaire
            SurfDisplay(ph,pygame.Rect((990,411),(0,0))),  # 6  - Alimentation
            SurfDisplay(ph,pygame.Rect((1039,448),(0,0))), # 7  - Energie Maximale
            SurfDisplay(ph,pygame.Rect((1040,487),(0,0))), # 8  - Vitesse Maximale
            SurfDisplay(ph,pygame.Rect((971,525),(0,0))),  # 9  - Génération
            SurfDisplay(ph,pygame.Rect((903,565),(0,0))),  # 10 - Age
            SurfDisplay(ph,pygame.Rect((933,604),(0,0))),  # 11 - Vitalité
            SurfDisplay(ph,pygame.Rect((1005,643),(0,0))), # 12 - Objectif Actuel
        ]
        self.followed_food_info_displays:list[SurfDisplay] = [
            SurfDisplay(ph,pygame.Rect((908,203),(0,0))),  # 0  - Nom
            SurfDisplay(ph,pygame.Rect((1030,238),(0,0))), # 1  - Nom Scientifique
            SurfDisplay(fonts.F20("Fruit"),pygame.Rect((908,276),(0,0))),  # 2  - Type
            SurfDisplay(ph,pygame.Rect((1081,313),(0,0))),  # 3  - Quantité totale d'unité
            SurfDisplay(ph,pygame.Rect((1053,351),(0,0))),  # 4  - Quantité disponible
            SurfDisplay(ph,pygame.Rect((1034,386),(0,0))), # 5  - Energie par unité
            SurfDisplay(ph,pygame.Rect((1033,425),(0,0))),  # 6  - Temps de pousse
            SurfDisplay(ph,pygame.Rect((1118,463),(0,0))), # 7  - Espèce(s) phytophage(s)
            SurfDisplay(ph,pygame.Rect((1029,541),(0,0))), # 8  - Milieu de pousse
        ]
        self.followed_obj:Union[Food,Animal,None] = None #animal ou nourriture suivi (s'il y en a sinon None)
        self.show_followed_obj_info=False#variable pour savoir s'il faut montrer ou non les stats de l'animal
        self.followed_type = 0

        self._reload_keybinds_displays()

        Simulation.speed = 1
        Simulation.playing = True
    
    def start_sim(self):
        devprint("CHARGEMENT EN MODE DEMARRAGE DE SIMULATION")
        self.env = Environnement() #crée un objet de la classe Environnement
        self.env.load_params()
        self.reset_vars()
        self.state = IN_SIMULATION
    
    def start_sim_random (self):
        import random
        params={
            "width" : 3840,
            "height" : 2160,
            "bg": "placeholder_sim_bg",
            "water":[],
            "animals":{
                "cerf":random.randint(0,1)*random.randint(20,50),
                "blaireau":random.randint(0,1)*random.randint(20,50),
                "coq":random.randint(0,1)*random.randint(20,50),
                "elan":random.randint(0,1)*random.randint(20,50),
                "lapin":random.randint(0,1)*random.randint(20,50),
                "ours":random.randint(0,1)*random.randint(5,10),
                "renard":random.randint(0,1)*random.randint(5,10),
                "sanglier":random.randint(0,1)*random.randint(5,10),
                "loup":random.randint(0,1)*random.randint(5,10)
            },
            "foods":{
                "baies":random.randint(150,400),
                "herbe":random.randint(30,70)
            }
        }
        del random
        world.load_sim_params({"app_version":list(version),"params":params})
        world.loaded_data = None
        f_ld.loaded_file = None
        self.env = Environnement() #crée un objet de la classe Environnement
        self.env.load_params()
        self.reset_vars()
        self.state = IN_SIMULATION
    
    def load_sim(self):
        devprint("CHARGEMENT EN MODE CHARGEMENT DE SIMULATION")
        data=world.loaded_data
        self.env:Environnement = data["env"]
        self.env._reassign_world_vars()
        self.env._reassign_objects_funcs()
        self.env.reset_entities()
        FoodType._load_list(data["foodtypes"])
        Food._load_list(data["foods"])
        AnimalType._load_list(data["animaltypes"])
        Animal._load_list(data["animals"])
        self.reset_vars()
        self.state = IN_SIMULATION

    @staticmethod
    def change_speed(new_speed):#methode uttilisée pour changer la vitesse de la simulation
        Simulation.speed=new_speed
        Simulation.playing=True

    def get_pos_from_pixel(self,pos:Point):
        """
        Convertis une position en pixels de la fenêtre en une position dans self.env
        """
        c=self.screen.get_rect().center
        d=(pos[0]-c[0],c[1]-pos[1])
        pos=(self.cam_pos[0]+d[0]/self.zoom,self.cam_pos[1]-d[1]/self.zoom)
        return pos
    
    def get_pixel_from_pos(self,pos:Point):
        """
        Convertis une position dans self.env en une position en pixels de la fenêtre
        """
        cp=self.cam_pos
        c=self.screen.get_rect().center
        d=((pos[0]-cp[0])*self.zoom,(cp[1]-pos[1])*self.zoom)
        px=(c[0]+d[0],c[1]-d[1])
        return px

    def handle_input(self):
        """
        Gère les entrées de l'utilisateur
        """
        if self.state in self.display_mgr_states:
            clicked_smth = self.display_mgr.check_click()

        if self.state == IN_SIMULATION:

            for event in get_events():

                if event.type == pygame.KEYDOWN:

                    if event.key == self.keybinds["quit"]:
                        self.state = IN_PANEL_MAIN
                    
                    elif event.key == self.keybinds["pause"]:
                        Simulation.playing = not Simulation.playing
                    
                    elif event.key == self.keybinds["switch_overlay"]:
                        self.display_overlay = not self.display_overlay
                    
                    elif event.key==self.keybinds["test"] and self.followed_type==1:
                        if self.followed_obj.current_objective.current_subobjective==None:
                            print(self.followed_obj.current_objective.scouting)
                        else:
                            print(self.followed_obj.current_objective.current_subobjective.type)
                
                elif event.type == pygame.MOUSEBUTTONDOWN:


                    if event.button == 1:#click gauche
                        if not clicked_smth: #Pour éviter qu'on n'arrête de suivre un animal en cliqunt sur un bouton
                            self.last_click_time = ticks()
                            self.last_click_pos = event.pos
                            self.click_wait = True
                    
                    elif event.button == 4:# scroll vers le haut
                        mouse = pygame.mouse.get_pos()
                        pos1=self.get_pos_from_pixel(mouse)
                        self.zoom=min(self.zoom*1.2,self.zoom_range[1])
                        pos2=self.get_pos_from_pixel(mouse)
                        self.cam_pos=(self.cam_pos[0]-pos2[0]+pos1[0],self.cam_pos[1]-pos2[1]+pos1[1])
                        self.check_cam_pos()
                        self.env.reduce_animals_n_foods = self.zoom<=Simulation.point_reduced_zoom
                        if not self.env.reduce_animals_n_foods:
                            self.rescale_env()
                    
                    elif event.button == 5:#scroll vers le bas
                        mouse = pygame.mouse.get_pos()
                        pos1=self.get_pos_from_pixel(mouse)
                        self.zoom=max(self.zoom/1.2,self.zoom_range[0])
                        pos2=self.get_pos_from_pixel(mouse)
                        self.cam_pos=(self.cam_pos[0]-pos2[0]+pos1[0],self.cam_pos[1]-pos2[1]+pos1[1])
                        self.check_cam_pos()
                        self.env.reduce_animals_n_foods = self.zoom<=Simulation.point_reduced_zoom
                        if not self.env.reduce_animals_n_foods:
                            self.rescale_env()
                    
                
                elif event.type == pygame.MOUSEBUTTONUP:

                    if event.button == 1:
                        self.click_hold = False
                        if self.click_wait:
                            self.click_wait = False
                            if not self.check_animals_dist(self.get_pos_from_pixel(event.pos)) and not self.check_foods_dist(self.get_pos_from_pixel(event.pos)):
                                self.followed_type=0
                                self.followed_obj=None

        elif self.state == IN_PANEL_MAIN:
            for event in get_events():

                if event.type == pygame.KEYDOWN:

                    if event.key == self.keybinds["quit"]:
                        self.state = IN_SIMULATION

        
        elif self.state in PANEL_STATES:
            for event in get_events():

                if event.type == pygame.KEYDOWN:

                    if self.state == IN_PANEL_SETTINGS and self.currently_rebinding!=None and (event.key not in self.keybinds.values() or event.key==self.keybinds[self.currently_rebinding]):
                        self.keybinds[self.currently_rebinding]=event.key
                        Settings.save()
                        self._reload_keybinds_displays()
                        self.currently_rebinding = None
                        self.rebinding = False

                    elif self.currently_rebinding==None and event.key == self.keybinds["quit"]:
                        self.state = IN_PANEL_MAIN
            
                if event.type==pygame.MOUSEBUTTONDOWN:

                    if self.state == IN_PANEL_SETTINGS:

                        for keybind in self.settings_rebind_rects:
                            if keybind[1].collidepoint(event.pos):
                                self.currently_rebinding = keybind[0]
                                self.rebinding = True
                                break
                        else:
                            self.currently_rebinding = None
                            self.rebinding=False
    
    def check_animals_dist (self,pos:Point): #Vérifie la proximité du click avec les animaux pour mise en place du suivi
        closest = None #Afin de choisir l'animal le plus proche du click s'il y en a plusieurs à proximité sinon None -> pas de suivi
        closest_dist = 50
        for animal in Animal.instances: #uttilisation de test_complexite_temps.py pr voir que c'était mieux que for animal in Animal.instances[1:]
            distance = dist(animal.pos,pos)
            if closest_dist>distance:
                closest=animal
                closest_dist = distance
        if closest:#pour ne pas prendre un animal s'il n'y a pas d'animaux à côté du click
            self.followed_obj = closest
            self.followed_type = 1
            self.update_followed_animal_static_infos()
        return bool(closest)
    
    def check_foods_dist (self,pos:Point):
        closest = None #Afin de choisir la nourriture la plus proche du click s'il y en a plusieurs à proximité sinon None -> pas de suivi
        closest_dist = 50
        for food in Food.instances:
            distance = dist(food.pos,pos)
            if closest_dist>distance:
                closest=food
                closest_dist = distance
        if closest:#pour ne pas prendre une nourriture s'il n'y en a pas à côté du click
            self.followed_obj = closest
            self.followed_type = 2
            if type(closest.type)==FruitType:
                self.update_followed_food_static_infos()
        return bool(closest)

    def update(self):
        """
        Met à jour la simulation à chaque frame
        """

        if self.state in self.display_mgr_states:
            self.display_mgr.update()

        if self.state == STARTING_SIM:
            self.start_sim()
        elif self.state == LOADING_SIM:
            self.load_sim()
        elif self.state == STARTING_SIM_RANDOM:
            self.start_sim_random()
        elif self.state == IN_SIMULATION:
            self.tick_env()
            self.update_click()
            if self.followed_type == 1:
                if self.followed_obj.dead:
                    self.followed_obj = None
                    self.followed_type = 0
                else:
                    self.update_followed_animal_variant_infos()
                    self.update_center_follow()
            elif self.followed_type==2 and type(self.followed_obj.type)==FruitType:
                self.update_followed_food_variant_infos()
            elif self.click_hold:
                self.update_center_hold()
        if self.state != IN_PANEL_SETTINGS:
            self.currently_rebinding=None
            self.rebinding = False
    
    def tick_env(self): #Update l'env en fonction de la vitesse
        extra_tick = Simulation.speed*Simulation.playing #Simulation.playing permet de ne pas faire avancer la simulation si Simulation.playing==False puisque cela multiplierait les ticks à ajouter à self.env_tick_counter par 0
        self.env_tick_counter += extra_tick
        self.env.ticks_passed += extra_tick
        while self.env_tick_counter >= 1:#permet de faire plusieurs fois les updates dans le cas où la vitesse de la simulation serait très élevée
            self.env_tick_counter-=1
            if self.to_update_index>=self.to_update_len:
                self.to_update = Animal.instances[:]
                self.to_update_len=len(self.to_update)
                self.to_update_index=0
                self.to_update_amount=self.to_update_len//Global.opti_lvl+1
            for i in range(self.to_update_len):
                animal=self.to_update[i]
                if not animal.dead:
                    if self.to_update_index<=i<self.to_update_index+self.to_update_amount:
                        update_behaviour(animal)
                    animal.update(simulate_action(animal))
            self.to_update_index+=self.to_update_amount
            
    def update_center_follow(self):
        """
        Met à jour la position de la caméra en suivant un animal
        """
        if self.followed_obj:
            self.cam_pos = self.followed_obj.pos
            self.check_cam_pos()
    
    def update_center_hold(self):
        """
        Met à jour la position de la caméra en se déplaçant en fonction du click gauche de l'utilisateur
        """
        mouse = pygame.mouse.get_pos()
        diff = self.click_hold_coords_diff
        self.cam_pos = (-mouse[0]/self.zoom+diff[0],-mouse[1]/self.zoom+diff[1])
        self.check_cam_pos()
    
    def check_cam_pos(self):
        sw,sh=self.screen.get_size()
        minx,miny,maxx,maxy = sw/2/self.zoom,sh/2/self.zoom,self.env.width-sw/2/self.zoom,self.env.height-sh/2/self.zoom,
        self.cam_pos = (min(max(self.cam_pos[0],minx),maxx),min(max(self.cam_pos[1],miny),maxy))

    def update_click(self):
        """
        Vérifie la longueur du click pour différencier le click de l'appui prolongé
        """
        if self.click_wait and (time_dif(self.last_click_time)>=200 or dist(self.last_click_pos,pygame.mouse.get_pos())>=3):
            self.click_hold_coords_diff = (self.cam_pos[0]+self.last_click_pos[0]/self.zoom,self.cam_pos[1]+self.last_click_pos[1]/self.zoom)
            self.click_hold = True
            self.click_wait = False
    
    def update_followed_animal_static_infos(self):
        f = fonts.F20
        animal = self.followed_obj
        self.followed_animal_info_displays[0].surf = f(animal.sex_params.name)
        self.followed_animal_info_displays[1].surf = f(animal.species.scientific_name)
        self.followed_animal_info_displays[2].surf = f(animal.get_sex_name())
        self.followed_animal_info_displays[3].surf = f(str(animal.sex_params.size)+" m")
        self.followed_animal_info_displays[4].surf = f(str(animal.sex_params.mass)+" kg")
        self.followed_animal_info_displays[5].surf = f(animal.species.diet)
        foods = ""
        max_left=4
        for food in animal.species.foods:
            if self.env.foods.get(food) or self.env.animals.get(food):
                max_left-=1
                if max_left>=0:
                    foods = foods+food.capitalize()+", "
        if max_left>=0:
            self.followed_animal_info_displays[6].surf = f(foods[:-2])
        else:
            self.followed_animal_info_displays[6].surf = f(foods[:-2]+f" +{-max_left}")
        self.followed_animal_info_displays[7].surf = f(str(round(animal.energy_max_kJ))+" kJ")
        self.followed_animal_info_displays[8].surf = f(str(round(animal.max_speed*10,2))+" km/h")
        self.followed_animal_info_displays[9].surf = f(str(animal.gen))  
    
    def update_followed_food_static_infos(self):
        f = fonts.F20
        food = self.followed_obj
        self.followed_food_info_displays[0].surf = f(food.type.name.capitalize())
        self.followed_food_info_displays[1].surf = f(food.type.scientific_name)
        self.followed_food_info_displays[3].surf = f(str(self.env.foods[food.type.name]))
        self.followed_food_info_displays[5].surf = f(str(food.type.base_energy))
        self.followed_food_info_displays[6].surf = f(str(int(food.type.regen_frames//60))+" s")
        amount=0
        for at in AnimalType.instances_dict.values():
            amount+= food.type.name in at.foods

        self.followed_food_info_displays[7].surf = f(str(amount))
        self.followed_food_info_displays[8].surf = f(food.type.biome)
    
    def update_panel_stats(self):
        t=convert(self.env.ticks_passed,"frames","time_format")
        most_advanced = max(*AnimalType.instances_dict.values(), key=lambda at:at.last_gen)
        self.panel_displays[IN_PANEL_STATS] = [
            SurfDisplay(fonts.F20(f"Nombre d'animaux en vie : {len(Animal.instances)}"),pygame.Rect(490,270,0,0)),
            SurfDisplay(fonts.F20(f"Nombre d'animaux morts : {self.env.dead_animals}"),pygame.Rect(490,320,0,0)),
            SurfDisplay(fonts.F20(f"Nombre d'espèces : {len(AnimalType.instances_dict)}"),pygame.Rect(490,370,0,0)),
            SurfDisplay(fonts.F20(f"Temps simulé : {int(t['j'])} j, {int(t['h'])} h"),pygame.Rect(490,420,0,0)),
            SurfDisplay(fonts.F20(f"Espèce la plus développée : {most_advanced.m_params.name}"),pygame.Rect(490,470,0,0))
        ]
    
    def draw_night_overlay(self):
        time = convert(self.env.ticks_passed,"frames","time_format")
        h,m=time["h"],time["m"]
        if os_name=="Windows":
            if h<6 or h>=22:
                self.night_overlay.set_alpha(120)
            elif 6<=h<8:
                self.night_overlay.set_alpha(120-(h-6)*60-m)
            elif 20<=h<22:
                self.night_overlay.set_alpha((h-20)*60+m)
            else:
                self.night_overlay.set_alpha(0)
            self.screen.blit(self.night_overlay, (0, 0))
        else:pass
    
    def get_time_info_surf(self):
        w = convert(self.env.ticks_passed,"frames","time_format")
        all_time = f"Jour {int(w['j'])+1} - {int(w['h']):02d}h{int(w['m']//10*10):02d}"

        text = fonts.F18(all_time,(0,0,0))
        return text

    def draw(self):
        if self.state == IN_SIMULATION:
            self.screen.fill("lightgreen")
            camx=self.cam_pos[0]*self.zoom-self.screen.get_width()/2
            camy=self.cam_pos[1]*self.zoom-self.screen.get_height()/2
            if Global.opti_lvl==20:
                cam_rect = pygame.Rect(0,0,self.screen.get_width()/self.zoom,self.screen.get_height()/self.zoom)
            else:
                cam_rect = pygame.Rect(0,0,self.screen.get_width()/self.zoom+(200*self.zoom),self.screen.get_height()/self.zoom+(200*self.zoom))
            cam_rect.center = self.cam_pos
            self.env.draw(self.screen,camx,camy,cam_rect,self.zoom)
            self.draw_night_overlay()
            if self.followed_type == 1:
                if Settings.advanced_display["path"]:
                    if hasattr(self.followed_obj.current_objective,"scouting") and self.followed_obj.current_objective.scouting:
                        self.draw_scouting_path(self.followed_obj,camx,camy)
                    elif hasattr(self.followed_obj.current_objective,"current_object") and hasattr(self.followed_obj.current_objective.current_object,"pos"):
                        self.draw_goto(self.followed_obj.pos,self.followed_obj.current_objective.current_object.pos,camx,camy) 
                if Settings.advanced_display["hitbox"]:
                    self.followed_obj.update_hitbox()
                    self.draw_hitbox(self.followed_obj,camx,camy)
                if Settings.advanced_display["speed_vect"]:
                    self.draw_speed_vect(self.followed_obj,camx,camy)
                if Settings.advanced_display["fov"]:
                    self.draw_animal_view(self.followed_obj,camx,camy)
            elif self.followed_type == 2:
                if Settings.advanced_display["hitbox"]:
                    self.draw_hitbox(self.followed_obj,camx,camy)
        elif self.state in PANEL_STATES:
            camx=self.cam_pos[0]*self.zoom-self.screen.get_width()/2
            camy=self.cam_pos[1]*self.zoom-self.screen.get_height()/2
            if Global.opti_lvl>=5:
                cam_rect = pygame.Rect(0,0,self.screen.get_width()/self.zoom,self.screen.get_height()/self.zoom)
            else:
                cam_rect = pygame.Rect(0,0,(self.screen.get_width()+200)/self.zoom,(self.screen.get_height()+200)/self.zoom)
            cam_rect.center = self.cam_pos
            self.env.draw(self.screen,camx,camy,cam_rect,self.zoom)
            self.draw_night_overlay()
            if self.followed_type == 1:
                if Settings.advanced_display["path"]:
                    if hasattr(self.followed_obj.current_objective,"scouting") and self.followed_obj.current_objective.scouting:
                        self.draw_scouting_path(self.followed_obj,camx,camy)
                    elif hasattr(self.followed_obj.current_objective,"current_object") and hasattr(self.followed_obj.current_objective.current_object,"pos"):
                        self.draw_goto(self.followed_obj.pos,self.followed_obj.current_objective.current_object.pos,camx,camy) 
                if Settings.advanced_display["hitbox"]:
                    self.draw_hitbox(self.followed_obj,camx,camy)
                if Settings.advanced_display["speed_vect"]:
                    self.draw_speed_vect(self.followed_obj,camx,camy)
                if Settings.advanced_display["fov"]:
                    self.draw_animal_view(self.followed_obj,camx,camy)
            elif self.followed_type == 2:
                if Settings.advanced_display["hitbox"]:
                    self.draw_hitbox(self.followed_obj,camx,camy)
        
        if self.state in self.display_mgr_states:
            self.display_mgr.draw()

    def rescale_env(self):
        self.env.rescale_surf(self.zoom)
        for animaltype in AnimalType.instances_dict.values():
            animaltype.scale_sprites(self.zoom)
        for foodtype in FoodType.instances.values():
            foodtype.scale_sprites(self.zoom)
    
    def update_followed_animal_variant_infos(self):
        animal:Animal=self.followed_obj
        age=convert(self.env.ticks_passed-animal.age,"frames","time_format")
        self.followed_animal_info_displays[10].surf = fonts.F20(f"{age['j']} j, {age['h']} h")
        self.followed_animal_info_displays[11].surf = fonts.F20(f"{int(animal.hp/animal.max_hp*100)}%")
        name:str = animal.current_objective.type
        if name == "find":
            obj = "Se nourrir"
        elif name == "reproduce":
            obj = "Se reproduire"
        elif name == "flee":
            obj = "Fuir un prédateur"
        elif name == "kill":
            obj = "Tuer une proie"
        elif name == "affinities":
            obj = "Former un groupe"
        elif name=="rest":
            obj="Se reposer"
        else:raise ValueError(name)
        self.followed_animal_info_displays[12].surf = fonts.F20(obj)

    def update_followed_food_variant_infos(self):
        food:Food=self.followed_obj
        f=fonts.F20
        self.followed_food_info_displays[4].surf = f(str(food.available_fruits_amount))


    def draw_scouting_path(self,animal:Animal,camx,camy):
        pattern=[animal.pos]+animal.scouting_objective.pattern[animal.scouting_objective.current_index:]
        pygame.draw.lines(self.screen,"blue",False,[(pattern[i][0]*self.zoom-camx,pattern[i][1]*self.zoom-camy) for i in range(len(pattern))])
    
    def draw_goto(self,animal_pos:Point,objective_pos:Point,camx:Number,camy:Number):
        pygame.draw.line(self.screen,"blue",(animal_pos[0]*self.zoom-camx,animal_pos[1]*self.zoom-camy),(objective_pos[0]*self.zoom-camx,objective_pos[1]*self.zoom-camy))

    def draw_hitbox(self,obj:Animal|Food,camx,camy):
        for triangle in obj.hitbox:
            pygame.draw.polygon(self.screen,"red",[(triangle.points[i][0]*self.zoom-camx,triangle.points[i][1]*self.zoom-camy) for i in range(3)])

    def draw_speed_vect(self,animal:Animal,camx,camy):
        point_eight_five_rads=math.pi*0.85
        p2=animal.pos+Vect(length=animal.speed*100,direction=animal.rad)
        p3=p2+Vect(length=7,direction=animal.rad+point_eight_five_rads)
        p4=p2+Vect(length=7,direction=animal.rad-point_eight_five_rads)
        p1=animal.pos[0]*self.zoom-camx,animal.pos[1]*self.zoom-camy
        p2=p2[0]*self.zoom-camx,p2[1]*self.zoom-camy
        p3=p3[0]*self.zoom-camx,p3[1]*self.zoom-camy
        p4=p4[0]*self.zoom-camx,p4[1]*self.zoom-camy
        #Nous avons utilisé cette liste de couleurs : https://www.pygame.org/docs/ref/color_list.html
        pygame.draw.line(self.screen,"black",p3,p2,5)
        pygame.draw.line(self.screen,"chartreuse3",p3,p2,3)
        pygame.draw.line(self.screen,"black",p4,p2,5)
        pygame.draw.line(self.screen,"chartreuse3",p4,p2,3)
        pygame.draw.line(self.screen,"black",p1,p2,5)
        pygame.draw.line(self.screen,"chartreuse3",p1,p2,3)
    
    def draw_animal_view(self,animal:Animal,camx,camy):
        rdir=animal.rad+animal.fov/2
        ldir=animal.rad-animal.fov/2
        p1=animal.pos+Vect(direction=rdir,length=animal.view_dist)
        p2=animal.pos+Vect(direction=ldir,length=animal.view_dist)
        pygame.draw.line(self.screen,"purple",(p1[0]*self.zoom-camx,p1[1]*self.zoom-camy),(animal.pos[0]*self.zoom-camx,animal.pos[1]*self.zoom-camy))
        pygame.draw.line(self.screen,"purple",(p2[0]*self.zoom-camx,p2[1]*self.zoom-camy),(animal.pos[0]*self.zoom-camx,animal.pos[1]*self.zoom-camy))
        pygame.draw.arc(self.screen,"purple",pygame.Rect((animal.pos[0]-animal.view_dist)*self.zoom-camx,(animal.pos[1]-animal.view_dist)*self.zoom-camy,animal.view_dist*2*self.zoom,animal.view_dist*2*self.zoom),-rdir,-ldir)
    
    def quick_simulation(self,ticks:int):
        while self.env.ticks_passed<ticks:
            self.env.ticks_passed+=1
            for animal in Animal.instances:
                    update_behaviour(animal)
                    animal.update(simulate_action(animal))

    def run(self):
        self.run_fcts(SIMULATION_STATES,self.handle_input,self.update,self.draw)


if __name__ == "__main__":
    LAUNCH_TYPE = "sim"
    sim = Simulation()
    if LAUNCH_TYPE=="default":
        load_default_sim()
        sim.start_sim()
    elif LAUNCH_TYPE=="random":
        sim.start_sim_random()
    elif LAUNCH_TYPE=="sim":
        f_ld.load_sim_file("data/simulations/sim/Simulation_demo.sim")
        sim.load_sim()
    sim.run()
    quit()
