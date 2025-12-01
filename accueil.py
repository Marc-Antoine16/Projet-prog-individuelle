import customtkinter as ctk
import yfinance as yf
import pandas as pd
from datetime import date
import threading as th
from login import LoginPage

class Accueil(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.dropdown_window = ctk.CTkToplevel(self)
        self.options = pd.read_csv(
            "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"
        )["Symbol"].tolist()
        self.dropdown_window.overrideredirect(True)
        self.dropdown_window.lift()
        self.dropdown_window.attributes("-topmost", True)
        self.dropdown_window.withdraw()
        self.dropdown_buttons = []

        self.prix_label = {}
        self.rendement_labels = {}
        self.date_label = None

        self.create_widgets()

    def create_widgets(self):
        self.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        self.titre_label = ctk.CTkLabel(self, text="Accueil", font=("Arial", 30, "bold"))
        self.titre_label.grid(row=0, column=3, pady=(10,10))

        self.connexion_button = ctk.CTkButton(
            self, text="🔒", fg_color="transparent", hover_color="gray",
            font=("Arial", 30), command=self.ouvrir_login
        )
        self.connexion_button.grid(row=0, column=9, padx=(10,10), pady=(10,10))

        self.mot_cherche = ctk.CTkEntry(self, placeholder_text="Rechercher une action...", width=175)
        self.mot_cherche.grid(row=0, column=1, padx=(10,10), pady=(10,10))
        self.mot_cherche.bind("<KeyRelease>", lambda e: self.update_dropdown())

        text = "Bienvenue sur votre plateforme de Paper Trading !\nVoici quelques fonctionnalités. Pour plus d'options, veuillez vous connecter."

        self.texte_avant_watchlist = ctk.CTkLabel(self, text=text,font=("Arial", 20), text_color="gray")
        self.texte_avant_watchlist.grid(row=1, column=0, columnspan=10, pady=(10,20), sticky="n")

        i = 2 
        for stock in self.master.stocks:
            self._creer_stock_widgets(stock, i)
            i += 1

        self.boucle_stock()

    def _creer_stock_widgets(self, stock, row):
        titre_action = ctk.CTkLabel(self, text=stock, font=("Arial", 24, "bold"))
        titre_action.grid(row=row, column=0, pady=(10,10))

        bouton_sup = ctk.CTkButton(
            self, text="❎", fg_color="transparent", hover_color="red",
            font=("Arial", 24), width=60, height=60, command=lambda s=stock: self.supprime_stock(s)
        )
        bouton_sup.grid(row=row, column=4, pady=(10,10))

        prix = round(float(self.master.stocks[stock]["Close"].iloc[self.master.temps]), 2)
        self.prix_label[stock] = ctk.CTkLabel(self, text=str(prix), font=("Arial", 24, "bold"))
        self.prix_label[stock].grid(row=row, column=1, pady=(10,10))

        df = self.master.stocks[stock]
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
        self.rendement_labels[stock] = ctk.CTkLabel(self, text=texte_rendement, text_color=couleur, font=("Arial", 14))
        self.rendement_labels[stock].grid(row=row, column=3, pady=(10,10))

    def boucle_stock(self):
        if not self.master.stocks:
            if self.date_label is not None:
                self.date_label.configure(text="Aucun stock")
            self.master.temps += 1
            self.boucle_id = self.after(5000, self.boucle_stock)
            return

        if not hasattr(self, "prix_label"):
            self.prix_label = {}
        if not hasattr(self, "rendement_labels"):
            self.rendement_labels = {}
        if not hasattr(self, "date_label"):
            self.date_label = None

        if self.master.temps >= len(self.master.stocks[next(iter(self.master.stocks))]['Close']):
            self.master.temps = 0

    
        for i, stock in enumerate(self.master.stocks, start=2):
            df = self.master.stocks[stock]
            prix = round(float(df["Close"].iloc[self.master.temps]), 2)

            if stock not in self.prix_label:
                self.prix_label[stock] = ctk.CTkLabel(self, text=str(prix), font=("Arial", 24, "bold"))
                self.prix_label[stock].grid(row=i, column=1, pady=(10,10))
            else:
                self.prix_label[stock].configure(text=str(prix))

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

            if stock not in self.rendement_labels:
                self.rendement_labels[stock] = ctk.CTkLabel(self, text=texte_rendement, text_color=couleur, font=("Arial", 14))
                self.rendement_labels[stock].grid(row=i, column=3, pady=(10,10))
            else:
                self.rendement_labels[stock].configure(text=texte_rendement, text_color=couleur)

        # Date
        date_text = self.master.stocks[next(iter(self.master.stocks))].index[self.master.temps].date()
        if self.date_label is None:
            self.date_label = ctk.CTkLabel(self, text=date_text, text_color="light gray", font=("Arial", 24))
            self.date_label.grid(row=0, column=5, padx=(0,10), pady=(10,10))
        else:
            self.date_label.configure(text=date_text)

        self.master.temps += 1
        self.boucle_id = self.after(5000, self.boucle_stock)

    # --- Ajouter un stock ---
    def option_changed(self, value):
        if value == "Ajouter...":
            return
        if value in self.master.stocks:
            return
        self.label_chargement = ctk.CTkLabel(self, text=f"Téléchargement de {value}...", font=("Arial", 16))
        self.label_chargement.grid(row=len(self.master.stocks)+2, column=0, pady=(10,10))
        th.Thread(target=self.telecharger_action, args=(value,), daemon=True).start()

    def telecharger_action(self, value):
        try:
            df = yf.download(value, start="2024-01-01", end=f"{date.today()}", interval="1d", auto_adjust=True)
            if df.empty or "Close" not in df.columns:
                self.after(0, lambda: self.label_chargement.configure(text=f"Erreur de téléchargement pour {value}"))
                return
        except Exception as e:
            self.after(0, lambda: self.label_chargement.configure(text=f"Erreur de connexion ({value})"))
            return
        self.after(0, lambda: self.ajouter_stock(value, df))

    def ajouter_stock(self, value, df):
        if hasattr(self, "label_chargement"):
            self.label_chargement.destroy()
        self.master.stocks[value] = df
        row = len(self.master.stocks) + 1
        self._creer_stock_widgets(value, row)

    def supprime_stock(self, nom):
        if hasattr(self, "boucle_id"):
            try:
                self.after_cancel(self.boucle_id)
            except:
                pass

        if nom in self.master.stocks:
            del self.master.stocks[nom]

        self.prix_label.clear()
        self.rendement_labels.clear()

        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkToplevel):
                continue
            info = widget.grid_info()
            if info and "row" in info and int(info["row"]) >= 2:
                widget.destroy()

        for i, stock in enumerate(self.master.stocks, start=2):
            self._creer_stock_widgets(stock, i)

        self.boucle_stock()

    def update_dropdown(self, *args):
        if self.dropdown_window is not None and not self.dropdown_window.winfo_exists():
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
                btn = ctk.CTkButton(self.dropdown_window, text=valeur, width=self.mot_cherche.winfo_width(),
                                     fg_color="gray20", hover_color="gray35",
                                     command=lambda v=valeur: self.selectionne_option(v))
                btn.pack(pady=1)
                self.dropdown_buttons.append(btn)
        for j in range(len(valeurs_filtrees), len(self.dropdown_buttons)):
            self.dropdown_buttons[j].pack_forget()

    def selectionne_option(self, valeur):
        self.mot_cherche.delete(0, "end")
        self.mot_cherche.insert(0, valeur)
        self.dropdown_window.withdraw()
        self.option_changed(valeur)

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
        self.login = LoginPage(master=self.master)