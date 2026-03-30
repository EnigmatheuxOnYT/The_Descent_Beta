#Projet : The Descent
#Auteurs : Ahmed-Adam REZKALLAH, Noé SAMUEL

import sys
import os
os.chdir(os.path.abspath(__file__)[:-28])
from file_loader import load_json_file,load_sim_file
from main import *

if len(sys.argv)>=2:
    file_path:str=sys.argv[1]
    ext=file_path.split(".")[-1]
    sucess = False
    if ext in ["simstat","json"]:
        sucess = load_json_file(file_path)
        state = STARTING_SIM
    elif ext == "sim":
        sucess = load_sim_file(file_path)
        state = LOADING_SIM
    if sucess:
        try:
            simulator=Main()
            simulator.state = state
            simulator.run_fcts(RUNNING_STATES,simulator.update)
            pygame.quit()
        except:sucess=False
    if not sucess:
        running=True
        def quit():
            global running
            running=False
        def normal_launch():
            global running
            running = False
            simulator = Main()
            simulator.run()
        btn_quit=Button((640,450),(80,30),"Quitter","black",fonts.F22,"white",quit)
        btn_normal_launch=Button((640,490),(300,30),"Lancer le simulateur normalement","black",Font(18),"white",normal_launch)
        displays=[SurfDisplay(Font(30)("Ce fichier est invalide."),(640,300)),
                  SurfDisplay(Font(30)("Il a peut-être été corrompu, ou vient d'une version ancienne du logiciel."),(640,340)),
                  SurfDisplay(Font(30)("Version actuelle : "+version_string),(640,380)),
                  ]
        while running:
            for event in get_events():
                if event.type==pygame.MOUSEBUTTONDOWN and btn_quit.rect.collidepoint(event.pos):btn_quit.clicked()
                elif event.type==pygame.MOUSEBUTTONDOWN and btn_normal_launch.rect.collidepoint(event.pos):btn_normal_launch.clicked()
                elif event.type==pygame.QUIT:running=False
                elif (event.type ==pygame.KEYDOWN and event.key == Settings.keybinds["fullscreen"]):pygame.display.toggle_fullscreen()
            btn_quit.update()
            btn_normal_launch.update()
            Global.screen.fill((155,200,175))
            btn_quit.draw()
            btn_normal_launch.draw()
            for display in displays:display.draw()
            pygame.display.flip()
            UseScreen.clock.tick(UseScreen.fps)