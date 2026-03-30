#Projet : The Descent
#Auteurs : Ahmed-Adam REZKALLAH, Noé SAMUEL

import pygame
import time
import os
from utils import*

#on peut rajouter des couleurs si nécessaire, j'ai juste mis les couleurs de base
NAMED_COLORS={"black":(0,0,0),"white":(255,255,255),"red":(255,0,0),"green":(0,255,0),"blue":(0,0,255),"yellow":(255,255,0)}

#convertis un str en tuple RGB
def get_color(value:str) -> tuple[int,int,int]:
    value = value.strip() #on retire les espaces autours (au cas ou)

    if value.startswith("(") and value.endswith(")"): #si c'est un str en tuple
        nums = value[1:-1].split(",")
        if len(nums)!=3: 
            print(f"Entered RGB incorect, must be a tuple of 3 int value is :{value}")
            return (255,255,255)
        try:
            return tuple(int(n.strip()) for n in nums)
        except ValueError: #ce sera blanc si on a fait une erreur dans le .txt
            return (255,255,255)
        
    return NAMED_COLORS.get(value.lower(),(255,255,255)) #si c une couleur

def smart_split(tag_str:str) -> list[str]:
    parts = []
    current = ""
    depth = 0

    for char in tag_str:
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1

        if char == "," and depth == 0:
            parts.append(current.strip())
            current = ""
        else:
            current += char

    if current:
        parts.append(current.strip())

    return parts

def parse_style_attrs(tag_str:str,active_style:dict[str,object]) -> dict[str,object]:
    new_style = active_style.copy()

    if not tag_str: #si y'a pas de nouveau style, c le mm qu'st déjà actif
        return new_style
    
    #on sépart le str par les virgule (puisque c comme ça que doit être fait le style dans les balises du .txt)
    parts = smart_split(tag_str)

    for p in parts:
        if "=" not in p: #si y'a pas de = alors ce n'est pas valid: skip
            print(f"Element invalide: {p} , éléments: {parts}")
        else:
            key,val = p.split("=",1)
            key = key.strip().upper()
            val = val.strip().strip('"').strip("'")

            if key=="FONT":
                try:
                    new_style["size"]=int(val)
                except ValueError:
                    pass

            elif key=="COLOR":
                new_style["color"]=get_color(val)

    return new_style

def sep_text_tag(text:str) -> list[tuple[str]]:
    segments = []
    i = 0

    while i<len(text):
        if text[i]=="<":
            j = text.find(">",i)

            if j==-1:#si on a pas de balise fermante
                segments.append(("text",text[i:]))
                break

            tag_content=text[i+1:j].strip()
            segments.append(("tag",tag_content))
            i = j+1

        else:
            j = text.find("<",i)

            if j==-1:#si y'a pas de balise ouvrante c que du text
                segments.append(("text",text[i:]))
                break

            segments.append(("text",text[i:j]))
            i=j

    return segments

#le text en entrée est écrit en pseudo-html ducoup il faut l'interpréter avant de l'afficher
def read_styled_txt(text:str) -> tuple[list[tuple[str,dict[str,object]]],str]:
    segments = sep_text_tag(text)

    default_style={"size":24,"color":(255,255,255)}#on défini un style par défault au cas ou
    style_stack=[default_style]

    in_final=False
    final_parts=[] #list les élément avec la balise <**></**> qui seront affichés à part, en dernier
    spans=[] #list les autres éléments

    current_style=default_style

    for kind,content in segments:
        if kind=="tag":
            if content.startswith("/"):#balise fermante
                tag_name=content[1:].strip().lower()
                if tag_name=="**":#balise spécial fin
                    in_final=False
                else:
                    if len(style_stack)>1:
                        style_stack.pop()
                        current_style=style_stack[-1] #on change le style au dernier style avant la balise concernée
            else:
                parts=content.split(None,1)
                tag_name=parts[0].strip().lower()
                attrs=parts[1] if len(parts)>1 else ""

                if tag_name=="**": #balise spécial fin
                    in_final=True
                else: #nouveau style
                    new_style=parse_style_attrs(attrs,style_stack[-1])
                    style_stack.append(new_style)
                    current_style=new_style

        elif kind=="text":
            if not content:
                continue

            if in_final:#text dan la balise spécial
                final_parts.append(content)

            else:
                parts=content.split("\n")
                for idx,part in enumerate(parts):
                    if len(part)==0:
                        spans.append(("",current_style.copy()))
                    if part:
                        spans.append((part,current_style.copy()))
                    if idx<len(parts)-1:
                        spans.append(("\n",current_style.copy()))

    final_message="".join(final_parts).strip()

    return spans,final_message

#converti pr l'affichage
def convert_spans(spans:tuple[str,dict[str,object]],screen:pygame.Surface,line_spacing:int=4) -> tuple[list[tuple[pygame.Surface,(int,int)]],int,int]:
    width,height=screen.get_size()

    lines=[]
    current_line=[]
    x_cursor=0

    def new_font(size):return Font(size)

    for text,style in spans:
        if text=="\n":#saut de ligne
            if current_line:
                lines.append(current_line)
                current_line=[]
                x_cursor=0
            else:
                lines.append([])

        else:
            font=new_font(style["size"])
            color=style["color"]
            words=text.split(" ")

            for w_index,word in enumerate(words):
                word_text=word
                if w_index<len(words)-1:
                    word_text+=" "
                word_surface=font.render(word_text,color)
                w_width,w_height=word_surface.get_size()

                if x_cursor+w_width>width:#si c'est trop long:ligne suivante
                    lines.append(current_line)
                    current_line=[]
                    x_cursor=0
                current_line.append((word_surface,x_cursor,w_height))
                x_cursor+=w_width

    if current_line:#évite une ligne vide suplémentaire à la fin
        lines.append(current_line)

    rendered=[]
    total_height=0

    #calcule de la hauteur
    for line in lines:
        line_height=max((entry[2] for entry in line),default=0)
        total_height+=line_height+line_spacing

    base_y=height + 50
    y_cursor=base_y

    for line in lines:
        line_height = max((entry[2] for entry in line),default=0)

        line_width = sum(surf.get_width() for surf,_,_ in line)

        start_x = (width-line_width)//2

        x_cursor=start_x
        for surf,_,_ in line:
            rendered.append((surf,(x_cursor,y_cursor)))
            x_cursor+=surf.get_width()

        y_cursor+=line_height + line_spacing

    return rendered,total_height,base_y

def run_credits(screen,filename,background_color=(0,0,0),scroll_speed=60,final_duration=5.0):
    with open(filename,"r",encoding="utf-8") as f:
        raw_text=f.read()

    spans,final_message=read_styled_txt(raw_text)
    rendered_spans,total_height,base_y=convert_spans(spans,screen)
    
    width,height=screen.get_size()
    clock=pygame.time.Clock()
    offset=0.0
    running=True

    def skip_act():
        nonlocal running
        running = False
    skip_button = Button((Global.screen.get_width()-60,685),(80,40),"Passer",(255,255,255),Font(24),(255,255,255),skip_act,crown_color=(0,0,0,0))

    phase="scroll"
    final_start_time=None
    
    while running:
        dt=clock.tick(60)/1000.0
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running = False
            elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                skip_button.check_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN):
                    skip_act()

        screen.fill(background_color)

        if phase=="scroll":
            offset+=scroll_speed*dt
            for surf,(x,y) in rendered_spans:
                draw_y=y-offset
                if draw_y+surf.get_height()>=0 and draw_y<=height:
                    screen.blit(surf,(x,draw_y))

            if (base_y+total_height)-offset<0:
                phase="final"
                final_start_time=time.time()

        if phase=="final":
            if final_message:
                font=Font(36)
                
                lines=final_message.split("\n")
                rendered_lines=[font.render(line,(255,255,255)) for line in lines]
                total_h=sum(s.get_height() for s in rendered_lines)+(len(rendered_lines)-1)*5
                y_cursor=(height-total_h)//2

                for surf in rendered_lines:
                    x=(width-surf.get_width())//2
                    screen.blit(surf,(x,y_cursor))
                    y_cursor+=surf.get_height()+5

            if time.time()-final_start_time>=final_duration:
                running = False

        skip_button.draw()

        pygame.display.flip()

if __name__=="__main__":
    pygame.init()
    screen=Global.screen
    pygame.display.set_caption("Demo crédits")

    sample_filename="data/credits/credits.txt"
    if not os.path.exists(sample_filename):
        sample_content=("<a FONT=28,COLOR=(255,255,255)>""The Descent\n""<b COLOR=\"yellow\">Developeur principal :</b> Ah\n\nmed\n""<b COLOR=\"red\">Artiste ?:</b> Noé\n""<b COLOR=\"green\">Music ?:</b> Erreur\n""</a>\n\n""<a FONT=22,COLOR=(200,200,255)>Remerciments spéciaux :\n""<b COLOR=\"yellow\">Toi, l'idiot qui a tout regardé !</b>\n""</a>\n\n""<**>Merci d'avoir simulé !\nA la prochaine.</**>")
        with open(sample_filename,"w",encoding="utf-8") as f:
            f.write(sample_content)

    running=True

    font=pygame.font.SysFont(None,36)
    msg=font.render("Credits terminés. Fermer la fenêtre.",True,(255,255,255))

    while running:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                run_credits(screen,sample_filename,background_color=(0,0,0),scroll_speed=60,final_duration=2.0)
        
        screen.fill((0,0,0))
        screen.blit(msg,msg.get_rect(center=screen.get_rect().center))
        pygame.display.flip()

    quit()
