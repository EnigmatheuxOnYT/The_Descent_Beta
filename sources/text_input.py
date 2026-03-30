#Projet : The Descent
#Auteurs : Ahmed-Adam REZKALLAH, Noé SAMUEL

from utils import *

class _TextInput_base(Runable):
    def __init__(self):
        x,y = 700,400

        win_bg_surf = pygame.image.load("data/assets/menu/PopUp_Menu_SauvegardeSimulation.png").convert()

        self.input_rect = input_rect = pygame.Rect(0,0,450,70)
        self.input_rect.center = input_rect.center = (x/2,y/2)
        self.win_bg = SurfDisplay(win_bg_surf,self.screen.get_rect().center)
        self.font = Font(40)
        def done_btn_effect():self.done=True
        def cancel_btn_effect():self.cancel=True
        self.done_button = Button((x/3+self.win_bg.pos.left-10,3*y/4+self.win_bg.pos.top+30),"menu/Bouton_Menu_Terminer",done_btn_effect)
        self.cancel_button = Button((2*x/3+self.win_bg.pos.left+10,3*y/4+self.win_bg.pos.top+30),"menu/Bouton_Menu_Annuler",cancel_btn_effect)
        
        self.max_x = input_rect.width-5
        self.cursor = pygame.Surface((2,self.font.base_font.get_height()))
        self.cursor.fill("black")
        self.cursor_rect=self.cursor.get_rect(centery=self.input_rect.height/2)


    def __call__(self,info_txt:str="",text_checker:Callable[[str],bool]=lambda txt:True)->None|str:
        self.info_text = info_txt
        self.info_display = SurfDisplay(self.font.render(info_txt),(self.screen.get_width()/2,self.screen.get_height()/2-100))
        self.text_checker = text_checker
        self.done = False
        self.done_checked = False
        self.cancel = False
        self.result=""
        self.cursor_pos = 0
        self.last_move = 0
        pygame.key.start_text_input()
        self.run()
        pygame.key.stop_text_input()
        return None if self.cancel else self.result
    
    def handle_input(self):
        for event in get_events():
            if event.type==pygame.TEXTINPUT:
                txt=event.text
                self.result=self.result[:self.cursor_pos]+txt+self.result[self.cursor_pos:]
                self.cursor_pos+=len(txt)
            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_RETURN:
                    self.done=True
                elif event.key==pygame.K_BACKSPACE:
                    self.result=self.result[:max(self.cursor_pos-1,0)]+self.result[self.cursor_pos:]
                    self.cursor_pos=max(self.cursor_pos-1,0)
                    self.last_move=ticks()
                elif event.key==pygame.K_DELETE:
                    self.result=self.result[:self.cursor_pos]+self.result[min(self.cursor_pos+1,len(self.result)):]
                    self.last_move=ticks()
                elif event.key==pygame.K_LEFT:
                    self.cursor_pos=max(self.cursor_pos-1,0)
                    self.last_move=ticks()
                elif event.key==pygame.K_RIGHT:
                    self.cursor_pos=min(self.cursor_pos+1,len(self.result))
                    self.last_move=ticks()
                elif event.key in (pygame.K_UP,pygame.K_PAGEUP,pygame.K_HOME):
                    self.cursor_pos=0
                    self.last_move=ticks()
                elif event.key in (pygame.K_DOWN,pygame.K_PAGEDOWN,pygame.K_END):
                    self.cursor_pos=len(self.result)
                    self.last_move=ticks()
                elif event.key == pygame.K_ESCAPE:
                    self.cancel = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.done_button.check_click(event.pos)
                self.cancel_button.check_click(event.pos)

    def update(self):
        self.done_button.update()
        self.cancel_button.update()
        if self.done:
            self.done_checked = self.done = self.text_checker(self.result)
            if not self.done_checked:self.info_display.surf=self.font.render(self.info_text,"red")

    def draw(self):
        surf = pygame.Surface(self.input_rect.size)
        surf.fill("white")
        w,h = self.font.base_font.size(self.result[:self.cursor_pos])
        if w+5>self.max_x:
            self.cursor_rect.centerx=self.max_x
        else:
            self.cursor_rect.centerx=w+5
        txt_surf = self.font.render(self.result)
        txt_rect = txt_surf.get_rect(midleft=(self.cursor_rect.centerx-w,self.input_rect.height/2))
        surf.blit(txt_surf,txt_rect)
        if ticks()%1000>500 or ticks()-self.last_move<500:
           surf.blit(self.cursor,self.cursor_rect)
        self.win_bg.surf.blit(surf,self.input_rect)
        self.win_bg.draw()
        self.done_button.draw()
        self.cancel_button.draw()
        self.info_display.draw()


    def run(self):
        while self.running and not self.done and not self.cancel:
            self._handle_base_inputs(disable_fullscreen=True)
            self.handle_input()
            self.update()
            self.draw()
            self._refresh_screen()

TextInput=_TextInput_base()

if __name__ == "__main__":
    print(TextInput())
    quit()