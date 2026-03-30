#Projet : The Descent
#Auteurs : Ahmed-Adam REZKALLAH, Noé SAMUEL

from utils import *
import threading

class LoadingScreen(Runable):
    def __init__(self,states:list[GameState]):
        loading_txt = fonts.F40.render("Chargement...","white")
        self.wheel_center=(60,660)
        if os_name=="Windows":
            self.surf=pygame.Surface((500,100))
            self.surf.fill((0,0,0))
            self.surf_rect = self.surf.get_rect(bottomleft=self.screen.get_rect().bottomleft)
            wheel_center = (60,40)
            txt_midleft = (120,40)
            pygame.draw.circle(self.surf,"white",wheel_center,30)
            pygame.draw.circle(self.surf,"black",wheel_center,28)
            self.surf.blit(loading_txt,loading_txt.get_rect(midleft=txt_midleft))
            self.current_angle=0
            self.current_secondary_circle_center = (100,self.screen.get_height()-50)
            self.allowedstates=states
            self.thread = threading.Thread(target=self.loop,name="Loading screen thread",daemon=True)
        elif os_name=="Darwin":
            self.screen.fill((0,0,0))
            self.screen.blit(loading_txt,loading_txt.get_rect(midleft=(120,660)))
            pygame.draw.circle(self.screen,"white",self.wheel_center,30)
            pygame.draw.circle(self.screen,"black",self.wheel_center,28)
            pygame.display.flip()

    
    def update(self):
        vect=Movement(length=30,direction=self.current_angle)
        self.current_secondary_circle_center=self.wheel_center+vect
        self.current_angle+=math.pi/30


    def draw(self):
        self.screen.blit(self.surf,self.surf_rect)
        pygame.draw.circle(self.screen,"black",self.current_secondary_circle_center,30)
    
    def loop(self):
        while self.running and self.state in self.allowedstates:
            self._handle_base_inputs()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
    
    def run(self):
        if os_name == "Windows":self.thread.start()

if __name__=="__main__":
    LoadingScreen([LOADING_MENU]).run()
    quit()