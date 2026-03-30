#Projet : The Descent
#Auteurs : Ahmed-Adam REZKALLAH, Noé SAMUEL, Clément Roux--Bénabou


#importation des modules python
from random import random as rd
from environnement.objects import Animal,Food,world,FruitType
from environnement.ia.base import *
from utils import *

#renvoie True avec une probabilité égale à val ex: test_random(0.3) a 30% de chances de renvoyer True
def test_random(val:float):return rd()<val

#Change la valeur d'un nombre entre 0 et 1 en fonction du coefficient
def get_importance(values:list[tuple[float,float]]):
    num=den=0.0
    for val,coeff in values:
        num+=val*coeff
        den+=coeff
    return num/den

#Définition des types d'actions possibles pour un animal
ActionType = Literal[NoneAction,Move,Turn,Eat,Attack,Reproduce_a]
#Les valeurs associées à une action:
# -> pour Move : [min_acceleration, mid_acceleration, max_acceleration, min_turn, mid_turn, max_turn]
# -> pour Eat : Food
# -> pour Attack, Reproduce_a : Animal
ActionValue = Union[Animal,Food,Number] #Pour le mouvement, on a [min_acceleration,mid_acceleration,max_acceleration,min_turn,mid_turn,max_turn]
PossibleAction = tuple[ActionType,list[ActionValue],int] #Type d'action, array de valeurs représenté en liste, préférence parmi l'array(, importance - non présente dans l'objet mais ajoutée après coup pour le tri lignes 173 et 175)

_none_action = (NoneAction,[0],0) #action ne rien faire par défaut

class ObjectiveTypeError(TypeError):pass

def simulate_action(animal:Animal)->Action:
    """
    Renvoie l'action d'un animal en fonction de ses objectifs actuels et autres paramètes tels que le mouvement précédent de l'animal, son énergie etc.
    """

    #compare la direction actuelle à la direction de la cible
    def compare_moves_turn(move:Movement)->tuple[Number,Number]:
        """
        Compare move (Le vecteur représentant le déplacement de l'animal à sa destinantion) au mouvement précédent de l'animal
        et renvoie la modification de sa direction idéale pour atteindre sa destination. Valeur entre -1 et 1.
        """
        d1=animal.rad #Direction de l'animal
        d2=move.direction_rad #Direction (sens) du vecteur move

        
        diff=(d2 - d1 + math.pi) % (2*math.pi) - math.pi #Différence des angles dans l’intervalle [- π, π[

        #si la différence dépasse la capacité de rotation max
        if diff >= Animal.turn:
            return 1,diff
        if diff <= -Animal.turn:
            return -1,diff
        #sinon on normalise pour obtenir une valeur entre -1 et 1
        else:
            return diff/Animal.turn,diff
    
    #compare la vitesse actuelle à la distance de l’objectif
    def compare_moves_speed(move:Movement)->Number:
        """
        Compare move (Le vecteur représentant le déplacement de l'animal à sa destinantion) au mouvement précédent de l'animal
        et renvoie la modification de sa vitesse idéale pour atteindre sa destination. Valeur entre -1 et 1.
        """

        distance = move.length#Distance entre l'animal et sa destination
        speed=animal.speed#Vitesse de l'animal
        acceleration = Animal.acceleration*animal.max_speed#Acceleration de l'animal
        
        #Distance minimale que l'animal doit parcourir avant de s'arrêter + sa vitesse 
        n = math.ceil(speed/acceleration)
        min_dist = n*speed-(n-1)*n*acceleration/2 #Calcul avec sum([i for in range(n+1)]) = n*(n+1)/2 pour tout n naturel
        
        if distance >= min_dist+speed+acceleration:#Si l'objectif est loin
            return 1
        elif distance <= min_dist-speed: #Si l'objectif est trop proche pour s'arrêter à temps ou de justesse
            return -1
        else:
            dist_left = distance-min_dist
            if dist_left > speed-acceleration:
                return (dist_left-speed)/(acceleration) #Si l'objectif est trop près pour pouvoir accélerer au max mais trop loin pour qu'on doive ralentir au max
            return -1 #Si l'objectif est proche mais pas trop
        
    def get_action(objective:Objective)->PossibleAction:
        """
        Récupère l'action de l'animal correspondant à un objectif
        """

        #gère un objectif de type "aller à un point"
        def get_goto(objective:GoTo)->PossibleAction:
            """
            Récupère l'action de l'animal correspondant à un objectif GoTo
            """

            vect=Movement(point_1=animal.pos,point_2=objective.pos) #crée un vecteur représentant le déplacement de l'animal vers la position cible
            turnpref,diff=compare_moves_turn(vect) #calcule combien l'animal doit tourner pour viser la destination
            if turnpref in [-1,1]:
                min_dist = animal._circle_diameter*math.sin(diff) #Calcul de la distance minimale parcourue par l'animal s'il tourne au maximum mais continue d'avancer
                if min_dist>vect.length:
                    return Turn,[turnpref],0
            
            #on prépare un tableau de valeurs pour Move (combinaison rotation + vitesse)
            #Sinon on remplit values comme indiqué ligne 12 et pref avec :
            #   - la dizaine pour l'index (+1) parmi les trois premières valeurs de la modification d'angle optimale pour remplir l'objecitf
            #   - L'unité pour l'index (+1) parmi les trois dernières valeurs de la modification de vitesse optimale pour remplir l'objecitf
            if turnpref>=0:
                values=[0,0,turnpref]
                pref=30
            else:
                values=[turnpref,0,0]
                pref=10
            #on ajuste la vitesse selon la distance
            
            if turnpref not in [-1,1] and not objective.must_stop:
                speedpref = 1
            else:
                speedpref=compare_moves_speed(vect)
            if speedpref>=0:
                values+=[0,0,speedpref]
                pref+=3
            else:
                values+=[speedpref,0,0]
                pref+=1
            
            return Move,values,pref

        
        #objectif -> trouver de la nourriture
        def get_find(objective:Find)->PossibleAction:
            """
            Récupère l'action de l'animal correspondant à un objectif Find
            """
            if objective.current_subobjective!=None and objective.current_subobjective.type=="complete": #Si l'objectif doit être finalisé, alors l'animal remplit les conditions pour manger la nourriture
                obj = objective.current_object #la nourriture
                objective.completed = True
                return Eat,[obj],0
            elif objective.scouting: #si l’animal explore -> continue à chercher
                return get_scout(animal.scouting_objective)
            return _none_action #sinon il ne fait rien

        #objectif -> créer des affinités sociales
        def get_affinities(objective:MakeAffinities)->PossibleAction:
            """
            Récupère l'action de l'animal correspondant à un objectif MakeAffinities
            """
            if objective.current_subobjective!=None and objective.current_subobjective.type=="complete": #Si l'objectif doit être finalisé, alors l'animal remplit les conditions pour manger la nourriture
                objs = objective.current_object
                objective.completed = True
                return Socialize,[objs],0
            elif objective.scouting:
                return get_scout(animal.scouting_objective)
            return _none_action

        #pour se reproduire
        def get_reproduce(objective:Reproduce_o)->PossibleAction:
            """
            Récupère l'action de l'animal correspondant à un objectif Reproduce
            """
            if objective.current_subobjective!=None and objective.current_subobjective.type=="complete":
                objective.completed = True
                return Reproduce_a,[objective.current_object],0
            if objective.scouting:
                return get_scout(animal.scouting_objective)
            return _none_action
        
        def get_rest(objective:Rest)->PossibleAction:
            """
            Récupère l'action de l'animal correspondant à un objectif Rest
            """
            return Rest_a,[0],0

        #pour fuir (pas encore implémenté parce qu'il n'y a pas de prédateur)
        def get_flee(objective:Flee)->PossibleAction:
            """
            Récupère l'action de l'animal correspondant à un objectif Flee
            """
            vect = Movement(point_1=objective.animal.pos,point_2=animal.pos)
            vect.length=500
            return get_goto(GoTo(animal.pos+vect,must_stop=False))
        
        #pour attaquer une cible
        def get_kill(objective:Kill)->PossibleAction:
            """
            Récupère l'action de l'animal correspondant à un objectif Kill
            """
            if objective.current_subobjective!=None:
                if objective.current_subobjective.type=="complete":
                    return Attack,[objective.current_object],0
                elif objective.current_subobjective.type=="goto":
                    return get_goto(objective.current_subobjective)
            return _none_action
        
        #pour chercher qqch (parcour un pattern de points)
        def get_scout(objective:Scout)->PossibleAction:
            """
            Récupère l'action de l'animal correspondant à un objectif Scout
            """
            return get_goto(GoTo(objective.pattern[objective.current_index],must_stop=False))

        if objective==None:
            update_behaviour(animal)
            objective=animal.current_objective

        #si l’objectif possède un sous-objectif actif on le traite d’abord
        if objective.current_subobjective!=None and objective.current_subobjective.type!="complete":
            return get_action(objective.current_subobjective)
        #sinon on choisit selon le type d’objectif principal
        elif objective.type=="go_to":
            return get_goto(objective)
        elif objective.type=="find":
            return get_find(objective)
        elif objective.type=="kill":
            return get_kill(objective)
        elif objective.type=="flee":
            return get_flee(objective)
        elif objective.type=="affinities":
            return get_affinities(objective)
        elif objective.type=="reproduce":
            return get_reproduce(objective)
        elif objective.type == "scout":
            return get_scout(objective)
        elif objective.type=="rest":
            return get_rest(objective)
        else:raise ObjectiveTypeError(f"Type d'objectif {objective.type} inconnu")

            
    #conversion d'une PossibleAction en Move
    def extract_move_action(possible_action:PossibleAction)->Move:
        """
        Transforme PossibleAction de type Move en Move
        """
        length=min(max(animal.speed+(animal.max_speed*Animal.acceleration*possible_action[1][possible_action[2]%10+2]),0),animal.max_speed) #calcul de la nouvelle vitesse (longueur du vecteur de déplacement)
        direction=animal.last_move.direction_rad+(Animal.turn*possible_action[1][possible_action[2]//10-1])#calcul de la nouvelle direction (radians)
        m=Movement.from_length_direction(length,direction)#création d’un objet Movement représentant ce déplacement
        return Move(m) #on retourne l’action Move du mouvement

    def extract_other_action(possible_action:PossibleAction):
        """
        Transforme PossibleAction de type autre que Move en Action
        """
        return possible_action[0](possible_action[1][possible_action[2]])
    
    #Pour plus tard si l'importance ne dépend pas que de l'objectif
    """
    possible_actions : list[PossibleAction] = [(*_none_action,-2)] #Pour que l'animal soit certain de pouvoir faire qqch
    for objective in animal.objectives:
        if objective.current_subobjective!=None and objective.current_subobjective.type!="complete":
            possible_actions.append((*get_action(objective.current_subobjective),objective.importance))
        else:
            possible_actions.append((*get_action(objective),objective.importance))
    best=max(possible_actions,key=lambda pa:pa[3]) #Trie et renvoie l'action avec l'importance la plus élevée
    """
    #Pour l'instant plus opti, probablement final
    best = get_action(animal.current_objective)#c’est celui avec la plus grande importance pondéré
    #si c’est un déplacement : Move sinon : Eat, Attack, Reproduce...
    return extract_move_action(best) if best[0]==Move else extract_other_action(best)


def update_behaviour(animal:Animal)->None:
    """
    Met à jour les objectifs de l'animal en fonction de différents facteurs comme sa personnalité
    """


    #données de perception :ce que l’animal "voit"
    a_view = animal._get_in_view_animals()
    animal.update_hitbox()

    #permettent d’évaluer la faim, la fatigue, la vie(HP), etc
    p_e=max(animal.stamina/animal.max_stamina,0) #niveau d’énergie entre 0 et 1
    p_f=animal.metabolic_energy_kJ/animal.max_metabolic_energy_kJ #niveau de réserve de nourriture
    p_hp=animal.hp/animal.max_hp #niveau d'HP

    def generate_objectives():
        """
        Crée de nouveaux objectifs en fonction de ce que l'animal perçoit
        """
        for visible_animal in a_view:#pour tout les animaux dans le champ de vision de l'animal
            #vérifie si l’animal visible est un prédateur
            if visible_animal.species.name_shortcut in animal.species.predators:
                for objective in animal.objectives:
                    if objective.current_object == visible_animal:
                        break
                else:
                    animal.objectives.append(Flee(visible_animal)) #si c'est un prédateur on ajoute un objectif Flee (fuir)
    
    def update_objective_importance(objective:Objective):
        """
        Mets à jour l'importance d'un objectif en fonction de la personnalité de l'animal
        """
        #objectifs de type GoTo ou Scout ne doivent pas être "principaux"
        def update_go_to_imporance(objective:GoTo):raise ObjectiveTypeError("Un animal de doit pas avoir d'objectif GoTo comme principal")
        def update_scout_imporance(objective:Scout):raise ObjectiveTypeError("Un animal de doit pas avoir d'objectif Scout comme principal")
        def update_kill_imporance(objective:Kill):raise ObjectiveTypeError("Un animal de doit pas avoir d'objectif Kill comme principal")

        def update_find_imporance(objective:Find):
            #Met à jour l'importance de l'objectif en fonction de son trait "eater" et de son niveau de faim
            objective.importance = get_importance([(1-p_f,1),(animal.personnality["eater"],1)])
        
        def update_affinities_importance(objective:MakeAffinities):
            #Met à jour l'importance de l'objectif en fonction de son trait "sociable" et de son niveau de faim, de fatigue et de vitalité
            objective.importance = get_importance([(p_e,1/3),(p_f,1/3),(p_hp,1/3),(animal.personnality["sociable"],1)])
            
        def update_rest_importance(objective:Rest):
            #Met à jour l'importance de l'objectif en fonction de son trait "patient" et de son niveau de fatigue
            objective.importance = get_importance([(1-p_e,1),(animal.personnality["patient"],1)])
        
        def update_reproduce_imporance(objective:Reproduce_o):
            if animal.juvenile:#si l’animal est trop jeune pas de reproduction
                objective.importance = -1
            else:#sinon importance selon énergie et trait "reproductive"
                objective.importance = get_importance([(p_e,1/3),(p_f,1/3),(p_hp,1/3),(animal.personnality["reproductive"],1)])        
        
        def update_flee_imporance(objective:Flee):
            #Met à jour l'importance de l'objectif en fonction de son trait "fearful" de son niveau de vitalité et de celui de son adversaire
            objective.importance = get_importance([(1-p_hp,1/2),(objective.current_object.hp/objective.current_object.max_hp,1/2),(animal.personnality["fearful"],1)])
        
        #sélection de la bonne fonction selon le type de l’objectif
        if objective.type == "go_to":
            update_go_to_imporance(objective)
        elif objective.type == "find":
            update_find_imporance(objective)
        elif objective.type == "scout":
            update_scout_imporance(objective)
        elif objective.type == "affinities":
            update_affinities_importance(objective)
        elif objective.type == "reproduce":
            update_reproduce_imporance(objective)
        elif objective.type == "kill":
            update_kill_imporance(objective)
        elif objective.type == "flee":
            update_flee_imporance(objective)
        elif objective.type == "rest":
            update_rest_importance(objective)
        else:
            raise ObjectiveTypeError(f"Type d'objectif {objective.type} inconnu")

    def update_objective_state(objective:Objective):
        """
        Mets à jour l'etat d'un objectif
        """
        
        #pour Find
        def update_find_state(objective:Find):
            f_view = animal._get_in_view_foods()
            sub = objective.current_subobjective
            #si aucun sous-objectif ou si on explore (scouting)
            if sub == None or objective.scouting:

                for obj in f_view:#cherche d’abord la nourriture visible à l’écran
                    if obj.can_eat():
                        objective.current_subobjective = GoTo(obj.pos)
                        objective.current_object = obj
                        objective.scouting = False
                        break
                else:#si rien de visible on la cherche dans la mémoire
                    closest = None
                    closest_dist = None
                    for food in animal.memory.food_spots:
                        if food.can_eat() and food not in f_view and not animal.collide(food.hitbox):
                            distance = sqrdist(animal.pos,food.pos)
                            if closest_dist == None:
                                closest = food
                                closest_dist = distance
                            elif distance < closest_dist:
                                closest = food
                                closest_dist = distance
                    
                    if closest:
                        objective.current_subobjective = GoTo(closest.pos)
                        objective.current_object = closest
                        objective.scouting = False
                    else:#sinon on continue à explorer
                        for prey in a_view:
                            if prey.species.name_shortcut in objective.food_types:
                                objective.current_subobjective = Kill(prey)
                                objective.current_object=prey
                                objective.scouting=False
                                break
                        else:
                            if not objective.scouting:
                                objective.switch_scouting()
            
            #si le sous-objectif est un "GoTo"
            elif sub.type =="go_to":
                #si l’objet ciblé n’a plus de fruits -> on recommence à chercher
                if not objective.current_object.can_eat():
                    objective.switch_scouting()
                    objective.current_object = None
                #si on est arrivé l'objectif est complété
                elif animal.collide(objective.current_object.hitbox):
                    objective.current_subobjective = CompleteObjective()
                if objective.current_object not in f_view:
                    for obj in f_view:#cherche d’abord la nourriture visible à l’écran
                        if obj.can_eat() and sqrdist(animal.pos,obj.pos)<sqrdist(animal.pos,sub.pos):
                            objective.current_subobjective = GoTo(obj.pos)
                            objective.current_object = obj
            elif sub.type=="kill":
                update_kill_state(sub)
                if sub.completed:
                    objective.current_subobjective=GoTo(sub.animal.meat.pos)
                    objective.current_object=sub.animal.meat
            elif sub.type == "complete":
                if not objective.current_object.can_eat():
                    objective.switch_scouting()

        
        #pour MakeAffinities
        def update_affinities_state(objective:MakeAffinities):
                if objective.current_subobjective==None or objective.scouting:
                    objs = list()

                    for obj in a_view:#recherche d’autres individus de la même espèce dans le champ de vision
                        if obj.species == animal.species and ((obj.id in animal.memory.affinities.keys() and time_dif(animal.memory.affinities[obj.id][1])>=5000 and animal.memory.affinities[obj.id][1]<2) or obj.id not in animal.memory.affinities.keys()):
                            objs.append(obj)
                    
                    if objs!=list():#si des partenaires sont trouvés -> objectif complété
                        objective.current_subobjective = CompleteObjective()
                        objective.current_object = objs
                    
                    elif not objective.scouting:
                        objective.switch_scouting()

        
        def update_reproduce_state(objective:Reproduce_o):
                if not animal.juvenile: #si l'nimal est en age de se reproduire
                    sub = objective.current_subobjective

                    if sub == None or objective.scouting:#si aucun sous-objectif ou si on explore (scouting)

                        for obj in a_view:#cherche d’abord un partenaire visible
                            if obj.species.name_shortcut == animal.species.name_shortcut and not obj.juvenile and obj.sex!=animal.sex and obj.reproduction_will>=0.5: # and obj in animal.memory.affinities.keys() and animal.memory.affinities[obj][0]>=2:
                                objective.current_subobjective = GoTo(obj.pos)
                                objective.current_object = obj
                                objective.scouting = False
                                objective.following_since=0
                                break
                        else:#sinon cherche un partenaire parmi les animaux déjà rencontrés
                            for partner_id,affinity in list(animal.memory.affinities.items()):
                                try:
                                    partner = Animal.id_dict[partner_id]
                                except KeyError:
                                    animal.memory.affinities.pop(partner_id)
                                    continue
                                if partner.reproduction_will>=0.5 and affinity[0]>=2:
                                    objective.current_subobjective = GoTo(partner.pos,must_stop=False)
                                    objective.current_object = partner
                                    objective.scouting = False
                                    objective.following_since=0
                                    break
                            else:#si aucun partenaire n'est trouver l'animal continu d'en chercher un
                                if not objective.scouting:
                                    objective.switch_scouting()
                    
                    elif sub.type =="go_to":#si le sous-objectif est un "GoTo" donc que l'animal vas déjà vers le partenaire trouvé
                        objective.following_since+=1
                        if objective.following_since >=600:
                            animal.memory.affinities[objective.current_object.id]=(-1,math.inf)
                            objective.switch_scouting()
                        else:
                            sub.pos = objective.current_object.pos
                            #si le partenaire meurt ou n’est plus prêt -> on recommence à explorer
                            if objective.current_object.reproduction_will<0.5 or objective.current_object.dead:
                                objective.switch_scouting()
                            #s'il est assez proche l'intéraction peut avoir lieu
                            elif animal.collide(objective.current_object.hitbox):
                                objective.current_subobjective = CompleteObjective()
                    elif sub.type=='complete': #si interaction terminée on vérifie si les conditions ont changées
                        #si l’animal est trop loin ou va trop vite crée un nouveau sous-objectif "GoTo" vers la position actuelle du partenaire
                        if not animal.collide(objective.current_object.hitbox):
                            objective.current_subobjective = GoTo(objective.current_object.pos)
        
        def update_scout_state(objective:Scout):
            #si l’animal atteint un point de la trajectoire de scouting il passe au suivant
            if sqrdist(animal.pos,objective.pattern[objective.current_index])<animal.sex_params.sprint_speed_sqr:
                objective.current_index = (objective.current_index+1)%len(objective.pattern)
                if objective.current_index == 0:
                    objective.pattern = animal.get_scout_path()
        
        def update_kill_state(objective:Kill):
            sub = objective.current_subobjective

            if sub == None:#si aucun sous-objectif
                objective.current_subobjective = GoTo(objective.animal.pos)
            
            elif sub.type =="go_to":#si le sous-objectif est un "GoTo" donc que l'animal va déjà vers la proie
                sub.pos = objective.animal.pos
                #si la proie meurt, anorl l'objectif est terminé
                if objective.animal.dead:
                    objective.completed = True
                #s'il est assez proche l'attaque peut avoir lieu
                elif animal.collide(objective.animal.hitbox):
                    objective.current_subobjective = CompleteObjective()
            elif sub.type=='complete': #si interaction terminée on vérifie si les conditions ont changées
                if not animal.collide(objective.animal.hitbox):
                    objective.current_subobjective = GoTo(objective.animal.pos)
                if objective.animal.dead:
                    objective.completed = True
        
        def update_flee_state(objective:Flee):
            if sqrdist(animal.pos,objective.animal.pos)>40000:
                objective.completed = True

        #gestion des objectifs terminés
        if objective.completed:
            if objective.type in ("find","affinities","reproduce"):
                #on les réinitialise au lieu de les supprimer
                objective.current_object = None
                objective.current_subobjective = None
                objective.completed = False
                objective.scouting = False
            else:#on retire l'objectif ex:kill ou flee
                animal.objectives.remove(objective)
                return None
    
        def update_rest_state(objective:Rest):
            return

        #mise à jour spécifique selon le type d’objectif
        if objective.type=="find":
            update_find_state(objective)
        elif objective.type=="affinities":
            update_affinities_state(objective)
        elif objective.type=="reproduce":
            update_reproduce_state(objective)
        elif objective.type=="scout":
            update_scout_state(objective)
        elif objective.type=="kill":
            update_kill_state(objective)
        elif objective.type=="flee":
            update_flee_state(objective)
        elif objective.type=="rest":
            update_rest_state(objective)
        else:
            raise NotImplementedError(objective.type)
        
    
    generate_objectives() #détecte et crée de nouveaux objectifs

    #mise à jour de chaque objectif existant
    for objective in animal.objectives:
        update_objective_importance(objective)
    
    was_scouting = False
    if isinstance(animal.current_objective,(Find,Reproduce_o)):
        was_scouting = animal.current_objective.scouting
    elif isinstance(animal.current_objective,Rest):
        was_scouting=animal.current_objective.was_scouting
    
    best = max(animal.objectives,key=lambda o:o.importance)
    update_objective_state(best)
    animal.current_objective = best

    update_objective_state(animal.scouting_objective)#mise à jour de l’objectif de scouting général

    if was_scouting and isinstance(best,Rest):best.was_scouting=True

    if not was_scouting and isinstance(best,(Find,Reproduce_o)) and best.scouting:
        #si aucun objectif exploratoire n’était actif avant mais qu’il l’est maintenant
        animal.scouting_objective.current_index=0
        animal.scouting_objective.pattern = animal.get_scout_path()
