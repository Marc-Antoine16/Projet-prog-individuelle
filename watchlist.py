import customtkinter as ctk
from info import Info
import yfinance as yf
from graphe import Graph
from compte import Compte
import pandas as pd
import time
from PIL import Image
from datetime import date
import threading as th

class Watchlist(ctk.CTkFrame):
    def __init__(self, master=None, stocks=None, temps = None, compte = None):
        super().__init__(master)
        self.master = master
        self.stocks = stocks
        self.temps = temps
        self.compte = compte
        self.pause = False
        self.options = pd.read_csv("https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv")["Symbol"].tolist()
        self.options_with_placeholder = ["Ajouter..."] + self.options
        self.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.create_widgets()

    def create_widgets(self):
        self.master.grid_rowconfigure(0, weight= 1)
        self.master.grid_columnconfigure(0, weight= 1)

        self.titre_label = ctk.CTkLabel(self, text="Watchlist", font=("Arial", 30, "bold"))
        self.titre_label.grid(row=0, column=0, pady=(10,10))

        self.bouton_compte = ctk.CTkButton(self, text = "Deconnexion", fg_color="transparent", hover_color="red", font=("Arial", 24), command= lambda : self.logout())
        self.bouton_compte.grid(row = 8, column = 0, pady = (10,10))

        self.barre_recherche = ctk.StringVar()
        self.mot_cherche = ctk.CTkEntry(self, textvariable=self.barre_recherche, placeholder_text="Rechercher une action...")
        self.mot_cherche.grid(row=0, column=4, padx=(10,10), pady=(10,10))
        self.barre_recherche.trace_add("write", self.update_dropdown)

        self.dropdown_window = None

        
        self.bouton_compte = ctk.CTkButton(self, text = "Compte", fg_color="transparent", hover_color="red", font=("Arial", 24), command = self.ouvrir_compte)
        self.bouton_compte.grid(row = 7, column = 0, pady = (10,10))

        

        i = 1
        for stock in self.stocks:
            self.titre_action = ctk.CTkButton(self, text=stock ,fg_color = "transparent", hover_color="lightpink", font=("Arial", 24, "bold"), command=lambda s=stock: self.onButtonClicked(s))
            self.titre_action.grid(row=i, column=0, pady=(10,10))

            self.boutonGraphe = ctk.CTkButton(self, text="📈", fg_color="transparent", hover_color="orange", font=("Arial", 24), width=60, height=60 , command = lambda s = stock: self.ouvrir_graph(s))
            self.boutonGraphe.grid(row=i, column=9, pady=(10,10))
            
            self.bouton_supprime = ctk.CTkButton(self, text="❎", fg_color="transparent", hover_color="red", font=("Arial", 24), width=60, height=60, command = lambda s = stock: self.supprime_stock(s))
            self.bouton_supprime.grid(row=i, column=10, pady=(10,10))

            self.bouton_achat = ctk.CTkButton(self, text="Acheter", fg_color="transparent", hover_color="green", font=("Arial", 24), width=80, height=60 , command = lambda a = stock: self.acheter_stock(a))
            self.bouton_achat.grid(row = i, column = 4, pady = (10, 10))

        
            i += 1      

        self.boucle_stock()

    def boucle_stock(self):
        if not self.stocks:
            if self.date_label is not None:
                self.date_label.configure(text="Aucun stock")
            self.temps += 1  # le temps continue quand même
            self.boucle_id = self.after(5000, self.boucle_stock)
            return
        #Initialisation des dictionnaires de widgets si pas fait
        if not hasattr(self, "prix_buttons"):
            self.prix_buttons = {}
        if not hasattr(self, "rendement_labels"):
            self.rendement_labels = {}
        if not hasattr(self, "date_label"):
            self.date_label = None

        #Reset du temps si dépasse le nombre de jours
        if self.temps >= len(self.stocks[next(iter(self.stocks))]['Close']):
            self.temps = 0

        for i, stock in enumerate(self.stocks, start=1):
            data = self.stocks[stock]
            y = data["Close"]

            prix = round(float(y.iloc[self.temps]), 2)
            textePrix=str(prix) #evite le chargement

            if stock not in self.prix_buttons:
                self.prix_buttons[stock] = ctk.CTkButton(self,text=textePrix, fg_color="transparent", hover_color="lightpink",font=("Arial", 24, "bold"),command=lambda s=stock: self.onButtonClicked(s) )
                self.prix_buttons[stock].grid(row=i, column=1, pady=(10,10))
            else:
                self.prix_buttons[stock].configure(text=str(prix))

            if self.temps >= 1:  #au moins deux jours
                dernier = float(y.iloc[self.temps])
                avant_dernier = float(y.iloc[self.temps - 1])
                variation = dernier - avant_dernier
                pourcentage = (variation / avant_dernier) * 100
            else:
                variation = 0.0
                pourcentage = 0.0

            if variation >= 0:
                signe = "+"
                couleur = "green"
            else:
                signe="-"
                couleur="red"

            variation = abs(round(variation, 2))
            pourcentage = abs(round(pourcentage, 2))

            texte_rendement = f"{signe}{variation} $ ({signe}{pourcentage}%) la dernière journée."

            if stock not in self.rendement_labels:
                self.rendement_labels[stock] = ctk.CTkLabel(self,text=texte_rendement, text_color=couleur, font=("Arial", 14))
                self.rendement_labels[stock].grid(row=i, column=3, pady=(10,10))
            else:
                self.rendement_labels[stock].configure(text=f"{signe}{variation} $ ({signe}{pourcentage}%) la dernière journée.",text_color=couleur,  font=("Arial", 14))

        date_text = self.stocks[next(iter(self.stocks))].index[self.temps].date()

        if self.date_label is None:
            self.date_label = ctk.CTkLabel(self,text=date_text,text_color="light gray",font=("Arial", 24))
            self.date_label.grid(row=0, column=3, padx=(0,10), pady=(10,10))
        else:
            self.date_label.configure(text=date_text)

        if self.pause == False:
            self.temps += 1
            self.boucle_id = self.after(5000, self.boucle_stock)

    def clear_main_frame(self):
        if hasattr(self, "boucle_id"):
            try:
                self.after_cancel(self.boucle_id)
            except Exception:
                pass

        for widget in self.winfo_children():
            widget.destroy()
        
        
    def onButtonClicked(self, pseudo):
        self.clear_main_frame()
        Info(self.master, self.stocks, pseudo, self.temps, self.compte)

    def ouvrir_graph(self, name):
        self.clear_main_frame()
        Graph(self.master, self.stocks, name, self.temps, self.compte)
    
    def logout(self):
        self.clear_main_frame()
        from login import LoginPage
        LoginPage(master=self, stocks=self.stocks)


    def update_dropdown(self, *args):
        recherche = self.barre_recherche.get().upper()

        if self.dropdown_window is not None and self.dropdown_window.winfo_exists():
            self.dropdown_window.destroy()

        if recherche == "":
            return

        valeurs_filtrees = [option for option in self.options if recherche in option]

        if not valeurs_filtrees:
            return

        self.dropdown_window = ctk.CTkToplevel(self)
        self.dropdown_window.overrideredirect(True)
        self.dropdown_window.lift()
        self.dropdown_window.attributes("-topmost", True)

        x = self.mot_cherche.winfo_rootx()
        y = self.mot_cherche.winfo_rooty() + self.mot_cherche.winfo_height()
        self.dropdown_window.geometry(f"+{x}+{y}")

        for valeur in valeurs_filtrees[:10]:
            btn = ctk.CTkButton(
                self.dropdown_window,
                text=valeur,
                width=self.mot_cherche.winfo_width(),
                fg_color="gray20",
                hover_color="gray35",
                command=lambda v=valeur: self.selectionne_option(v)
            )
            btn.pack(pady=1)

    def selectionne_option(self, valeur):
        if self.dropdown_window is not None:
            self.after(100, self.dropdown_window.destroy)

        self.barre_recherche.set(valeur)
        self.option_changed(valeur)

    def option_changed(self, value): #ajout nouveau stock, créer widgets sans reconstruire la page pour que les labels de rendement deja existant reste visible et continue de se mettre a jour
        if value == "Ajouter...":
            return
        
        if value in self.stocks:  # déjà dans la watchlist
            return
        
        self.label_chargement = ctk.CTkLabel(self, text=f"Téléchargement de {value}...", font=("Arial", 16))
        self.label_chargement.grid(row=len(self.stocks) + 1, column=0, pady=(10,10))

        th.Thread(target=self.telecharger_action, args=(value,), daemon=True).start()

    def telecharger_action(self, value):
        try:
            df = yf.download(value, start="2024-01-01", end=f"{date.today()}", interval="1d", auto_adjust=True)
            if df.empty or "Close" not in df.columns:
                print(f"Erreur: impossible de charger {value}")
                self.after(0, lambda: self.label_chargement.configure(text=f"Erreur de téléchargement pour {value}"))
                return
        except Exception as e:
            print("Erreur téléchargement :", e)
            self.after(0, lambda: self.label_chargement.configure(text=f"Erreur de connexion ({value})"))
            return

        self.after(0, lambda: self.ajouter_stock(value, df))


    def ajouter_stock(self, value, df):
        if hasattr(self, "label_chargement"):
            self.label_chargement.destroy()

        self.stocks[value] = df
        i = len(self.stocks)

        btn_action = ctk.CTkButton(self, text=value, fg_color="transparent", hover_color="lightpink", font=("Arial", 24, "bold"), command=lambda s=value: self.onButtonClicked(s))
        btn_action.grid(row=i, column=0, pady=(10,10))

        btn_graph = ctk.CTkButton(self, text="📈", fg_color="transparent", hover_color="orange", font=("Arial", 24), width=60, height=60, command=lambda s=value: self.ouvrir_graph(s))
        btn_graph.grid(row=i, column=9, pady=(10,10))

        btn_sup = ctk.CTkButton(self, text="❎", fg_color="transparent", hover_color="red", font=("Arial", 24), width=60, height=60, command=lambda s=value: self.supprime_stock(s))
        btn_sup.grid(row=i, column=10, pady=(10,10))

        btn_achat = ctk.CTkButton(self, text="Acheter", fg_color="transparent", hover_color="green", font=("Arial", 24), width=80, height=60, command=lambda s=value: self.acheter_stock(s))
        btn_achat.grid(row=i, column=4, pady=(10,10))

        prix = round(float(df["Close"].iloc[self.temps]), 2)
        self.prix_buttons[value] = ctk.CTkButton(self, text=str(prix), fg_color="transparent", hover_color="lightpink", font=("Arial", 24, "bold"), command=lambda s=value: self.onButtonClicked(s))
        self.prix_buttons[value].grid(row=i, column=1, pady=(10,10))

        if self.temps >= 1:
            dernier = float(df["Close"].iloc[self.temps])
            avant_dernier = float(df["Close"].iloc[self.temps - 1])
            variation = dernier - avant_dernier
            pourcentage = (variation / avant_dernier) * 100
        else:
            variation = 0
            pourcentage = 0

        signe = "+" if variation >= 0 else "-"
        couleur = "green" if variation >= 0 else "red"

        variation = abs(round(variation, 2))
        pourcentage = abs(round(pourcentage, 2))
        texte_rendement = f"{signe}{variation} $ ({signe}{pourcentage}% ) la dernière journée."

        self.rendement_labels[value] = ctk.CTkLabel(self, text=texte_rendement, text_color=couleur, font=("Arial", 14))
        self.rendement_labels[value].grid(row=i, column=3, pady=(10,10))


    def ouvrir_compte(self):
        actions = self.compte.action if self.compte is not None else {}
        argent = self.compte.argent if self.compte is not None else 10000

        self.clear_main_frame()

        from compte import Compte
        self.compte = Compte(self.master, self.stocks, self.temps, action=actions, argent = argent)

        self.compte.create_widgets()

    def acheter_stock(self, action):
        self.pause = True
        page_achat = ctk.CTkToplevel(self)
        page_achat.title(f"achat de {action}")
        page_achat.geometry("300x200")
        page_achat.grab_set()

        self.quantite_label = ctk.CTkLabel(page_achat, text= "quantité : ")
        self.quantite_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        self.quantite_entry = ctk.CTkEntry(page_achat, placeholder_text="Entrez la quantité...")
        self.quantite_entry.grid(row=0, column=1, padx=20, pady=(20, 10), sticky="ew")
        
        ou = ctk.CTkLabel(page_achat, text= "OU")
        ou.grid(row=1, column=0, padx=20, pady=(20, 10), sticky="w")

        self.prix_label = ctk.CTkLabel(page_achat, text= "prix : ")
        self.prix_label.grid(row=2, column=0, padx=20, pady=(20, 10), sticky="w")
        self.prix_entry = ctk.CTkEntry(page_achat, placeholder_text="Entrez le prix...")
        self.prix_entry.grid(row=2, column=1, padx=20, pady=(20, 10), sticky="ew")

        if(float(self.quantite_entry.get())):
            self.submit_button = ctk.CTkButton(self, text = "Soumettre", command= self.soumettreAchat(action))
            self.submit_button.grid(row=3, column=1, padx=20, pady=(20, 10), sticky="ew")
        
    def soumettreAchat(self, action):
        prix_achat = round(self.stocks[action]["Close"].iloc[self.temps - 1].iloc[0], 2)
        quantite = float(self.quantite_entry.get())
        if self.compte is None:
            from compte import Compte
            self.compte = Compte(self.master, self.stocks, self.temps, action={}, argent=10000)

        if isinstance(self.quantite_entry.get(), int) and self.compte.argent >= prix_achat * self:
            self.compte.argent -= prix_achat

            if action in self.compte.action:
                ancienne_quantite = self.compte.action[action]["quantite"]
                ancien_prix = self.compte.action[action]["prix_achat"]

                nouveau_prix_moyen = ((ancien_prix * ancienne_quantite) + prix_achat) / (ancienne_quantite + 1)
                self.compte.action[action]["quantite"] += 1

            else:
                self.compte.action[action] = {"data": self.stocks[action], "prix_achat": prix_achat, "quantite": 1}

        else:
            self.label = ctk.CTkLabel(self, text="Pas assez de fonds pour acheter cette action", fg_color="dark gray", font=("Arial", 20))
            self.label.grid(row=3, column=3, padx=(20, 20), pady=(20, 20))
            self.after(3000, self.label.destroy)
    

    def supprime_stock(self, nom):
        if hasattr(self, "boucle_id"):
            try:
                self.after_cancel(self.boucle_id)
            except Exception:
                pass

        if nom in self.stocks:
            del self.stocks[nom]

        if hasattr(self, "prix_buttons"):
            self.prix_buttons.clear()
        if hasattr(self, "rendement_labels"):
            self.rendement_labels.clear()
        if hasattr(self, "date_label") and self.date_label is not None:
            try:
                self.date_label.destroy()
            except Exception:
                pass
            self.date_label = None

        self.clear_main_frame()
        self.create_widgets()