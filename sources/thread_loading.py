#Projet : The Descent
#Auteurs : Ahmed-Adam REZKALLAH, Noé SAMUEL

#Ce fichier devait servir à charger les modifications de taille du fond de la simulation mais a été abandonné
import threading

class loader:
    _lock = threading.Lock()
    _done:dict[int,bool] = dict()
    _error:dict[int,Exception|None] = dict()
    _next_id = 0
    def __init__(self,func):
        self.func=func
        self.keep=False
        with loader._lock:
            self.id = loader._next_id
            loader._next_id+=1
            loader._done[self.id]=False
            loader._error[self.id]=None
    
    def done(self)->bool:
        with loader._lock:
            return loader._done[self.id]

    def error(self)->Exception|None:
        with loader._lock:
            return loader._error[self.id]
        
    def __call__(self,*args,**kwargs):
        try:
            self.func(*args,**kwargs)
        except Exception as e:
            with loader._lock:
                loader._error[self.id]=e
        with loader._lock:
            loader._done[self.id]=True
        if not self.keep:
            loader._done.pop(self.id)
            loader._error.pop(self.id)

def load_asset(loader:loader,*args,keep=False,**kwargs):
    loader.keep=False
    thread=threading.Thread(target=loader,args=args,kwargs=kwargs,daemon=True)
    thread.start()