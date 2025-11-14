import customtkinter as ctk
import yfinance as yf
import pandas as pd
import time
from datetime import date
import threading as th
from login import LoginPage

class Accueil(ctk.CTkFrame):
    def __init__(self, master=None, stocks=None, temps = None):
        super().__init__(master)
        self.master = master
        self.stocks = stocks
        self.temps = temps
        self.pause = False
        self.dropdown_window = ctk.CTkToplevel(self)
        self.options = pd.read_csv("https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv")["Symbol"].tolist()
        self.dropdown_window.overrideredirect(True)
        self.dropdown_window.lift()
        self.dropdown_window.attributes("-topmost", True)
        self.dropdown_window.withdraw()
        self.dropdown_buttons = []

        self.create_widgets()

    def create_widgets(self):
        self.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.master.grid_rowconfigure(0, weight= 1)
        self.master.grid_columnconfigure(0, weight= 1)

        self.titre_label = ctk.CTkLabel(self, text="Accueil", font=("Arial", 30, "bold"))
        self.titre_label.grid(row=0, column=3, pady=(10,10))

        self.connexion_button = ctk.CTkButton(self, text="🔒", fg_color="transparent", hover_color="gray", font=("Arial", 30), command=self.ouvrir_login)
        self.connexion_button.grid(row=0, column=9, padx=(10,10), pady=(10,10))

        self.mot_cherche = ctk.CTkEntry(self, placeholder_text="Rechercher une action...", width=175)
        self.mot_cherche.grid(row=0, column=1, padx=(10,10), pady=(10,10))
        self.mot_cherche.bind("<KeyRelease>", lambda e: self.update_dropdown())

        i = 1
        for stock in self.stocks:
            self.titre_action = ctk.CTkLabel(self, text=stock, font=("Arial", 24, "bold"))
            self.titre_action.grid(row=i, column=0, pady=(10,10))
            
            self.bouton_supprime = ctk.CTkButton(self, text="❎", fg_color="transparent", hover_color="red", font=("Arial", 24), width=60, height=60, command = lambda s = stock: self.supprime_stock(s))
            self.bouton_supprime.grid(row=i, column= 4, pady=(10,10))

        
            i += 1      

        self.boucle_stock()

    def boucle_stock(self):
        if not self.stocks:
            if self.date_label is not None:
                self.date_label.configure(text="Aucun stock")
            self.temps += 1
            self.boucle_id = self.after(5000, self.boucle_stock)
            return
        if not hasattr(self, "prix_buttons"):
            self.prix_label = {}
        if not hasattr(self, "rendement_labels"):
            self.rendement_labels = {}
        if not hasattr(self, "date_label"):
            self.date_label = None

        if self.temps >= len(self.stocks[next(iter(self.stocks))]['Close']):
            self.temps = 0

        for i, stock in enumerate(self.stocks, start=1):
            data = self.stocks[stock]
            y = data["Close"]

            prix = round(float(y.iloc[self.temps]), 2)
            textePrix=str(prix)

            if stock not in self.prix_label:
                self.prix_label[stock] = ctk.CTkLabel(self,text=textePrix,font=("Arial", 24, "bold"))
                self.prix_label[stock].grid(row=i, column=1, padx = (10, 10), pady=(10,10))
            else:
                self.prix_label[stock].configure(text=str(prix))

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
            self.date_label.grid(row=0, column=5, padx=(0,10), pady=(10,10))
        else:
            self.date_label.configure(text=date_text)

        if self.pause == False:
            self.temps += 1
            self.boucle_id = self.after(5000, self.boucle_stock)
    
    def update_dropdown(self, *args):
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
                btn = ctk.CTkButton(self.dropdown_window, text=valeur, width=self.mot_cherche.winfo_width(), fg_color="gray20", hover_color="gray35", command=lambda v=valeur: self.selectionne_option(v))
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

        titre_action = ctk.CTkLabel(self, text=value, font=("Arial", 24, "bold"))
        titre_action.grid(row=i, column=0, padx = (10, 10), pady=(10,10))

        btn_sup = ctk.CTkButton(self, text="❎", fg_color="transparent", hover_color="red", font=("Arial", 24), width=60, height=60, command=lambda s=value: self.supprime_stock(s))
        btn_sup.grid(row=i, column=4, pady=(10,10))

        prix = round(float(df["Close"].iloc[self.temps]), 2)
        self.prix_label[value] = ctk.CTkLabel(self, text=str(prix), font=("Arial", 24, "bold"))
        self.prix_label[value].grid(row=i, column=1, pady=(10,10))

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
    
    
    def supprime_stock(self, nom):
        if hasattr(self, "boucle_id"):
            try:
                self.after_cancel(self.boucle_id)
            except Exception:
                pass

        if nom in self.stocks:
            del self.stocks[nom]

        if hasattr(self, "prix_buttons"):
            self.prix_label.clear()
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

    def clear_main_frame(self):
        if hasattr(self, "boucle_id"):
            try:
                self.after_cancel(self.boucle_id)
            except Exception:
                pass

        for widget in self.winfo_children():
            widget.destroy()

    def ouvrir_login(self):
        self.clear_main_frame()
        self.login = LoginPage(master=self.master, stocks=self.stocks, temps=self.temps)