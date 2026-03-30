#Projet : The Descent
#Auteurs : Ahmed-Adam REZKALLAH, Noé SAMUEL

from utils import os_name,Callable
import threading
from pathlib import Path
import shutil

PROJECT_ROOT = Path(__file__).resolve().parents[1]

class FileDialog:
    is_open = False
    window_name = None

    @staticmethod
    def close_file_dialog()->None:raise RuntimeError("Aucune fenêtre n'est ouverte actuellement.")

    @staticmethod
    def open_file_dialog(filetypes:list[str],done_function:Callable[[str|None],None]):
        """
        Choix de fichier Cross-platforme:
        - macOS: NSOpenPanel
        - Windows/Linux: Tkinter hidden root
        Renvoie le chemin absolu du fichier selectionné ou None.
        """

        if "sim" in filetypes:
            base_dir = "data/simulations/sim"
        elif "simstat" in filetypes:
            base_dir = "data/simulations/simstat"
        else:
            raise ValueError(f"Ajouter la dir de base pour les type de fichier {filetypes}")

        def open_window_win():
            global close_file_dialog
            title = "Choix de fichier "
            for filetype in filetypes:
                title+=filetype+" ou "
            title = title[:-4]
            FileDialog.window_name=title

            import tkinter as tk #type:ignore
            from tkinter import filedialog #type:ignore

            root = tk.Tk() #crée la fenêtre tkinter (obligatoire pr lancer filedialog)
            FileDialog.is_open=True
            def close_file_dialog()->None:
                root.destroy()
            root.withdraw()  #cacher la fenêtre tkinter de base (on en a pas besoin)
            options = {"title": title,"initialdir":base_dir}#crée un dict pr stocker les options de la fenêtre tkinter
            options["filetypes"] = [(f"Fichier {ext}", f".{ext}") for ext in filetypes]#on converti en un forma lisible par tkinter
            filename = filedialog.askopenfilename(**options)#ouvre le navigateur de fichiers
            if not filename:
                root.destroy()
                def close_file_dialog()->None:raise RuntimeError("La fenêtre a déjà été fermée")
                FileDialog.is_open = False
                FileDialog.window_name=None
                return done_function(None)
            root.destroy()#on se débarasse de tkinter
            def close_file_dialog()->None:raise RuntimeError("La fenêtre a déjà été fermée")
            FileDialog.is_open=False

            file_path = Path(filename).resolve()

            if file_path.is_relative_to(PROJECT_ROOT):
                relative_path = file_path.relative_to(PROJECT_ROOT)
            else:
                destination = PROJECT_ROOT/"data/simulations/sim"/file_path.name

                counter=1
                while destination.exists():
                    destination = PROJECT_ROOT/"data/simulations/sim"/f"{file_path.stem}_{counter}{file_path.suffix}"
                    counter += 1

                shutil.copy2(file_path,destination)
                relative_path = destination.relative_to(PROJECT_ROOT)

            return done_function(relative_path.as_posix())
        
        def open_window_mac():
            title = "Choix de fichier "
            for filetype in filetypes:
                title+=filetype+" ou "
            title = title[:-4]
            # macOS native dialog
            try:
                from Cocoa import NSOpenPanel,NSURL # type:ignore
            except ImportError:
                raise ImportError("PyObjC requis pour macOS: pip install pyobjc") #au cas ou pyobject  a été désinstallé par l'uttilisateur

            #voir cocoa_test_vs.py pr les explications
            panel = NSOpenPanel.openPanel()
            panel.setCanChooseFiles_(True)
            panel.setCanChooseDirectories_(False)
            panel.setAllowsMultipleSelection_(False)
            panel.setTitle_(title)
            panel.setAllowedFileTypes_(filetypes)
            
            url = NSURL.fileURLWithPath_(base_dir)
            panel.setDirectoryURL_(url)

            result = panel.runModal()

            if result == 1:  #boutton ok
                file_path = Path(panel.URLs()[0].path()).resolve()

                if file_path.is_relative_to(PROJECT_ROOT):
                    relative_path = file_path.relative_to(PROJECT_ROOT)
                else:
                    destination = PROJECT_ROOT/"data/simulations/sim"/file_path.name

                    counter=1
                    while destination.exists():
                        destination = PROJECT_ROOT/"data/simulations/sim"/f"{file_path.stem}_{counter}{file_path.suffix}"
                        counter += 1

                    shutil.copy2(file_path,destination)
                    relative_path = destination.relative_to(PROJECT_ROOT)

                print(relative_path.as_posix())
                return done_function(relative_path.as_posix())
            return done_function(None)

        if os_name == "Windows" and not FileDialog.is_open:
            thread=threading.Thread(target=open_window_win,daemon=True)
            thread.start()
        elif os_name=="Darwin":
            open_window_mac()


if __name__ == "__main__":
    def test(txt):print(txt)
    FileDialog.open_file_dialog(["sim"],test)
    print(PROJECT_ROOT)
    quit()