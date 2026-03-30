#Projet : The Descent
#Auteurs : Ahmed-Adam REZKALLAH, Noé SAMUEL

from utils import *
from environnement.json_loader import *
from file_loader import *
from file_dialog import FileDialog as fd, Path
import queue
from credits_launcher import *
from input_box import *
#importation des modules pythons


def get_json_files(folder_path):
    return {f.split(".")[0]:os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".json")}

class CustomWindow:
    bck = pygame.image.load(os.sep.join(["data","assets","menu","Fond_Menu_ModePersonnalise.png"]))
    bck_w,bck_h = bck.get_size()
    x = (1280-bck_w)//2
    y = (720-bck_h)//2

    padding_x = 30
    padding_top = 60
    padding_bottom = 10

    scrolled = 0
    scroll_speed = 30
    surf_scroll_barre = pygame.Surface((0,0))
    scroll_barre:list = []
    remember_y = None

    animals:dict[str,dict[str,any]] = {}
    simstat = {}

    content = []
    params = []
    animal_order = []
    text_blocks:list[Input_box] = []
    global_block:list[Input_box] = []
    content_height = 0
    reset_button:Union[Button,None] = None
    submit_button:Union[Button,None] = None
    submit_button_line_height:Union[float,None] = None

    menu = None

    @staticmethod
    def _init(menu):
        CustomWindow.menu = menu
        CustomWindow.content = []
        CustomWindow.text_blocks = []
        CustomWindow.content_height = 0
        CustomWindow.submit_button_line_height = None

        animal_paths = get_json_files(os.sep.join(["data","species"]))
        for animal in animal_paths:
            CustomWindow.animals[animal] = load_species(animal)
        CustomWindow.simstat = load_sim_env("data/simulations/default/default_sim.json")
        CustomWindow.separator_img = pygame.image.load("data/assets/menu/Barre_Separateur_Menu.png").convert_alpha()

        animal_by_diet:dict[str,list[str]] = {}
        for animal in CustomWindow.animals:
            diet = CustomWindow.animals[animal]["diet"]
            animal_by_diet.setdefault(diet,[]).append(animal)

        parameters = ["Nombre d'individus",
                      "max_stamina",
                      "max_hp",
                      "view_dist",
                      "stamina_recovery_rate"]
        CustomWindow.params = parameters

        content = []
        for diet in animal_by_diet:
            content.append([diet,True])
            for animal in animal_by_diet[diet]:
                CustomWindow.animal_order.append(animal)
                content.append([animal,True])
                for param_name in parameters:
                    content.append(param_name)
        content.append(["End",True])

        font24 = Font(24)
        font36 = Font(36)


        CustomWindow.content_height+=18
        CustomWindow.content.append([font36.render("Taille de la simulation",(0,0,0))])
        CustomWindow.content_height+=46
        CustomWindow.content_height+=18
        for x in ["Largeur (x)","Hauteur (y)"]:
            label_surf = font24.render(x+" : ",(0,0,0))
            CustomWindow.content.append(label_surf)
            ti = Input_box(pos=(0,0),size=(120,36),filter="digits",max_len=5)
            CustomWindow.global_block.append(ti)
            CustomWindow.content_height+=44


        for e in content:
            if type(e) == list:
                label = e[0]

                if label == "End":
                    CustomWindow.content.append([])
                    CustomWindow.content_height+=18
                    CustomWindow.submit_button_line_height = CustomWindow.content_height
                    CustomWindow.content_height+=60
                    continue

                CustomWindow.content.append([])
                CustomWindow.content_height+=18
                CustomWindow.content.append([font36.render(label,(0,0,0))])
                CustomWindow.content_height+=46

            else:
                if e:label_surf = font24.render(e+" : ",(0,0,0))
                else:label_surf = font24.render("",(0,0,0))
                CustomWindow.content.append(label_surf)

                if e == "Nombre d'individus":max_len = 5
                else:max_len = 5
                ti = Input_box(pos=(0,0),size=(120,36),filter="digits",max_len=max_len)
                CustomWindow.text_blocks.append(ti)

                CustomWindow.content_height+=44

        CustomWindow.surf_scroll_barre = pygame.Surface((25,410), pygame.SRCALPHA)
        CustomWindow.scroll_barre = [0,0,25,40]

        answers = [tb.result for tb in CustomWindow.text_blocks]
        for i,animal in enumerate(CustomWindow.animal_order):
            for j,param in enumerate(CustomWindow.params):
                if param == "Nombre d'individus":
                    answers[j+i*len(CustomWindow.params)] = CustomWindow.simstat["params"]["animals"][animal]
                else:answers[j+i*len(CustomWindow.params)]=CustomWindow.animals[animal][param]
        for i,tb in enumerate(CustomWindow.text_blocks):tb.result=str(answers[i])

        for i,tb in enumerate(CustomWindow.global_block):tb.result=str(CustomWindow.simstat["params"][["width","height"][i]])

    @staticmethod
    def init_submit_button():
        if CustomWindow.submit_button_line_height is None:
            return
        
        def on_submit():
            Data.sim_type = "Perso"
            answers = [tb.result for tb in CustomWindow.text_blocks]
            for i,animal in enumerate(CustomWindow.animal_order):
                for j,param in enumerate(CustomWindow.params):
                    a = answers[j+i*len(CustomWindow.params)]
                    if param == "Nombre d'individus":
                        if a == "":CustomWindow.simstat["params"]["animals"][animal]=0
                        elif a[0]==".":a="0"+a
                        elif a[-1]==".":a=a+"0"
                        CustomWindow.simstat["params"]["animals"][animal]=int(a)
                    else:
                        if a == "":CustomWindow.animals[animal][param]=0
                        elif a[0]==".":a="0"+a
                        elif a[-1]==".":a=a+"0"
                        CustomWindow.animals[animal][param]=float(a)
                        
            for i,tb in enumerate(CustomWindow.global_block):
                r = tb.result
                if r == "":r="0"
                elif r[0]==".":r="0"+r
                elif r[-1]==".":r=r+"0"
                param = ["width","height"][i]
                CustomWindow.simstat["params"][param] = max(int(tb.result),3840 if param=="width" else 2160)
                
            CustomWindow.save_new_simstats()
            try:
                CustomWindow.menu.load_json("data/simulations/simstat/temp_custom_simstat.json")
                CustomWindow.menu.state = STARTING_SIM
            except Exception as e:
                print(e)
            finally:
                CustomWindow.load_original_data()
                CustomWindow.save_new_simstats()
        
        center_x = CustomWindow.x+CustomWindow.bck_w//2
        logical_y = CustomWindow.y+CustomWindow.padding_top+CustomWindow.submit_button_line_height
        CustomWindow.submit_button = Button((center_x,logical_y+25),"menu/Boutons_Menu_Valider",on_submit)

    @staticmethod
    def init_reset_button():
        CustomWindow.reset_button = Button((970,200),"menu/Bouton_Menu_Reset",CustomWindow.load_original_data)

    @staticmethod
    def get_viewport_rect():
        return pygame.Rect(CustomWindow.x+CustomWindow.padding_x,CustomWindow.y+CustomWindow.padding_top,CustomWindow.bck_w-2*CustomWindow.padding_x,CustomWindow.bck_h-CustomWindow.padding_top-CustomWindow.padding_bottom)

    @staticmethod
    def handle_scroll(event:pygame.event.Event):
        viewport = CustomWindow.get_viewport_rect()
        mouse_x,mouse_y = pygame.mouse.get_pos()
        condition = 1030 <= mouse_x <= 1055 and CustomWindow.scroll_barre[1]+170 <= mouse_y <= CustomWindow.scroll_barre[3]+CustomWindow.scroll_barre[1]+170

        if event.type == pygame.MOUSEWHEEL:
            CustomWindow.scrolled -= event.y*CustomWindow.scroll_speed

            max_scroll = max(0,CustomWindow.content_height - viewport.height)

            CustomWindow.scrolled = max(0,min(CustomWindow.scrolled,max_scroll))
            if CustomWindow.content_height>viewport.height:
                CustomWindow.scroll_barre[1] = (CustomWindow.scrolled / (CustomWindow.content_height - viewport.height) * (410 - CustomWindow.scroll_barre[3]))
        if condition and event.type == pygame.MOUSEBUTTONDOWN:
            CustomWindow.remember_y = mouse_y
        if event.type == pygame.MOUSEMOTION and CustomWindow.remember_y is not None:
            diff = (CustomWindow.remember_y-mouse_y)/(410-CustomWindow.scroll_barre[3])*(CustomWindow.content_height-viewport.height)
            max_scroll = max(0,CustomWindow.content_height-viewport.height)
            CustomWindow.scrolled = max(0,min(CustomWindow.scrolled-diff,max_scroll))
            if CustomWindow.content_height>viewport.height:
                CustomWindow.scroll_barre[1] = CustomWindow.scrolled/(CustomWindow.content_height-viewport.height)*(410-CustomWindow.scroll_barre[3])
            CustomWindow.remember_y = mouse_y
        if event.type == pygame.MOUSEBUTTONUP:
            CustomWindow.remember_y = None

    @staticmethod
    def handle_events()->bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            CustomWindow.handle_scroll(event)
            for tb in CustomWindow.global_block+CustomWindow.text_blocks:
                tb.handle_input(event)
            if CustomWindow.submit_button is not None and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                CustomWindow.submit_button.check_click(event.pos)
            if CustomWindow.reset_button is not None and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                CustomWindow.reset_button.check_click(event.pos)
        return True

    @staticmethod
    def display():
        Global.screen.blit(CustomWindow.bck,(CustomWindow.x,CustomWindow.y))

        viewport = CustomWindow.get_viewport_rect()
        Global.screen.set_clip(viewport)


        spacing = 0
        param_y_list = []

        for e in CustomWindow.content:

            y = (CustomWindow.y+CustomWindow.padding_top+spacing-CustomWindow.scrolled)

            if type(e)==list:
                if e:
                    Global.screen.blit(e[0],(CustomWindow.x+CustomWindow.padding_x,y))
                    spacing+=46
                else:
                    sep = CustomWindow.separator_img
                    x = CustomWindow.x+(CustomWindow.bck_w-sep.get_width())//2
                    y_draw = y-sep.get_height()//2
                    Global.screen.blit(sep,(x,y_draw))
                    spacing+=18
            else:
                Global.screen.blit(e,(CustomWindow.x+CustomWindow.padding_x,y))
                spacing+=44
                param_y_list.append(y)

        for tb,y_screen in zip(CustomWindow.global_block+CustomWindow.text_blocks,param_y_list):
            x_label = CustomWindow.x+CustomWindow.padding_x
            tb.input_rect.topleft = (x_label+260,y_screen)
            tb.cursor_rect.centery = tb.input_rect.height/2
            tb.update()
            tb.draw()
    
        if CustomWindow.submit_button is not None and CustomWindow.submit_button_line_height is not None:
            base_y = CustomWindow.y+CustomWindow.padding_top+CustomWindow.submit_button_line_height
            btn_y = base_y-CustomWindow.scrolled + 25
            CustomWindow.submit_button.rect.center = (CustomWindow.x+CustomWindow.bck_w//2,btn_y)
            CustomWindow.submit_button.update()
            CustomWindow.submit_button.draw()

        Global.screen.set_clip(None)

        if CustomWindow.reset_button !=None:
            CustomWindow.reset_button.update()
            CustomWindow.reset_button.draw()

        CustomWindow.surf_scroll_barre.fill((0,0,0,0))
        pygame.draw.rect(CustomWindow.surf_scroll_barre,(100,100,100),(0,0,25,410),border_radius=12)
        pygame.draw.rect(CustomWindow.surf_scroll_barre,(200,200,200),CustomWindow.scroll_barre,border_radius=12)

        Global.screen.blit(CustomWindow.surf_scroll_barre,(1030,170))

    @staticmethod
    def save_new_simstats():
        for animal in CustomWindow.animals:
            with open(os.sep.join(["data","species",animal+".json"]),"w") as n:
                json.dump(CustomWindow.animals[animal],n)
        with open(os.sep.join(["data","simulations","simstat","temp_custom_simstat.json"]),"w") as n:
            json.dump(CustomWindow.simstat,n)

    @staticmethod
    def load_original_data():
        animal_paths = get_json_files(os.sep.join(["data","species","default"]))
        for animal in animal_paths:
            CustomWindow.animals[animal] = load_species(animal)
        CustomWindow.simstat = load_sim_env("data/simulations/default/default_sim.json")

        answers = [tb.result for tb in CustomWindow.text_blocks]
        for i,animal in enumerate(CustomWindow.animal_order):
            for j,param in enumerate(CustomWindow.params):
                if param == "Nombre d'individus":
                    answers[j+i*len(CustomWindow.params)] = CustomWindow.simstat["params"]["animals"][animal]
                else:answers[j+i*len(CustomWindow.params)]=CustomWindow.animals[animal][param]
        for i,tb in enumerate(CustomWindow.text_blocks):tb.result=str(answers[i])

        for i,tb in enumerate(CustomWindow.global_block):tb.result=str(CustomWindow.simstat["params"][["width","height"][i]])



class Save_va:
    menu = None
    load_a_pkl_with_file_dialog = None
    pending_main_thread_actions = queue.Queue()
    load_and_run = None

    saves_info_length = 0
    saves = []
    saves_info = []
    surf_scroll_barre = pygame.Surface((0,0))
    scroll_barre = []
    scroll_speed = 30

    LEFT_MARGIN  = -50
    RIGHT_MARGIN  = -50
    START_X = 150
    S_max = 0
    C_max = 0
    C_left  = 0
    C_right = 0

    trashmode = False
    def f(): Save_va.trashmode = not Save_va.trashmode
    trash_button = Button((200,580),"menu/Bouton_Menu_SuppressionSave",f)
    del f

    def _init(length_saves_info,saves_info,scroll_barre_length,menu):
        Save_va.menu = menu

        def pop_up_to_confirm_wrapper(func:Callable):
            def wrapper(*args,**kwargs):
                if Save_va.trashmode:
                    popup_image = pygame.image.load("data/assets/menu/PopUp_RetraitSave.png").convert_alpha()
                else:popup_image = pygame.image.load("data/assets/menu/PopUp_Menu_ChargementSauvegarde.png").convert_alpha()
                popup_area = popup_image.get_size()

                rect = popup_image.get_rect(center=Global.screen.get_rect().center)

                btn_yes = pygame.image.load("data/assets/menu/Bouton_PopUp_Oui.png").convert_alpha()
                btn_yes_hover = pygame.image.load("data/assets/menu/Bouton_PopUp_Oui_hover.png").convert_alpha()
                btn_no = pygame.image.load("data/assets/menu/Bouton_PopUp_Non.png").convert_alpha()
                btn_no_hover = pygame.image.load("data/assets/menu/Bouton_PopUp_Non_hover.png").convert_alpha()

                btn_yes_rect =btn_yes.get_rect(center=(rect.left + popup_area[0]/3-40, rect.top + 2*popup_area[1]/3+50))
                btn_no_rect = btn_no.get_rect(center=(rect.left + 2*popup_area[0]/3+40, rect.top + 2*popup_area[1]/3+50))

                waiting = True
                clock = pygame.time.Clock()

                while waiting:
                    clock.tick(60)
                    mouse_pos = pygame.mouse.get_pos()
                    mouse_pressed = pygame.mouse.get_pressed()[0]

                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            quit()

                    Global.screen.blit(popup_image, rect.topleft)

                    if btn_yes_rect.collidepoint(mouse_pos):
                        Global.screen.blit(btn_yes_hover, btn_yes_rect.topleft)
                        if mouse_pressed:
                            func(*args, **kwargs)
                            waiting = False
                    else:
                        Global.screen.blit(btn_yes, btn_yes_rect.topleft)

                    if btn_no_rect.collidepoint(mouse_pos):
                        Global.screen.blit(btn_no_hover, btn_no_rect.topleft)
                        if mouse_pressed:
                            waiting = False
                    else:
                        Global.screen.blit(btn_no, btn_no_rect.topleft)

                    pygame.display.flip()

            return wrapper

        @pop_up_to_confirm_wrapper
        def loadAndRun(path):
            if Save_va.trashmode:
                Save_va.supr_save_file_path(path)
                Save_va.reinit()
            else:
                menu.load_pkl(path)
                if menu.is_load_successful:
                    menu.load_current_load_state()
                else:
                    Save_va.supr_save_file_path(path)
                    Save_va.reinit()

        Save_va.load_and_run=lambda path:Save_va.pending_main_thread_actions.put(lambda:loadAndRun(path))

        def external_load():

            def on_file_selected(path):
                if path is None:
                    return
                
                
                f = read_sim_file(path)

                add_path({"path":path,
                          "name":path.split(".")[-2].split("/")[-1],
                          "Nombre d'animaux":len(f["animals"]),
                          "Nombre d'espèces":len({animal.species for animal in f["animals"]}),
                          "Temps (j)":f["environnement"].ticks_passed,
                          "Type de simulation":f["csv_memory"]["type"]})

                Save_va.reinit()
                menu.run_fcts_once(menu.handle_input, menu.update, menu.draw)
                Save_va.pending_main_thread_actions.put(lambda:Save_va.load_and_run(path))

            fd.open_file_dialog(filetypes=["sim"],done_function=on_file_selected)

        Save_va.load_a_pkl_with_file_dialog=external_load

        Save_va.values(length_saves_info,saves_info,scroll_barre_length)

    @staticmethod
    def values(length_saves_info,saves_info,scroll_barre_length):
        Save_va.saves_info_length = length_saves_info
        Save_va.saves_info = saves_info
        def make_button(pos,click_effect,text,text_color,font:Font=None,extra_info:dict={}):
            if font is None: 
                font_size=15 if len(text)>20 else 17 if 19<len(text)<22 else 20 #ca permet de changer la taille de la police des textes si ils sont trop longs
                font = Font(font_size)
            button = Button(pos,"menu/Fond_Menu_SavesSimulation",click_effect)
            b_text = font(text,text_color)
            if text == "+" : #pour pouvoir mettre une position différente au texte du bouton +
                button.norm_surf.blit(b_text,((button.norm_surf.get_width()-b_text.get_width())//2,(button.norm_surf.get_height()-b_text.get_height())//2))
                button.hover_surf.blit(b_text,((button.hover_surf.get_width()-b_text.get_width())//2,(button.hover_surf.get_height()-b_text.get_height())//2))
            else:
                button.norm_surf.blit(b_text,((button.norm_surf.get_width()-b_text.get_width())//2,40))
                button.hover_surf.blit(b_text,((button.hover_surf.get_width()-b_text.get_width())//2,40))
                font = Font(18)
                for i,info in enumerate(extra_info):
                    t = font(f"{info}{extra_info[info]}")
                    h = t.get_height()+1
                    button.norm_surf.blit(t,(5,40+(i+2)*h*2))
                    button.hover_surf.blit(t,(5,40+(i+2)*h*2))
            return button
        Save_va.saves=[make_button((200+240*i,320),lambda i=i: Save_va.load_and_run(saves_info[i]["path"]),f"{saves_info[i]['name']}",(0,0,0),extra_info={"Nombre d'animaux : ":saves_info[i]["Nombre d'animaux"],"Nombre d'espèces : ":saves_info[i]["Nombre d'espèces"],"Temps simulé : ":saves_info[i]["Temps (j)"],"Type de simu : ":saves_info[i]["Type de simulation"]}) for i in range(length_saves_info)] #on ne met pas de taille de font pour faire fonctionner la condition de make_button pour changer la taille de la police si besoin
        Save_va.saves.append(make_button((200+240*len(Save_va.saves),320),Save_va.load_a_pkl_with_file_dialog,f"+",(0,0,0),Font(125)))
        Save_va.surf_scroll_barre = pygame.Surface((1000,20), pygame.SRCALPHA)
        Save_va.surf_scroll_barre.fill((0,0,0,0))
        Save_va.scroll_barre = [0,0,scroll_barre_length,20]

        Save_va.S_max = 1000 - scroll_barre_length
        Save_va.C_max = (240 * length_saves_info + 200) - 980
        Save_va.C_left  = Save_va.START_X + Save_va.LEFT_MARGIN
        Save_va.C_right = Save_va.START_X - Save_va.C_max - Save_va.RIGHT_MARGIN

    @staticmethod
    def display():
        if Save_va.trashmode:
            trash_symbol = pygame.image.load("data/assets/menu/Bouton_Menu_SuppressionSavePolygone.png").convert_alpha()
            for button in Save_va.saves[:-1]:
                x = button.rect.centerx - trash_symbol.get_width()/2
                y = button.rect.bottom - trash_symbol.get_height()/2
                Global.screen.blit(trash_symbol,(x,y))

        if Save_va.saves_info_length >= 4:
            pygame.draw.rect(Save_va.surf_scroll_barre,(70,70,70),(0,0,1000,20),border_radius=20)
            pygame.draw.rect(Save_va.surf_scroll_barre,(200,200,200),Save_va.scroll_barre,border_radius=20)
            Global.screen.blit(Save_va.surf_scroll_barre,(150,520))

    @staticmethod
    def reinit():
        f = load_sim_env("data/simulations/info_sim_hist.json") #il faut changer le nom de la def pcq c pas représentatif de tt les fois qu'on l'utilise
        saves_info=f["save_files"]
        seen = set()
        saves_info = [save_info for save_info in saves_info if not (save_info["path"] in seen or seen.add(save_info["path"]))]
        if f["save_files"]!=saves_info:
            f["save_files"]=saves_info
            with open("data/simulations/info_sim_hist.json",'w') as n:
                        json.dump(f,n)
        length_saves_info=len(saves_info)
        scroll_barre_length=4.5*1000/(length_saves_info+1)
        Save_va.values(length_saves_info,saves_info,scroll_barre_length)

    @staticmethod
    def check_filepath_validity(path):
        return Path(path).exists()

    @staticmethod
    def supr_save_file_path(path):
        f = load_sim_env("data/simulations/info_sim_hist.json") #il faut changer le nom de la def pcq c pas représentatif de tt les fois qu'on l'utilise
        saves_info=f["save_files"]
        saves_info=[save_info for save_info in saves_info if not save_info['path']==path]
        if f["save_files"]!=saves_info:
            f["save_files"]=saves_info
            with open("data/simulations/info_sim_hist.json",'w') as n:
                json.dump(f,n)

    def check_all_path_validity(self):
        for save in Save_va.saves_info:
            path = save["path"]
            if not self.check_filepath_validity(path): self.supr_save_file_path(path)
        


class Menu(Runable): #Classe gérant le menu du jeu
    def __init__(self):
        self.current_load_state = STARTING_SIM_RANDOM

        self.main_menu_background = pygame.image.load("data/assets/menu/Fond_Menu.png").convert()
        self.main_menu_background = pygame.transform.scale(self.main_menu_background, self.screen.get_size())

        self.menu_background = pygame.image.load("data/assets/menu/Fond_Menu_Sans_Titre.png").convert()
        self.menu_background = pygame.transform.scale(self.menu_background, self.screen.get_size())

        def load_a_pkl_with_file_dialog():
            if fd.is_open:
                self.show_file_dialog_warning = 1
            else:
                fd.open_file_dialog(filetypes=["sim"],done_function=self.load_pkl)
        
        def load_a_json_with_file_dialog():
            if fd.is_open:
                self.show_file_dialog_warning = 1
            else:
                fd.open_file_dialog(filetypes=["simstat"],done_function=self.load_json)

        def cancel_button_action():
            if fd.is_open:
                try:
                    fd.close_file_dialog()
                    self.state=IN_MAIN_MENU
                    self.is_last_file_invalid = False
                    self.is_load_successful = False
                except:
                    self.show_file_dialog_warning = 2
            else:
                self.state=IN_MAIN_MENU
                self.is_last_file_invalid = False
                self.is_load_successful = False

                
        t=WritingTypeAndSize
        y_offset = 35
        btn_cancel = [(775,615-y_offset),(130,40),"Retour",(0,0,0),t.F22,(255,255,255),cancel_button_action,(0,0,0,0),(0,0,0,0)]
        btn_quit = [(1015,615-y_offset),(90,40),"Quitter",(0,0,0),t.F22,(255,255,255),QUITTING,(0,0,0,0),(0,0,0,0)]
        def run_cr():run_credits(self.screen,"data/credits/credits.txt")

        allButtonsInfo={
            "main_menu_buttons":[
                [(340,615-y_offset),(245,40),"Charger une simulation",(0,0,0),t.F22,(255,255,255),IN_MENU_LOADING,(0,0,0,0),(0,0,0,0)],
                [(585,615-y_offset),(210,40),"Mode Personnalisé",(0,0,0),t.F22,(255,255,255),IN_SIM_SETUP,(0,0,0,0),(0,0,0,0)],
                [(775,615-y_offset),(130,40),"Paramètres",(0,0,0),t.F22,(255,255,255),IN_SETTINGS,(0,0,0,0),(0,0,0,0)],
                [(905,615-y_offset),(90,40),"Crédits",(0,0,0),t.F22,(255,255,255),run_cr,(0,0,0,0),(0,0,0,0)],
                btn_quit],
            "settings_buttons":[
                btn_cancel,
                btn_quit],
            "load_buttons":[
                btn_cancel,
                btn_quit],
            "custom_buttons":[
                [(775,665-y_offset),(130,40),"Retour",(0,0,0),t.F22,(255,255,255),cancel_button_action,(0,0,0,0),(0,0,0,0)],
                [(1015,665-y_offset),(90,40),"Quitter",(0,0,0),t.F22,(255,255,255),QUITTING,(0,0,0,0),(0,0,0,0)],
                [(340,665-y_offset),(245,40),"Charger un fichier",(0,0,0),t.F22,(255,255,255),load_a_json_with_file_dialog,(0,0,0,0),(0,0,0,0)]]

        }
        CustomWindow._init(self)
        CustomWindow.init_submit_button()
        CustomWindow.init_reset_button()

        self.allButtons={key:[Button(*allButtonsInfo[key][i]) for i in range(len(allButtonsInfo[key]))] for key in list(allButtonsInfo.keys())}
        self.allButtons["load_buttons"].append(Save_va.trash_button)
        
        saves_info=load_sim_env("data/simulations/info_sim_hist.json")["save_files"] #il faut changer le nom de la def pcq c pas représentatif de tt les fois qu'on l'utilise
        length_saves_info=len(saves_info)
        scroll_barre_length=4.5*1000/(length_saves_info+1)

        Save_va._init(length_saves_info,saves_info,scroll_barre_length,self)
        self.remember_pos_mouse = None

        f=fonts.F20
        settings_surfdisplays = [
            SurfDisplay("menu/Fond_MenuPrincipal_Parametres",(640,350)),
            SurfDisplay(f("Ouvrir le tableau de bord :"), pygame.Rect(450,282,0,0)),
            SurfDisplay(f("Mettre en plein écran :"), pygame.Rect(450,339,0,0)),
            SurfDisplay(f("Masquer l'affichage :"), pygame.Rect(450,403,0,0)),
            SurfDisplay(f("Pauser la simulation :"), pygame.Rect(450,464,0,0)),
            SurfDisplay(f("Afficher les fps :"), pygame.Rect(450,224,0,0)),
        ]

        self.settings_dynamic_surfs = [
            SurfDisplay(fonts.F20(get_btn_name(self.keybinds["quit"])),pygame.Rect(750,282,0,0)),
            SurfDisplay(fonts.F20(get_btn_name(self.keybinds["fullscreen"])),pygame.Rect(750,339,0,0)),
            SurfDisplay(fonts.F20(get_btn_name(self.keybinds["switch_overlay"])),pygame.Rect(750,403,0,0)),
            SurfDisplay(fonts.F20(get_btn_name(self.keybinds["pause"])),pygame.Rect(750,464,0,0)),
            SurfDisplay(fonts.F20(("Oui" if Global.show_fps else "Non")),pygame.Rect(750,224,0,0))
        ]
        self.settings_rebind_rects = [
            ("quit", pygame.Rect(735,278,100,30)),
            ("fullscreen", pygame.Rect(735,335,100,30)),
            ("switch_overlay", pygame.Rect(735,399,100,30)),
            ("pause", pygame.Rect(735,460,100,30)),
            ("fps", pygame.Rect(735,220,100,30))
        ]

        self.settings_rebind_hover_displays:dict[str,tuple[SurfDisplay,SurfDisplay]] = dict()
        for keybind in self.settings_rebind_rects:
            self.settings_rebind_hover_displays[keybind[0]]=(SurfDisplay(pygame.Surface(keybind[1].size),keybind[1]),SurfDisplay(pygame.Surface(keybind[1].size),keybind[1]))
            self.settings_rebind_hover_displays[keybind[0]][0].surf.fill((180,180,180))
            self.settings_rebind_hover_displays[keybind[0]][1].surf.fill((200,200,200))
        self.currently_rebinding = None

        def get_active_buttons()->list[Button]:
            if self.state == IN_MAIN_MENU:
                return self.allButtons["main_menu_buttons"]+[self.start_loaded_sim_button]
            elif self.state == IN_MENU_LOADING:
                if self.is_load_successful:
                    return self.allButtons["load_buttons"]+Save_va.saves
                return self.allButtons["load_buttons"]+Save_va.saves[:-1] if Save_va.trashmode else self.allButtons["load_buttons"]+Save_va.saves
            elif self.state == IN_SIM_SETUP:
                if self.is_load_successful:
                    return self.allButtons["custom_buttons"]+[self.start_loaded_sim_button]
                return self.allButtons["custom_buttons"]
            elif self.state == IN_SETTINGS:
                return self.allButtons["settings_buttons"]
            else:return []
            
        def get_active_surfdisplays():
            total=self.surf_displays["all_displays"][:]
            if self.state==IN_MENU_LOADING:
                if self.show_file_dialog_warning==1:total.append(self.open_file_dialog_warning_1)
                elif self.show_file_dialog_warning==2:total.append(self.open_file_dialog_warning_2)
                elif self.is_last_file_invalid:total.append(self.invalid_file_display)
                elif self.is_load_successful:total.append(self.successful_upload_display)
            elif self.state == IN_SETTINGS:
                total = total+settings_surfdisplays
                if self.currently_rebinding!=None:
                    total.append(self.settings_rebind_hover_displays[self.currently_rebinding][1])
                else:
                    for keybind in self.settings_rebind_rects:
                        if keybind[1].collidepoint(pygame.mouse.get_pos()):
                            total.append(self.settings_rebind_hover_displays[keybind[0]][0])
                total = total+self.settings_dynamic_surfs
            return total

        self.objs_mgr=DisplayManager(get_active_buttons,get_active_surfdisplays)
        
        version_surf=Font(25)(version_string)
        version_rect=version_surf.get_rect()
        version_rect.bottomleft=self.screen.get_rect().bottomleft

        self.surf_displays = {
            "all_displays":[
                SurfDisplay(version_surf,version_rect)]
        }
        self.invalid_file_display = SurfDisplay(t.F30.render("Fichier invalide","red"),(640,400))
        self.successful_upload_display = SurfDisplay(t.F30.render("Simulation chargée !","green"),(640,400))
        self.is_last_file_invalid = False
        self.is_load_successful = False
        self.start_loaded_sim_button = Button((627, 445),"menu/Bouton_Menu_LancerUneSimulation",self.load_current_load_state)

        self.open_file_dialog_warning_1 = SurfDisplay(t.F30.render("La fenêtre de choix de fichier est déjà ouverte !","red"),(640,400))
        self.open_file_dialog_warning_2 = SurfDisplay(t.F30.render("Fermez d'adord la fenêtre de choix de fichier !","red"),(640,400))
        self.show_file_dialog_warning = 0

    def load_pkl(self,filepath:str):
            self.show_file_dialog_warning=0
            sucess = load_sim_file(filepath)
            if sucess:
                self.current_load_state = LOADING_SIM
            self.is_last_file_invalid = not sucess
            self.is_load_successful = sucess

    def load_json(self,filepath:str):
            self.show_file_dialog_warning=0
            if filepath!=None:
                sucess = load_json_file(filepath)
                if sucess:
                    self.current_load_state = STARTING_SIM
                    self.load_current_load_state()

    def load_current_load_state(self):
        if self.current_load_state == STARTING_SIM_RANDOM:
            Data.sim_type = "Aléatoire"
        self.state = self.current_load_state

    def load_menu(self):
        Save_va.reinit()
        self.is_last_file_invalid = False
        self.is_load_successful = False
        self.current_load_state = STARTING_SIM_RANDOM
        pygame.event.clear()
        self.state = IN_MAIN_MENU

    def _reload_keybinds_displays(self):
        self.settings_dynamic_surfs = [
            SurfDisplay(fonts.F20(get_btn_name(self.keybinds["quit"])),pygame.Rect(750,282,0,0)),
            SurfDisplay(fonts.F20(get_btn_name(self.keybinds["fullscreen"])),pygame.Rect(750,339,0,0)),
            SurfDisplay(fonts.F20(get_btn_name(self.keybinds["switch_overlay"])),pygame.Rect(750,403,0,0)),
            SurfDisplay(fonts.F20(get_btn_name(self.keybinds["pause"])),pygame.Rect(750,464,0,0)),
            SurfDisplay(fonts.F20(("Oui" if Global.show_fps else "Non")),pygame.Rect(750,224,0,0))
        ]
    
    def handle_input(self):
        if self.state in MENU_STATES:

            if not self.state == IN_MENU_LOADING:self.objs_mgr.check_click()

            if self.state == IN_SIM_SETUP:
                CustomWindow.handle_events()

            if self.state == IN_MENU_LOADING:

                for event in get_events():

                    if event.type==pygame.DROPFILE:
                        filepath=event.file
                        self.load_pkl(filepath)

                    if event.type==pygame.MOUSEBUTTONDOWN:

                        if event.button == 1:
                            pos = event.pos 

                            for button in self.allButtons["load_buttons"]+Save_va.saves[:-1] if Save_va.trashmode else self.allButtons["load_buttons"]+Save_va.saves:
                                if button.rect.collidepoint(pos):
                                    button.clicked()
                            
                            if Save_va.saves_info_length >= 4 and 150 <= pos[0] <= 1150 and 520 <= pos[1] <= 540:
                                
                                if Save_va.scroll_barre[0] <= pos[0]-150 <= Save_va.scroll_barre[0]+Save_va.scroll_barre[2]:
                                    self.remember_pos_mouse = pos[0]
                                
                                else:
                                    Save_va.scroll_barre[0] = max(0, min(event.pos[0]-Save_va.START_X-Save_va.scroll_barre[2]/2, Save_va.S_max))
                                    for i,button in enumerate(Save_va.saves):
                                        button.rect.centerx = 200+240*i + (Save_va.scroll_barre[0]/Save_va.S_max) * (Save_va.C_right-Save_va.C_left)

                    if Save_va.saves_info_length >= 4 and event.type==pygame.MOUSEMOTION and self.remember_pos_mouse != None:
                        diff = (event.pos[0]-self.remember_pos_mouse)
                        Save_va.scroll_barre[0] = max(0, min(Save_va.scroll_barre[0] + diff, Save_va.S_max))
                        for i,button in enumerate(Save_va.saves):
                            button.rect.centerx = 200+240*i + (Save_va.scroll_barre[0]/Save_va.S_max) * (Save_va.C_right-Save_va.C_left)
                        self.remember_pos_mouse = event.pos[0]


                    if Save_va.saves_info_length >= 4 and event.type==pygame.MOUSEBUTTONUP and self.remember_pos_mouse != None:
                        self.remember_pos_mouse = None
                    
                    if event.type == pygame.MOUSEWHEEL:

                        diff = event.y * Save_va.scroll_speed
                        Save_va.scroll_barre[0] = max(0,min(Save_va.scroll_barre[0] - diff,Save_va.S_max))

                        for i,button in enumerate(Save_va.saves):
                            button.rect.centerx = 200+240*i + (Save_va.scroll_barre[0]/Save_va.S_max) * (Save_va.C_right-Save_va.C_left)
            
            elif self.state == IN_SETTINGS:
                for event in get_events():
                    if event.type==pygame.MOUSEBUTTONDOWN:
                        for keybind in self.settings_rebind_rects:
                            if keybind[1].collidepoint(event.pos):
                                if keybind[0]=="fps":
                                    Global.show_fps = not Global.show_fps
                                    self.settings_dynamic_surfs[4].surf = fonts.F20(("Oui" if Global.show_fps else "Non"))
                                else:
                                    self.currently_rebinding = keybind[0]
                                    self.rebinding = True
                                break
                        else:
                            self.currently_rebinding = None
                            self.rebinding=False

                    if event.type == pygame.KEYDOWN:

                        if self.currently_rebinding!=None and (event.key not in self.keybinds.values() or event.key==self.keybinds[self.currently_rebinding]):
                            self.keybinds[self.currently_rebinding]=event.key
                            Settings.save()
                            self._reload_keybinds_displays()
                            self.currently_rebinding = None
                            self.rebinding = False

    def update(self):
        if self.state in MENU_STATES:

            if self.state == LOADING_MENU:

                self.load_menu()

            else:
                while not Save_va.pending_main_thread_actions.empty():
                    action = Save_va.pending_main_thread_actions.get()
                    action()
                self.objs_mgr.update()
 

    def draw(self):
        if self.state in MENU_STATES:
            if self.state == IN_MAIN_MENU:
                self.screen.blit(self.main_menu_background, (0, 0))
            else:
                self.screen.blit(self.menu_background, (0, 0))
            self.objs_mgr.draw()

        if self.state == IN_MENU_LOADING:
            Save_va.display()

        if self.state == IN_SIM_SETUP:
            CustomWindow.display()
            self.objs_mgr.draw()

 
    def run(self):
        self.run_fcts(MENU_STATES,self.handle_input,self.update,self.draw)


if __name__ == "__main__":
    Global.state = IN_MAIN_MENU
    menu=Menu()
    menu.run()
    quit()