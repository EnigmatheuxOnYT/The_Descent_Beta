#Projet : The Descent
#Auteurs : Ahmed-Adam REZKALLAH, Noé SAMUEL

import multiprocessing as mp#on import multiprocess pr ne pas uttiliser threading
import math
import pygame

class LoadingScreen:
    def __init__(self, stop_event):
        pygame.init() #init de la fenêtre de chargement
        self.screen = pygame.display.set_mode((1280,720)) #la même taille que l'autre
        pygame.display.set_caption("Chargement...")
        self.clock = pygame.time.Clock() #son horloge indépendante de l'autre pr son framerate

        #repris de loading_screen
        self.surf = pygame.Surface((500,100))
        self.surf.fill((0,0,0))
        self.surf_rect = self.surf.get_rect(bottomleft=(0,self.screen.get_height()))

        wheel_local = (60,40)
        pygame.draw.circle(self.surf,"white",wheel_local,30) #rond blanc
        pygame.draw.circle(self.surf,"black",wheel_local,27) #rond noir plus petit pr faire un cercle blanc

        #converti pr être au bon endroit sur l'écran (en bas à guauche)
        self.wheel_center = (self.surf_rect.left+wheel_local[0],self.surf_rect.top+wheel_local[1])

        #valeurs pr le rond noir qui cachera le cercle blanc (effet de rotation)
        self.angle = 0
        self.radius = 30
        self.current_secondary_circle_center = self.wheel_center

        #le text Cahrgement à côté du cercle
        loading_txt = pygame.font.Font(None,40).render("Chargement...",True,(255,255,255))
        txt_pos = (120,self.screen.get_height()-70) #pos sur l'écran
        self.loading_txt = (loading_txt,txt_pos)

        self.stop_event = stop_event #store l'event qui permet d'arréter le tt

    def update(self):#adapté de loading_screen
        self.current_secondary_circle_center = (self.wheel_center[0]+math.cos(self.angle)*self.radius,self.wheel_center[1]+math.sin(self.angle)*self.radius)#équivaut ce qu'on faisait avec movement mais dcp c plus rapide puisqu'on l'importe pas 2 fois
        self.angle += math.pi/30
        
    def draw(self):
        self.screen.fill((0,0,0))#pr reset à chaque frame
        self.screen.blit(self.surf, self.surf_rect)#cercle banc
        self.screen.blit(*self.loading_txt)#sinon on voit pas "chargement..."
        dot_radius = 30 #on peut l'agrandir pr retirer une plus grand portion du cercle blanc
        pygame.draw.circle(self.screen,"black",self.current_secondary_circle_center,dot_radius)#le rond noir qui tourne sur le cercle blanc (effet de rotation)

    def loop(self): #j'uttilise pas runable pcq l'arrèt est plus particulier et indépendant du prog princ. dcp je veux pas créer de prob. sup.
        while not self.stop_event.is_set(): #continu tant qu'on lui a pas dit que ct terminé
            for event in pygame.event.get():
                if event.type == pygame.QUIT:#à noter on peut switch avec un quit global si on veux que tt s'arrète si l'utt ferme la fen^tre de chargement
                    self.stop_event.set() #si l'utt. veux juste fermer la fenêtre de chargement ça perturbera pas le reste du programe
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60) #60 fps

        pygame.quit() #pr arréter la fenêtre pygame
        

def loading_process(stop_event):#le target du multiprocessing
    screen = LoadingScreen(stop_event) #init
    screen.loop() #le loading screen en action
    

if __name__ == "__main__":
    #à mettre avant le code qu'on veut run en background
    mp.set_start_method("spawn",force=True)
    stop_event = mp.Event() #stop_event.is_set <=> False
    loader = mp.Process(target=loading_process,args=tuple([stop_event]),daemon=True) #pcq args veut un tuple; l'autre option c (stop_event,) mais je trouve moins compréhensible
    loader.start() #on lance la fenêtre pygame de chargement
    
    #pr test
    import time
    for i in range(10):
        print(f"Chargement {i}")#visuel
        time.sleep(1)
        
    #pr arréter la fenêtre de chargement
    stop_event.set() #après ça stop_event.is_set <=> True
    loader.join()
    print("Chargement Fini") #plus visuel
    quit()