#Projet : The Descent
#Auteurs : Ahmed-Adam REZKALLAH, Noé SAMUEL

#Fichier en partie (set_reg_value-delete_tree) crée avec l'aide d'IA (ChatGPT), il déclare l'application comme pouvant executer des .sim et des .simstat

from utils import *

linked_json_str=lambda sim_str,simstat_str:"""{
    "sim":"""+sim_str+""",
    "simstat":"""+simstat_str+""",
    "show":false
}"""
import json
import os

file_managing_folder = os.path.abspath("data/file_type_managing") + os.sep

if os_name == "Windows":
    import sys
    import winreg

    executable = sys.executable
    if os.path.exists(executable.replace("python.exe", "pythonw3.13.exe")):
        pythonw = executable.replace("python.exe", "pythonw3.13.exe")
    else:
        pythonw = executable.replace("python.exe", "pythonw.exe")
    python_exe = executable
    script_path = os.path.abspath("sources/argument_launcher.py") #script_path = os.path.abspath(__file__)[:-20]+"main.py"
    icon_folder_path = os.path.abspath("data/file_type_managing/assets")

    file_managing_folder = os.path.abspath("data/file_type_managing") + os.sep



    def set_reg_value(key, subkey, value):
        with winreg.CreateKey(key, subkey) as k:
            winreg.SetValueEx(k, None, 0, winreg.REG_SZ, value)


    def associate_file_extension(extension_no_point:str):
        extension = '.'+extension_no_point
        prog_id="MyApp.Fichier"+extension_no_point.upper()
        friendly_name="Sauvegarde Simulation" if extension_no_point=="sim" else "Paramètres Simulation"
        icon_path=icon_folder_path+extension_no_point+"\\.ico"
        set_reg_value(winreg.HKEY_CURRENT_USER,
                    rf"Software\Classes\{extension}",
                    prog_id)

        set_reg_value(winreg.HKEY_CURRENT_USER,
                    rf"Software\Classes\{prog_id}",
                    friendly_name)

        set_reg_value(winreg.HKEY_CURRENT_USER,
                    rf"Software\Classes\{prog_id}\DefaultIcon",
                    icon_path)

        set_reg_value(winreg.HKEY_CURRENT_USER,
                    rf"Software\Classes\{prog_id}\shell",
                    "open")

        set_reg_value(winreg.HKEY_CURRENT_USER,
                    rf"Software\Classes\{prog_id}\shell\open",
                    "Ouvrir")

        set_reg_value(winreg.HKEY_CURRENT_USER,
                    rf"Software\Classes\{prog_id}\shell\open\command",
                    f"\"{pythonw}\" \"{script_path}\" \"%1\"")


    def remove_file_association(extension_no_point:str):
        extension = '.'+extension_no_point
        prog_id="MyApp.Fichier"+extension_no_point.upper()
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER,
                            rf"Software\Classes\{extension}")
        except:
            pass

        import winreg

        def delete_tree(root, subkey):
            try:
                with winreg.OpenKey(root, subkey) as k:
                    while True:
                        try:
                            child = winreg.EnumKey(k, 0)
                            delete_tree(root, f"{subkey}\\{child}")
                        except OSError:
                            break
                winreg.DeleteKey(root, subkey)
            except:
                pass

        delete_tree(winreg.HKEY_CURRENT_USER,
                    rf"Software\Classes\{prog_id}")

    def link_sim():
        associate_file_extension("sim")

    def link_simstat():
        associate_file_extension("simstat")
        
    def unlink_sim():
        remove_file_association("sim")

    def unlink_simstat():
        remove_file_association("simstat")

    class FileTypeAssignScreen(Runable):
        def __init__(self):
            self.file_managing_path = file_managing_folder
            self.check_linked()
            txt = Font(30)("Voulez-vous associer cette application à l'exécution de fichiers .sim et .simstat ?")
            txt_rect=txt.get_rect(center=(640,360))
            self.surf_display = SurfDisplay(txt,txt_rect)
            def link():
                link_sim()
                link_simstat()
                self.rewrite_json(True,True)
                self.current="unlink"
            def unlink():
                unlink_sim()
                unlink_simstat()
                self.rewrite_json(False,False)
                self.current="link"
            self.buttons = {"link":Button((640,420),(630,60),"Associer .sim et .simstat à cette application","black",Font(30),"white",link),
                            "unlink":Button((640,420),(630,60),"Dissocier .sim et .simstat de cette application","black",Font(30),"white",unlink)
                            }
            
            self.current="link"
            if self.sim_linked and self.simstat_linked:
                self.current = "unlink"

            self.exit_button = Button((640,600),(100,50),"Terminé","black",Font(25),"white",IN_MAIN_MENU)

        def check_linked(self):
            linked_path = self.file_managing_path+"linked.json"
            if os.path.exists(linked_path):
                with open(linked_path) as f:
                    data = json.load(f)
                self.sim_linked = data["sim"]
                self.simstat_linked = data["simstat"]
                self.auto_open=data["show"]
                self.rewrite_json(data["sim"],data['simstat'])
            else:
                self.sim_linked = False
                self.simstat_linked = False
                self.rewrite_json(False,False)
                self.auto_open=True
        
        def rewrite_json(self,sim:bool,simstat:bool):
            sim_str = "true" if sim else "false"
            simstat_str = "true" if simstat else "false"
            json_str = linked_json_str(sim_str,simstat_str)
            with open(self.file_managing_path+"linked.json", "w") as f:
                f.write(json_str)
        
        def handle_input(self):
            if self.state == FILETYPES_ASSIGNATION:

                for event in get_events():
                    if event.type==pygame.MOUSEBUTTONDOWN:
                        if self.exit_button.rect.collidepoint(event.pos):
                            self.exit_button.clicked()
                        elif self.buttons[self.current].rect.collidepoint(event.pos):
                            self.buttons[self.current].clicked()
        
        def update (self):
            if self.state == FILETYPES_ASSIGNATION:

                self.buttons[self.current].update()
                self.exit_button.update()
        
        def draw(self):
            if self.state == FILETYPES_ASSIGNATION:
                self.screen.fill((155,200,175))
                self.surf_display.draw()
                self.buttons[self.current].draw()
                self.exit_button.draw()

        def run(self,auto_open=False):
            if (auto_open and self.auto_open) or not auto_open:
                self.run_fcts([FILETYPES_ASSIGNATION],self.handle_input,self.update,self.draw)
            else:
                self.state = LOADING_MENU

else:
    class FileTypeAssignScreen(Runable):
        def __init__(self):pass
        def run(self,auto_open=None):self.state=LOADING_MENU
        

if __name__ == "__main__":
    ecran_de_choix = FileTypeAssignScreen()
    Global.state = FILETYPES_ASSIGNATION
    ecran_de_choix.run()
    quit()
