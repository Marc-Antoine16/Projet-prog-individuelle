import customtkinter as ctk
import yfinance as yf
import pandas as pd
import numpy as np
from watchlist import Watchlist
from graphe import Graph
from login import LoginPage
from datetime import date
from accueil import Accueil
import os
import json

JSON_PATH = "users.json"

APP_GEOMETRY = "900x800"
APP_TITLE = "Paper Trading"

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("Dark")      
        self.geometry(APP_GEOMETRY)
        self.title(APP_TITLE)
        self.app_is_active = True
        self.user = None
        self.password = None
        self.compte = None
        self.temps = 0
        self.date = date.today()
        self.stocks = {
            "TSLA" : yf.download("TSLA", start="2024-01-01", end=f"{self.date}", interval="1d", auto_adjust=True),
            "AAPL" : yf.download("AAPL", start="2024-01-01", end=f"{self.date}", interval="1d", auto_adjust=True),
            "NVDA" : yf.download("NVDA", start="2024-01-01", end=f"{self.date}", interval="1d", auto_adjust=True)
        }
        self.protocol("WM_DELETE_WINDOW", self.close_app)
        self.show_accueil()   # mettre show_login()

    def show_watchlist(self):
        self.watchlist = Watchlist(master=self)
        self.current_page = self.watchlist

    def show_login(self):
        self.loginPage = LoginPage(master=self)
        self.current_page = self.loginPage

    def show_accueil(self):
        self.accueil = Accueil(master=self)
        self.current_page = self.accueil

    def close_app(self):
        users = {}
        if os.path.exists(JSON_PATH):
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                users = json.load(f)

        username = self.user

        data_user = {
            "password": self.password,
            "temps": self.temps,
            "argent": self.compte.argent if self.compte else 10000,
            "actions": {}
        }

        if self.compte is not None:
            for action, info in self.compte.action.items():
                data_user["actions"][action] = {
                    "prix_achat": info.get("prix_achat", 0),
                    "quantite": info.get("quantite", 0)
                }
        else: 
            pass

        users[username] = data_user

        try:
            with open(JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(users, f, indent=4, ensure_ascii=False)
            print("Données sauvegardées avec succès !")
        except Exception as e:
            print("Erreur lors de la sauvegarde :", e)

        self.app_is_active = False
    
        self.destroy()
        os._exit(0)
        
    
if __name__ == "__main__":
    app = MainApp() 
    app.mainloop()