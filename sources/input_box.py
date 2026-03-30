# Projet : The Descent
# Auteurs : Ahmed-Adam REZKALLAH, Noé SAMUEL

from utils import *
from typing import Literal,Callable

filters=Literal["any","digits","alpha_char"]

class Input_box(Runable):
    def __init__(self,pos:Point,size:tuple[int,int],filter:filters="any",max_len:int|None=None):
        x,y=pos

        self.input_rect=pygame.Rect(0,0,*size)
        self.input_rect.center=(x,y)

        self.font=Font(40)

        self.filter=filter
        self.max_len=max_len

        self.max_x=self.input_rect.width-5

        self.cursor=pygame.Surface((2,self.font.base_font.get_height()))
        self.cursor.fill("black")
        self.cursor_rect=self.cursor.get_rect(centery=self.input_rect.height/2)

        self.selected_all = False
        self.result:str=""
        self.cursor_pos:int=0
        self.last_move:int=0
        self.focus:bool=False

    def _accept_char(self,ch:str)->bool:
        if self.filter=="alpha_char":
            return ch.isalpha()
        elif self.filter=="digits":
            return ch.isdigit() or (ch=="." and "." not in self.result)
        return True

    def handle_input(self,event:pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button==1:
            if self.input_rect.collidepoint(event.pos):
                if not self.focus:
                    self.focus = True
                    self.selected_all = True
                else:
                    self.selected_all = not self.selected_all
            else:
                self.focus = False
                self.selected_all = False
            return
        
        if not self.focus:
            return
        
        if event.type == pygame.TEXTINPUT:
            txt=event.text
            filtered="".join(c for c in txt if self._accept_char(c))

            if self.max_len is not None:
                allowed=self.max_len-len(self.result)
                if allowed<=0:filtered=""
                else:filtered=filtered[:allowed]

            if filtered:
                if self.selected_all:
                    self.result = filtered
                    self.cursor_pos = len(filtered)
                    self.selected_all = False
                else:
                    self.result = self.result[:self.cursor_pos] + filtered + self.result[self.cursor_pos:]
                    self.cursor_pos += len(filtered)
    
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.result=self.result[:max(self.cursor_pos-1,0)]+self.result[self.cursor_pos:]
                self.cursor_pos=max(self.cursor_pos-1,0)
                self.last_move=ticks()

            elif event.key == pygame.K_DELETE:
                self.result=self.result[:self.cursor_pos]+self.result[min(self.cursor_pos+1,len(self.result)):]
                self.last_move=ticks()

            elif event.key == pygame.K_LEFT:
                self.cursor_pos=max(self.cursor_pos-1,0)
                self.last_move=ticks()

            elif event.key == pygame.K_RIGHT:
                self.cursor_pos=min(self.cursor_pos+1,len(self.result))
                self.last_move=ticks()

            elif event.key in(pygame.K_UP,pygame.K_PAGEUP,pygame.K_HOME):
                self.cursor_pos=0
                self.last_move=ticks()

            elif event.key in(pygame.K_DOWN,pygame.K_PAGEDOWN,pygame.K_END):
                self.cursor_pos=len(self.result)
                self.last_move=ticks()

            elif event.key == pygame.K_ESCAPE:
                self.focus=False

    def update(self):
        pass

    def draw(self):
        surf=pygame.Surface(self.input_rect.size,pygame.SRCALPHA)
        surf.fill("white")
        

        if self.selected_all:
            pygame.draw.rect(surf, (180, 200, 255), surf.get_rect())

        w,h=self.font.base_font.size(self.result[:self.cursor_pos])
        
        self.cursor_rect.centerx=self.max_x if w+5>self.max_x else w+5
        
        txt_surf=self.font.render(self.result)
        txt_rect=txt_surf.get_rect(midleft=(self.cursor_rect.centerx-w,self.input_rect.height/2))
        surf.blit(txt_surf,txt_rect)

        if self.focus and(ticks()%1000>500 or ticks()-self.last_move<500):
            surf.blit(self.cursor,self.cursor_rect)
        
        Global.screen.blit(surf,self.input_rect)

if __name__=="__main__":
    class TestScreen(Runable):
        def __init__(self):
            self.tb1=Input_box((400,250),(250,40),filter="any",max_len=20)
            self.tb2=Input_box((400,320),(250,40),filter="digits",max_len=10)
            self.submit_btn=Button((400,400),(200,50),"submit","black",Font(30),"red",self.on_submit)

        def on_submit(self):
            print("txt1:",self.tb1.result)
            print("txt2:",self.tb2.result)

        def mainloop(self):
            while self.running:
                for event in get_events():
                    self._handle_base_inputs(disable_fullscreen=True)
                    self.tb1.handle_input(event)
                    self.tb2.handle_input(event)
                    if event.type == pygame.QUIT:pygame.quit()
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button==1:self.submit_btn.check_click(event.pos)

                self.tb1.update()
                self.tb2.update()
                self.submit_btn.update()

                Global.screen.fill((40,40,40))

                self.tb1.draw()
                self.tb2.draw()
                self.submit_btn.draw()

                self._refresh_screen()
                self.clock.tick(self.fps)
                
    TestScreen().mainloop()
