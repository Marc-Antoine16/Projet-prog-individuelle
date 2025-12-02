import customtkinter as ctk
import yfinance as yf
from watchlist import Watchlist  
import json
import os


class LoginPage(ctk.CTkFrame):
    def __init__(self, master= None):
   
        super().__init__(master)
        self.master = master

        self.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(self, text="Connexion", font=("Arial", 18, "bold"))
        title.grid(row=0, column=0, pady=(10, 20))

        self.username_entry = ctk.CTkEntry(self, placeholder_text="Nom d'utilisateur")
        self.username_entry.grid(row=1, column=0, padx=10, pady=8, sticky="ew",)

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Mot de passe", show="*")
        self.password_entry.grid(row=2, column=0, padx=10, pady=8, sticky="ew")

        self.message_label = ctk.CTkLabel(self, text="", text_color="red")
        self.message_label.grid(row=3, column=0, pady=(4, 8))

   
        self.login_button = ctk.CTkButton(self, text="Se connecter", command=self.attempt_login)
        self.login_button.grid(row=4, column=0, pady=8)

        
        self.create_button = ctk.CTkButton(self, text="Créer un compte", command=self.create_account)
        self.create_button.grid(row=5, column=0, pady=6)

    def attempt_login(self):
        self.username = self.username_entry.get().strip()
        self.password = self.password_entry.get().strip()

        users_file = "users.json"

        if not os.path.exists(users_file):
            self.message_label.configure(text="Aucun compte n'existe encore.", text_color="red")
            return

        with open(users_file, "r") as f:
            users = json.load(f)

        if self.username in users and users[self.username]["password"] == self.password:
            self.master.user = self.username
            self.master.password = self.password
            saved_actions = users[self.username].get("actions", {})
            self.master.temps = users[self.username].get("temps", 0)
            self.argent = users[self.username].get("argent", 10000)

            from datetime import date
            import yfinance as yf

            actions_reconstruites = {}
            for action_name, info in saved_actions.items():
                try:
                    df = yf.download(
                        action_name,
                        start="2024-01-01",
                        end=f"{date.today()}",
                        interval="1d",
                        auto_adjust=True
                    )
                    if df.empty:
                        df = None
                except Exception:
                    df = None

                actions_reconstruites[action_name] = {
                    "data": df,
                    "prix_achat": info.get("prix_achat", 0),
                    "quantite": info.get("quantite", 0)
                }

            from compte import Compte
            self.master.compte = Compte(
                master=self.master,
                action=actions_reconstruites,
                argent=self.argent
            )
            self.message_label.configure(text="Connexion réussie!", text_color="green")
            self.clear_main_frame()
            from watchlist import Watchlist
            Watchlist(master=self.master)
        else:
            self.message_label.configure(text="Identifiants incorrects.", text_color="red")


    def clear_main_frame(self):
            for widget in self.master.winfo_children():
                widget.destroy()
       
    def create_account(self):

        # Récupère les infos entrées
        self.username = self.username_entry.get().strip()
        self.password = self.password_entry.get().strip()

        # Vérifie que les deux champs sont remplis
        if not self.username or not self.password:
            self.message_label.configure(text="Veuillez remplir tous les champs.", text_color="red")
            return

        users_file = "users.json"
        users = {}


        if os.path.exists(users_file):
            with open(users_file, "r") as f:
                users = json.load(f)

       
        if self.username in users:
            self.message_label.configure(text="Ce nom d'utilisateur existe déjà.", text_color="red")
            return

        users[self.username] = {"password": self.password, "temps" : 0, "actions": {}, "argent": 10000}
        
        with open(users_file, "w") as f:
            json.dump(users, f)

        self.message_label.configure(text="Compte créé avec succès!", text_color="green")