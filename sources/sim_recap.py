#Projet : The Descent
#Auteurs : Ahmed-Adam REZKALLAH, Noé SAMUEL

from utils import*
from csv_export import Data

class SimRecap(Runable):
    def __init__(self):
        Data.erase_memory()
        self.images=[]
        self.current=0
        center_y = self.screen.get_height() // 2
        center_x = self.screen.get_width() // 2
        size = (60, 60)
        font = Font(40)

        self.buttons = [Button((35+size[0]//2+10,center_y),"menu/Bouton_Graphs_FlecheGauche",lambda:self.change_image(-1)),
                        Button((self.screen.get_width()-35-size[0]//2-10,center_y),"menu/Bouton_Graphs_FlecheDroite",lambda:self.change_image(1)),
                        Button((center_x,670),"menu/Bouton_Graphs_Save",Data.shutil_to_permanent),
                        Button((1160,640),"menu/Bouton_Menu_MenuPrincipalGris",IN_MAIN_MENU)]


    def change_image(self, delta: int):
        if not self.images:
            return
        self.current = (self.current + delta) % len(self.images)

    def load_images(self):
        tempdir=os.path.abspath(os.sep.join(["data","simulations","csv","temp"]))

        Data.draw_all_spe_graph(os.sep.join(["data","simulations","csv","Donnees_Derniere_Simu_Analysee.csv"]))

        def scale_image(img,max_width,max_height):
            w,h=img.get_size()
            scale=min(max_width/w,max_height/h)
            new_size=(int(w*scale),int(h*scale))
            return pygame.transform.smoothscale(img,new_size)
        
        for file in sorted(os.listdir(tempdir)):
            path=os.path.join(tempdir,file)
            img=pygame.image.load(path).convert_alpha()
            img=scale_image(img,800,600)
            self.images.append(img)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type==pygame.MOUSEBUTTONDOWN:
                for btn in self.buttons:
                    btn.check_click(event.pos)

            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_LEFT:
                    self.current=(self.current-1)%len(self.images)
                if event.key==pygame.K_RIGHT:
                    self.current=(self.current+1)%len(self.images)

    def update(self):
        for btn in self.buttons:
            btn.update()

    def draw(self):
        self.screen.fill((155,200,175))
        if not self.images:return
        img=self.images[self.current]
        rect=img.get_rect(center=(self.screen.get_width()//2,self.screen.get_height()//2-40))
        self.screen.blit(img,rect)
        for btn in self.buttons:
            btn.draw()

    def run(self):
        self.load_images()
        Data.export_data()
        self.run_fcts([IN_SIM_RECAP],self.handle_input,self.update,self.draw)
        Data.erase_memory()

if __name__=="__main__":
    Global.state=IN_SIM_RECAP
    try:
        sim_recap=SimRecap()
        sim_recap.run()
    except Exception as e:print(e)
    finally:
        Data.erase_memory()
        quit()