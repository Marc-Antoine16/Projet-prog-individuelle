import customtkinter as ctk
import time

class Info(ctk.CTkFrame):
    def __init__(self, master=None, stocks=None, nom=None, temps=None, compte=None):
        super().__init__(master)
        self.master = master
        self.stocks = stocks
        self.nom = nom
        self.temps = temps
        self.compte = compte
        self.create_widgets()

    def create_widgets(self):
        self.grid(row=0, column=0, padx=50, pady=50, sticky="nsew")

        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        self.titre_label = ctk.CTkLabel(self, text="Statistiques", font=("Arial", 30, "bold"))
        self.titre_label.grid(row=1, column=0, padx=(10, 30), pady=(5, 20))

        self.titre_nom = ctk.CTkLabel(self, text=self.nom, font=("Arial", 40, "bold"))
        self.titre_nom.grid(row=0, column=1, padx=(20, 20), pady=(5, 20))

        self.titre_prix = ctk.CTkLabel(self, text="Prix", font=("Arial", 30, "bold"))
        self.titre_prix.grid(row=1, column=2, padx=(30, 0), pady=(5, 20))

        date = self.stocks[self.nom].index[0].date()
        self.date_label = ctk.CTkLabel(self, text=f"date : {date}", text_color="light gray", font=("Arial", 20))
        self.date_label.grid(row=0, column=3, padx=(0, 50), pady=(5, 10))

        self.categorie_open = ctk.CTkLabel(self, text="Ouverture", text_color="light gray", font=("Arial", 24))
        self.categorie_open.grid(row=2, column=0, padx=(10, 40), pady=(10, 10))

        self.categorie_close = ctk.CTkLabel(self, text="Fermeture", text_color="light gray", font=("Arial", 24))
        self.categorie_close.grid(row=3, column=0, padx=(10, 40), pady=(10, 10))

        self.categorie_high = ctk.CTkLabel(self, text="High", text_color="light gray", font=("Arial", 24))
        self.categorie_high.grid(row=4, column=0, padx=(10, 40), pady=(10, 10))

        self.categorie_low = ctk.CTkLabel(self, text="Low", text_color="light gray", font=("Arial", 24))
        self.categorie_low.grid(row=5, column=0, padx=(10, 40), pady=(10, 10))

        self.categorie_volume = ctk.CTkLabel(self, text="Volume", text_color="light gray", font=("Arial", 24))
        self.categorie_volume.grid(row=6, column=0, padx=(10, 40), pady=(10, 10))

        self.categorie_pourcentage = ctk.CTkLabel(self, text="Pourcentage", text_color="light gray", font=("Arial", 24))
        self.categorie_pourcentage.grid(row=7, column=0, padx=(10, 40), pady=(10, 10))

        self.categorie_variation = ctk.CTkLabel(self, text="Variation", text_color="light gray", font=("Arial", 24))
        self.categorie_variation.grid(row=8, column=0, padx=(10, 40), pady=(10, 10))

        self.open_label = ctk.CTkLabel(self, text="", text_color="light gray", font=("Arial", 24))
        self.open_label.grid(row=2, column=2, padx=(40, 0), pady=(10, 10))

        self.close_label = ctk.CTkLabel(self, text="", text_color="light gray", font=("Arial", 24))
        self.close_label.grid(row=3, column=2, padx=(40, 0), pady=(10, 10))

        self.high_label = ctk.CTkLabel(self, text="", text_color="light gray", font=("Arial", 24))
        self.high_label.grid(row=4, column=2, padx=(40, 0), pady=(10, 10))

        self.low_label = ctk.CTkLabel(self, text="", text_color="light gray", font=("Arial", 24))
        self.low_label.grid(row=5, column=2, padx=(40, 0), pady=(10, 10))

        self.volume_label = ctk.CTkLabel(self, text="", text_color="light gray", font=("Arial", 24))
        self.volume_label.grid(row=6, column=2, padx=(30, 0), pady=(10, 10))

        self.pourcentage_label = ctk.CTkLabel(self, text="", text_color="light gray", font=("Arial", 24))
        self.pourcentage_label.grid(row=7, column=2, padx=(40, 0), pady=(10, 10))

        self.variation_label = ctk.CTkLabel(self, text="", text_color="light gray", font=("Arial", 24))
        self.variation_label.grid(row=8, column=2, padx=(40, 0), pady=(10, 10))

        self.watchlist_button = ctk.CTkButton(self, text="retour", fg_color="transparent", hover_color="cyan",font=("Arial", 30, "bold"), command=self.retour)
        self.watchlist_button.grid(row=0, column=0, padx=(0, 0), pady=(5, 20))

        self.boucle_stock()

    def boucle_stock(self):
        if self.temps >= len(self.stocks[self.nom]['Close']):
            self.temps = 1

        stock = self.stocks[self.nom].iloc[self.temps]
        open = round(float(stock['Open']), 2)
        close = round(float(stock['Close']), 2)
        high = round(float(stock['High']), 2)
        low = round(float(stock['Low']), 2)
        volume = round(float(stock['Volume']), 2)
        pourcentage = round((close - open) / open * 100, 2)
        variation = round((close - open), 2)
        date = self.stocks[self.nom].index[self.temps].date()

        self.open_label.configure(text=open)
        self.close_label.configure(text=close)
        self.high_label.configure(text=high)
        self.low_label.configure(text=low)
        self.volume_label.configure(text=volume)
        self.pourcentage_label.configure(text=f"{pourcentage} %")
        self.variation_label.configure(text=variation)
        self.date_label.configure(text=f"date : {date}")

        self.temps += 1
        self.boucle_id = self.after(5000, self.boucle_stock)

    def clear_main_frame(self):
        if hasattr(self, "boucle_id"):
            self.after_cancel(self.boucle_id)
        for widget in self.winfo_children():
            widget.destroy()

    def retour(self):
        from watchlist import Watchlist
        self.clear_main_frame()
        Watchlist(self.master, self.stocks, self.temps, self.compte)