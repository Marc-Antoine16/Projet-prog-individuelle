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
import os
import json

JSON_PATH = "users.json"

class Watchlist(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pause = False
        self.date_label = None
        self.options = pd.read_csv("https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv")["Symbol"].tolist()
        self.options_with_placeholder = ["Ajouter..."] + self.options
        self.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.dropdown_window = ctk.CTkToplevel(self)
        self.dropdown_window.overrideredirect(True)
        self.dropdown_window.lift()
        self.dropdown_window.attributes("-topmost", True)
        self.dropdown_window.withdraw()
        self.dropdown_buttons = []
        self.create_widgets()

    def create_widgets(self):
        self.master.grid_rowconfigure(0, weight= 1)
        self.master.grid_columnconfigure(0, weight= 1)

        self.titre_label = ctk.CTkLabel(self, text="Watchlist", font=("Arial", 30, "bold"))
        self.titre_label.grid(row=0, column=0, pady=(10,10))

        self.bouton_deconnexion = ctk.CTkButton(self, text = "Deconnexion", fg_color="transparent", hover_color="red", font=("Arial", 24), command= lambda : self.logout())
        self.bouton_deconnexion.grid(row = 8, column = 0, pady = (10,10))

        self.mot_cherche = ctk.CTkEntry(self, placeholder_text="Rechercher une action...", width=175)
        self.mot_cherche.grid(row=0, column=4, padx=(10,10), pady=(10,10))
        self.mot_cherche.bind("<KeyRelease>", lambda e: self.update_dropdown())

        
        self.bouton_compte = ctk.CTkButton(self, text = "Compte", fg_color="transparent", hover_color="red", font=("Arial", 24), command = self.ouvrir_compte)
        self.bouton_compte.grid(row = 7, column = 0, pady = (10,10))

        

        i = 1
        for stock in self.master.stocks:
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
        if not self.master.app_is_active:
            return
        
        if not self.master.stocks:
            if self.date_label is not None:
                self.date_label.configure(text="Aucun stock")
            self.master.temps += 1  # le temps continue quand même
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
        if self.master.temps >= len(self.master.stocks[next(iter(self.master.stocks))]['Close']):
            self.master.temps = 0
        if self.pause == False and self.master.app_is_active:
            for i, stock in enumerate(self.master.stocks, start=1):
                data = self.master.stocks[stock]
                y = data["Close"]

                prix = round(float(y.iloc[self.master.temps]), 2)
                textePrix=str(prix) #evite le chargement

                if stock not in self.prix_buttons:
                    self.prix_buttons[stock] = ctk.CTkButton(self,text=textePrix, fg_color="transparent", hover_color="lightpink",font=("Arial", 24, "bold"),command=lambda s=stock: self.onButtonClicked(s) )
                    self.prix_buttons[stock].grid(row=i, column=1, pady=(10,10))
                else:
                    self.prix_buttons[stock].configure(text=str(prix))

                if self.master.temps >= 1:  #au moins deux jours
                    dernier = float(y.iloc[self.master.temps])
                    avant_dernier = float(y.iloc[self.master.temps - 1])
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

            date_text = self.master.stocks[next(iter(self.master.stocks))].index[self.master.temps].date()

            if self.date_label is None:
                self.date_label = ctk.CTkLabel(self,text=date_text,text_color="light gray",font=("Arial", 24))
                self.date_label.grid(row=0, column=3, padx=(0,10), pady=(10,10))
            else:
                self.date_label.configure(text=date_text)

            self.master.temps += 1
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
        Info(self.master, pseudo)

    def ouvrir_graph(self, name):
        self.clear_main_frame()
        Graph(self.master, name)
    
    def logout(self):
        users = {}
        if os.path.exists(JSON_PATH):
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                users = json.load(f)

        username = self.master.user

        # Crée le dictionnaire à sauvegarder pour l'utilisateur
        data_user = {
            "password": self.master.password,
            "temps": self.master.temps,
            "argent": self.master.compte.argent if self.master.compte else 10000,
            "actions": {}
        }

        self.master.temps = 0
        # On sauvegarde uniquement les actions achetées
        if self.master.compte and hasattr(self.master.compte, "action"):
            for action, info in self.master.compte.action.items():
                data_user["actions"][action] = {
                    "prix_achat": info.get("prix_achat", 0),
                    "quantite": info.get("quantite", 0)
                }

        # Met à jour ou ajoute l'utilisateur dans le dictionnaire complet
        users[username] = data_user

        # Sauvegarde le fichier complet avec tous les comptes
        try:
            with open(JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(users, f, indent=4, ensure_ascii=False)
            print("Données sauvegardées avec succès !")
        except Exception as e:
            print("Erreur lors de la sauvegarde :", e)

        # Retour à l'accueil
        self.clear_main_frame()
        from accueil import Accueil
        self.accueil = Accueil(master=self.master)

    def update_dropdown(self, *args):
        if self.dropdown_window is not None:
            if not self.dropdown_window.winfo_exists():
                self.dropdown_window = None

        if not hasattr(self, "dropdown_window") or not self.dropdown_window.winfo_exists():
            return
        recherche = self.mot_cherche.get().upper()
        x = self.mot_cherche.winfo_rootx()
        y = self.mot_cherche.winfo_rooty() + self.mot_cherche.winfo_height()
        self.dropdown_window.geometry(f"+{x}+{y}")

        if not recherche:
            self.dropdown_window.withdraw()
            return

        valeurs_filtrees = [opt for opt in self.options if recherche in opt]

        if not valeurs_filtrees:
            self.dropdown_window.withdraw()
            return

        self.dropdown_window.deiconify()

        for i, valeur in enumerate(valeurs_filtrees[:10]):
            if i < len(self.dropdown_buttons):
                btn = self.dropdown_buttons[i]
                btn.configure(text=valeur, command=lambda v=valeur: self.selectionne_option(v))
                btn.pack_forget()
                btn.pack(pady=1)
            else:
                btn = ctk.CTkButton(
                    self.dropdown_window,
                    text=valeur,
                    width=self.mot_cherche.winfo_width(),
                    fg_color="gray20",
                    hover_color="gray35",
                    command=lambda v=valeur: self.selectionne_option(v)
                )
                btn.pack(pady=1)
                self.dropdown_buttons.append(btn)

        for j in range(len(valeurs_filtrees), len(self.dropdown_buttons)):
            self.dropdown_buttons[j].pack_forget()

    def selectionne_option(self, valeur):
        self.mot_cherche.delete(0, "end")
        self.mot_cherche.insert(0, valeur)
        self.dropdown_window.withdraw()
        self.option_changed(valeur)

    def option_changed(self, value): #ajout nouveau stock, créer widgets sans reconstruire la page pour que les labels de rendement deja existant reste visible et continue de se mettre a jour
        if value == "Ajouter...":
            return
        
        if value in self.master.stocks:  # déjà dans la watchlist
            return
        
        self.label_chargement = ctk.CTkLabel(self, text=f"Téléchargement de {value}...", font=("Arial", 16))
        self.label_chargement.grid(row=len(self.master.stocks) + 1, column=0, pady=(10,10))

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

        self.master.stocks[value] = df
        i = len(self.master.stocks)

        btn_action = ctk.CTkButton(self, text=value, fg_color="transparent", hover_color="lightpink", font=("Arial", 24, "bold"), command=lambda s=value: self.onButtonClicked(s))
        btn_action.grid(row=i, column=0, pady=(10,10))

        btn_graph = ctk.CTkButton(self, text="📈", fg_color="transparent", hover_color="orange", font=("Arial", 24), width=60, height=60, command=lambda s=value: self.ouvrir_graph(s))
        btn_graph.grid(row=i, column=9, pady=(10,10))

        btn_sup = ctk.CTkButton(self, text="❎", fg_color="transparent", hover_color="red", font=("Arial", 24), width=60, height=60, command=lambda s=value: self.supprime_stock(s))
        btn_sup.grid(row=i, column=10, pady=(10,10))

        btn_achat = ctk.CTkButton(self, text="Acheter", fg_color="transparent", hover_color="green", font=("Arial", 24), width=80, height=60, command=lambda s=value: self.acheter_stock(s))
        btn_achat.grid(row=i, column=4, pady=(10,10))

        prix = round(float(df["Close"].iloc[self.master.temps]), 2)
        self.prix_buttons[value] = ctk.CTkButton(self, text=str(prix), fg_color="transparent", hover_color="lightpink", font=("Arial", 24, "bold"), command=lambda s=value: self.onButtonClicked(s))
        self.prix_buttons[value].grid(row=i, column=1, pady=(10,10))

        if self.master.temps >= 1:
            dernier = float(df["Close"].iloc[self.master.temps])
            avant_dernier = float(df["Close"].iloc[self.master.temps - 1])
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
        actions = self.master.compte.action if self.master.compte is not None else {}
        argent = self.master.compte.argent if self.master.compte is not None else 10000

        self.clear_main_frame()

        from compte import Compte
        self.master.compte = Compte(self.master, action=actions, argent = argent)

        self.master.compte.create_widgets()

    def acheter_stock(self, action):
        if hasattr(self, "boucle_id"):
            try:
                self.after_cancel(self.boucle_id)
            except Exception:
                pass

        self.pause = True

        page_achat = ctk.CTkToplevel(self)
        page_achat.title(f"Achat de {action}")
        page_achat.geometry("420x360")
        page_achat.grab_set()

        page_achat.protocol("WM_DELETE_WINDOW", lambda: self.on_close_achat(page_achat))

        self.prix_action = round(float(self.master.stocks[action]["Close"].iloc[self.master.temps]), 2)

        if self.master.compte is None:
            from compte import Compte
            self.master.compte = Compte(self.master, action={}, argent=10000)
            solde = 10000
        
        else:
            solde = self.master.compte.argent

        ctk.CTkLabel(page_achat, text=f"Prix actuel : {self.prix_action:.2f}$", font=("Arial", 18, "bold")).pack(pady=(10, 5))
        ctk.CTkLabel(page_achat, text=f"Solde disponible : {solde:.2f}$", font=("Arial", 16)).pack(pady=(0, 15))

        ctk.CTkLabel(page_achat, text="Choisir le mode d'achat :", font=("Arial", 16)).pack(pady=(0, 10))

        self.mode_achat = ctk.StringVar(value="quantite")

        frame_modes = ctk.CTkFrame(page_achat)
        frame_modes.pack(pady=(0, 10))

        ctk.CTkRadioButton(frame_modes, text="Quantité", variable=self.mode_achat, value="quantite", command=lambda: self.switch_mode(page_achat)).grid(row=0, column=0, padx=10)
        ctk.CTkRadioButton(frame_modes, text="Montant ($)", variable=self.mode_achat, value="prix", command=lambda: self.switch_mode(page_achat)).grid(row=0, column=1, padx=10)

        
        self.zone_dynamique = ctk.CTkFrame(page_achat)
        self.zone_dynamique.pack(pady=(10, 10))

        self.creer_zone_quantite(page_achat, solde)

        self.btn_submit = ctk.CTkButton(page_achat, text="Acheter", state="disabled", command=lambda: self.valider_achat(page_achat, action, solde))
        self.btn_submit.pack(pady=20)

    def on_close_achat(self, window):
        self.pause = False
        window.destroy()
        self.boucle_stock()
        
    def switch_mode(self, page_achat):
        for widget in self.zone_dynamique.winfo_children():
            widget.destroy()

        solde = self.master.compte.argent if self.master.compte is not None else 10000

        if self.mode_achat.get() == "quantite":
            self.creer_zone_quantite(page_achat, solde)
        else:
            self.creer_zone_prix(page_achat, solde)


    def creer_zone_quantite(self, page_achat, solde):
        self.var_quantite = ctk.StringVar()
        self.var_quantite.trace_add("write", lambda *a: self.verifier_saisie())

        ctk.CTkLabel(self.zone_dynamique, text="Quantité d'actions :", font=("Arial", 15)).pack(pady=(0, 5))
        frame_q = ctk.CTkFrame(self.zone_dynamique)
        frame_q.pack()

        self.quantite_entry = ctk.CTkEntry(frame_q, textvariable=self.var_quantite, width=120, placeholder_text="ex: 10")
        self.quantite_entry.grid(row=0, column=0, padx=(0, 10))

        ctk.CTkButton(frame_q, text="Max", width=60, fg_color="grey", hover_color="orange", command=lambda: self.ajouter_max(solde)).grid(row=0, column=1)


    def creer_zone_prix(self, page_achat, solde):
        self.var_prix = ctk.StringVar()
        self.var_prix.trace_add("write", lambda *a: self.verifier_saisie())

        ctk.CTkLabel(self.zone_dynamique, text="Montant à investir ($) :", font=("Arial", 15)).pack(pady=(0, 5))
        self.prix_entry = ctk.CTkEntry(self.zone_dynamique, textvariable=self.var_prix, width=180, placeholder_text="ex: 500")
        self.prix_entry.pack()


    def verifier_saisie(self, *args):
        max = int(self.master.compte.argent // self.prix_action)
        if self.mode_achat.get() == "quantite":
            val = self.var_quantite.get()
            valide = val.isdigit() and max >= int(val) > 0
        else:
            val = self.var_prix.get()
            try:
                valide = self.mastercompte.argent >= float(val) > 0
            except ValueError:
                valide = False

        self.btn_submit.configure(state="normal" if valide else "disabled")


    def ajouter_max(self, solde):
        quantite_max = int(solde // self.prix_action)
        self.var_quantite.set(str(quantite_max))


    def valider_achat(self, page_achat, action, solde):
        if self.mode_achat.get() == "quantite":
            quantite = int(self.var_quantite.get())
            cout_total = quantite * self.prix_action
        else:
            montant = float(self.var_prix.get())
            quantite = int(montant // self.prix_action)
            cout_total = quantite * self.prix_action

        if cout_total > solde:
            self.label = ctk.CTkLabel(self, text="Pas assez de fonds pour acheter cette action", fg_color="dark gray", font=("Arial", 20))
            self.label.grid(row=3, column=3, padx=(20, 20), pady=(20, 20))
            self.after(3000, self.label.destroy)

        else:
            self.master.compte.argent -= cout_total
            if action in self.master.compte.action:
                ancienne_quantite = self.master.compte.action[action]["quantite"]
                ancien_prix = self.master.compte.action[action]["prix_achat"]

                nouveau_prix_moyen = ((ancien_prix * ancienne_quantite) + cout_total) / (quantite)
                self.master.compte.action[action]["quantite"] += quantite

            else:
                self.master.compte.action[action] = {"data": self.master.stocks[action], "prix_achat": cout_total/quantite, "quantite": quantite}
        page_achat.destroy()
        self.pause = False
        self.boucle_stock()

    def supprime_stock(self, nom):
        if len(self.master.stocks) > 1:
            if hasattr(self, "boucle_id"):
                try:
                    self.after_cancel(self.boucle_id)
                except Exception:
                    pass

            if nom in self.master.stocks:
                del self.master.stocks[nom]

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

            for widget in self.winfo_children():
                if hasattr(widget, "grid_info"):
                    info = widget.grid_info()
                    if info and "row" in info and info["row"] >= 0:
                        widget.destroy()

            self.titre_label = ctk.CTkLabel(self, text="Watchlist", font=("Arial", 30, "bold"))
            self.titre_label.grid(row=0, column=0, pady=(10,10))

            self.mot_cherche = ctk.CTkEntry(self, placeholder_text="Rechercher une action...", width=175)
            self.mot_cherche.grid(row=0, column=4, padx=(10,10), pady=(10,10))
            self.mot_cherche.bind("<KeyRelease>", lambda e: self.update_dropdown())

            self.bouton_compte = ctk.CTkButton(
                self, text="Compte", fg_color="transparent", hover_color="red",
                font=("Arial", 24), command=self.ouvrir_compte
            )
            self.bouton_compte.grid(row=7, column=0, pady=(10,10))

            self.bouton_deconnexion = ctk.CTkButton(
                self, text="Deconnexion", fg_color="transparent", hover_color="red",
                font=("Arial", 24), command=self.logout
            )
            self.bouton_deconnexion.grid(row=8, column=0, pady=(10,10))

            i = 1
            for stock in self.master.stocks:

                btn_action = ctk.CTkButton(
                    self, text=stock, fg_color="transparent", hover_color="lightpink",
                    font=("Arial", 24, "bold"), command=lambda s=stock: self.onButtonClicked(s)
                )
                btn_action.grid(row=i, column=0, pady=(10,10))

                btn_graph = ctk.CTkButton(
                    self, text="📈", fg_color="transparent", hover_color="orange",
                    font=("Arial", 24), width=60, height=60,
                    command=lambda s=stock: self.ouvrir_graph(s)
                )
                btn_graph.grid(row=i, column=9, pady=(10,10))

                btn_sup = ctk.CTkButton(
                    self, text="❎", fg_color="transparent", hover_color="red",
                    font=("Arial", 24), width=60, height=60,
                    command=lambda s=stock: self.supprime_stock(s)
                )
                btn_sup.grid(row=i, column=10, pady=(10,10))

                btn_achat = ctk.CTkButton(
                    self, text="Acheter", fg_color="transparent", hover_color="green",
                    font=("Arial", 24), width=80, height=60,
                    command=lambda a=stock: self.acheter_stock(a)
                )
                btn_achat.grid(row=i, column=4, pady=(10,10))

                i += 1

            self.boucle_stock()