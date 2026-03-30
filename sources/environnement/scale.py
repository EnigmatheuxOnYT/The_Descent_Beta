#Projet : The Descent
#Auteurs : Ahmed-Adam REZKALLAH, Noé SAMUEL

import math

units = ("ticks","seconds","frames","time_format","units","meters","kph","upf")

def convert(value,base_unit,to)->int|dict[str,int]:
    def pygame_ticks_to_sim_seconds(ticks):
        return ticks*9/5 # càd que 1 ms dans la vraie vie = 1/180000 s dans la simu d'après notre échelle de 1 min dans la vraie vie = 0,33 sec de simulation
        # pour rappel : 1 min = 60 000 ms
        
    def sim_seconds_to_pygame_ticks(seconds):
        return seconds*5/9

    def format_seconds(seconds):
        return {"j":int(seconds//86400), "h":int(seconds%86400//3600), "m":int(seconds%3600//60), "s":int(seconds%60)}

    def unformat_seconds(temps:dict):
        return temps["j"]*86400+temps["h"]*3600+temps["m"]*60+temps["s"]

    def pygame_frames_to_pygame_ticks(frames):
        return 50*frames/3 #car 1 frame = 1/60 seconds (à 60 FPS) et donc 1 frame = 16,666... ticks = 16,666... ms

    def pygame_ticks_to_pygame_frames (ticks):
        return math.ceil(3*ticks/50)

    def sim_units_to_real_meters(units):
        return units/100

    def real_meters_to_sim_units(meters):
        return 100*meters

    def real_kph_to_sim_upf(kph):
        return kph/72

    def convert_time(val,base,to):
        if base == "seconds":
            t_val = sim_seconds_to_pygame_ticks(val)
        elif base == "frames":
            t_val = pygame_frames_to_pygame_ticks(val)
        elif base == "time_format":
            t_val = unformat_seconds(val)
            t_val = sim_seconds_to_pygame_ticks(t_val)
        elif base == "ticks":
            t_val = val
        else:raise TypeError()
        if to == "seconds":
            return pygame_ticks_to_sim_seconds(t_val)
        elif to == "frames":
            return pygame_ticks_to_pygame_frames(t_val)
        elif to == "time_format":
            seconds = pygame_ticks_to_sim_seconds(t_val)
            return format_seconds(seconds)
        elif to == "ticks":
            return t_val
        else:raise TypeError()
    
    def convert_dist(val,base,to):
        if base=="units" and to == "meters":
            return sim_units_to_real_meters(val)
        elif base=="meters" and to == "units":
            return real_meters_to_sim_units(val)
        else:raise TypeError()
        
    if base_unit in ("seconds","ticks","frames","time_format") and to in ("seconds","ticks","frames","time_format"):
        return convert_time(value,base_unit,to)
    elif base_unit in ("units","meters") and to in ("units","meters"):
        return convert_dist(value,base_unit,to)
    elif base_unit=="kph" and to=="ups":
        return real_kph_to_sim_upf(value)
    else:raise TypeError()