import customtkinter as ctk

class Compte(ctk.CTkFrame):
    def __init__(self, master = None, action = None, argent = None):
        super().__init__(master)
        self.master = master
        self.action = action if action is not None else {}
        self.pause = False
        self.argent = float(argent)
        self.user = self.master.user

    def create_widgets(self):
        self.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.master.grid_rowconfigure(0, weight= 1)
        self.master.grid_columnconfigure(0, weight= 1)

        self.titre_label = ctk.CTkLabel(self, text="Compte", font=("Arial", 30, "bold"))
        self.titre_label.grid(row=0, column=2, padx = (10, 30), pady=(5,20))
        
        self.date_label = ctk.CTkLabel(self, text="", text_color="light gray", font=("Arial", 24))
        self.date_label.grid(row=0, column=4, padx=(0, 10), pady=(10,10))

        self.argent_label = ctk.CTkLabel(self, text=f"{self.argent:.2f} $", font=("Arial", 20, "bold"))
        self.argent_label.grid(row=0, column=5, padx=10, pady=5)

        self.watchlist_button = ctk.CTkButton(self, text="retour", fg_color = "transparent", hover_color= "cyan", font=("Arial", 30, "bold"), command= self.retour)
        self.watchlist_button.grid(row=0, column=0, padx = (0, 0), pady = (5,20))

        tittles = ["Action", "Quantité", "Prix d'achat", "Prix actuel", "Évolution (%)"]
        for col, text in enumerate(tittles):
            titre = ctk.CTkLabel(self, text=text, font=("Arial", 20, "bold"))
            titre.grid(row=1, column=col, padx=10, pady=(10, 20))

        i = 2
        for nom, info in self.action.items():
            prix_achat = info["prix_achat"]

            prix_actuel = round(info["data"]["Close"].iloc[self.master.temps].iloc[0], 2) if self.master.temps < len(info["data"]["Close"]) else round(info["data"]["Close"].iloc[-1].iloc[0], 2)

            pourcentage = round(float((prix_actuel - prix_achat) / prix_achat) * 100, 2)

            couleur = "green" if pourcentage >= 0 else "red"

            quantite = info["quantite"]

            ctk.CTkLabel(self, text=nom, font=("Arial", 20, "bold")).grid(row=i, column=0, padx=10, pady=5)
            ctk.CTkLabel(self, text=f"{quantite}", font=("Arial", 15)).grid(row=i, column=1, padx=10, pady=5)
            ctk.CTkLabel(self, text=f"{prix_achat:.2f} $", font=("Arial", 15)).grid(row=i, column=2, padx=10, pady=5)
            ctk.CTkLabel(self, text=f"{prix_actuel:.2f} $", font=("Arial", 15)).grid(row=i, column=3, padx=10, pady=5)
            ctk.CTkLabel(self, text=f"{pourcentage:+.2f} %", font=("Arial", 15), text_color=couleur).grid(row=i, column=4, padx=10, pady=5)

            bouton_vendre = ctk.CTkButton(self, text="Vendre", fg_color="transparent", hover_color="red", font=("Arial", 15), command=lambda a=nom: self.vendre_action(a))
            bouton_vendre.grid(row=i, column=5, padx=0, pady=5)

            i += 1
            
        self.update_affichage()

    def update_affichage(self):
        if self.master.temps == len(self.master.stocks[next(iter(self.master.stocks))]['Close']):
            self.master.temps = 1
        elif self.pause == False:
            for widget in list(self.winfo_children()):
                try:
                    info = widget.grid_info()
                    if info and info.get("row", 0) >= 2:
                        widget.destroy()
                except Exception:
                    continue

            i = 2
            for nom, info in self.action.items():
                prix_achat = float(info["prix_achat"])
                t = int(self.master.temps)
                try:
                    prix_actuel = float(info["data"]["Close"].iloc[t].iloc[0])
                except Exception:
                    prix_actuel = float(info["data"]["Close"].iloc[-1].iloc[0])

                pourcentage = round(((prix_actuel - prix_achat) / prix_achat) * 100, 2)
                couleur = "green" if pourcentage >= 0 else "red"
                quantite = info["quantite"]

                ctk.CTkLabel(self, text=nom, font=("Arial", 20, "bold")).grid(row=i, column=0, padx=10, pady=5)
                ctk.CTkLabel(self, text=f"{quantite}", font=("Arial", 15)).grid(row=i, column=1, padx=10, pady=5)
                ctk.CTkLabel(self, text=f"{prix_achat:.2f} $", font=("Arial", 15)).grid(row=i, column=2, padx=10, pady=5)
                ctk.CTkLabel(self, text=f"{prix_actuel:.2f} $", font=("Arial", 15)).grid(row=i, column=3, padx=10, pady=5)
                ctk.CTkLabel(self, text=f"{pourcentage:+.2f} %", font=("Arial", 15), text_color=couleur).grid(row=i, column=4, padx=10, pady=5)

                bouton_vendre = ctk.CTkButton(
                    self, text="Vendre",
                    fg_color="transparent",
                    hover_color="red",
                    font=("Arial", 15),
                    command=lambda a=nom: self.vendre_action(a)
                )
                bouton_vendre.grid(row=i, column=5, padx=0, pady=5)
                i += 1

            if len(self.master.stocks) > 0:
                premier_stock = next(iter(self.master.stocks))
                try:
                    date_str = str(self.master.stocks[premier_stock].index[self.master.temps].date())
                except Exception:
                    date_str = ""
                if hasattr(self, "date_label") and self.date_label.winfo_exists():
                    self.date_label.configure(text=date_str)
                else:
                    self.date_label = ctk.CTkLabel(self, text=date_str, text_color="light gray", font=("Arial", 24))
                    self.date_label.grid(row=0, column=4, padx=(0, 10), pady=(10, 10))

            if hasattr(self, "argent_label") and self.argent_label.winfo_exists():
                self.argent_label.configure(text=f"{self.argent:.2f} $")

            self.master.temps += 1
            self.boucle_id = self.after(5000, lambda: self.update_affichage())

    def clear_main_frame(self):
        if hasattr(self, "boucle_id"):
            self.after_cancel(self.boucle_id)
            
        for widget in self.winfo_children():
            widget.destroy()

    def vendre_action(self, action):
        if hasattr(self, "boucle_id"):
            try:
                self.after_cancel(self.boucle_id)
            except Exception:
                pass

        self.pause = True

        page_vente = ctk.CTkToplevel(self)
        page_vente.title(f"Vente de {action}")
        page_vente.geometry("420x300")
        page_vente.grab_set()

        page_vente.protocol("WM_DELETE_WINDOW", lambda: self.on_close_vente(page_vente))

        self.prix_action = round(float(self.master.stocks[action]["Close"].iloc[self.master.temps]), 2)
        quantite_max = self.action[action]["quantite"]

        ctk.CTkLabel(page_vente, text=f"Prix actuel : {self.prix_action:.2f}$", font=("Arial", 18, "bold")).pack(pady=(10, 5))
        ctk.CTkLabel(page_vente, text=f"Quantité maximale : {quantite_max}", font=("Arial", 15)).pack(pady=(0, 10))

        entry_frame = ctk.CTkFrame(page_vente)
        entry_frame.pack(pady=10)
        ctk.CTkLabel(entry_frame, text="Quantité à vendre :", font=("Arial", 16)).grid(row=0, column=0, padx=10)
        self.quantite_entry = ctk.CTkEntry(entry_frame, width=120)
        self.quantite_entry.grid(row=0, column=1, padx=10)

        self.error_label = ctk.CTkLabel(page_vente, text="", text_color="red", font=("Arial", 14))
        self.error_label.pack()

        self.submit_button = ctk.CTkButton(
            page_vente, 
            text="Valider la vente", 
            state="disabled", 
            font=("Arial", 16, "bold"), 
            command=lambda: self.valider_vente(page_vente, action)
        )
        self.submit_button.pack(pady=20)

        def on_entry_change(event=None):
            val = self.quantite_entry.get()
            if val.isdigit() and 0 < int(val) <= quantite_max:
                self.submit_button.configure(state="normal")
                self.error_label.configure(text="")
            else:
                self.submit_button.configure(state="disabled")
                if val != "":
                    self.error_label.configure(text=f"Entrez un nombre entre 1 et {quantite_max}")

        self.quantite_entry.bind("<KeyRelease>", on_entry_change)
    
    def on_close_vente(self, window):
        self.pause = False
        window.destroy()
        self.update_affichage()

    def valider_vente(self, page_vente, action):
        val = self.quantite_entry.get()
        if not val.isdigit():
            return
        val = int(val)

        info = self.action[action]
        quantite_actuelle = info["quantite"]

        if 0 < val <= quantite_actuelle:
            if self.master.temps < len(info["data"]["Close"]):
                prix_actuel = float(info["data"]["Close"].iloc[self.master.temps].iloc[0])
            else:
                prix_actuel = float(info["data"]["Close"].iloc[-1].iloc[0])

            self.argent += prix_actuel * val
            info["quantite"] -= val

            if info["quantite"] == 0:
                del self.action[action]

            page_vente.destroy()
            self.pause = False

            for widget in self.winfo_children():
                info = widget.grid_info()
                if info and info.get("row", 0) >= 2:
                    widget.destroy()

            i = 2
            for nom, info in self.action.items():
                prix_achat = float(info["prix_achat"])
                if self.master.temps < len(info["data"]["Close"]):
                    prix_actuel = float(round(info["data"]["Close"].iloc[self.master.temps].iloc[0], 2))
                else:
                    prix_actuel = float(round(info["data"]["Close"].iloc[-1].iloc[0], 2))

                pourcentage = round(((prix_actuel - prix_achat) / prix_achat) * 100, 2)
                couleur = "green" if pourcentage >= 0 else "red"
                quantite = info["quantite"]

                ctk.CTkLabel(self, text=nom, font=("Arial", 20, "bold")).grid(row=i, column=0, padx=10, pady=5)
                ctk.CTkLabel(self, text=f"{quantite}", font=("Arial", 15)).grid(row=i, column=1, padx=10, pady=5)
                ctk.CTkLabel(self, text=f"{prix_achat:.2f} $", font=("Arial", 15)).grid(row=i, column=2, padx=10, pady=5)
                ctk.CTkLabel(self, text=f"{prix_actuel:.2f} $", font=("Arial", 15)).grid(row=i, column=3, padx=10, pady=5)
                ctk.CTkLabel(self, text=f"{pourcentage:+.2f} %", font=("Arial", 15), text_color=couleur).grid(row=i, column=4, padx=10, pady=5)

                bouton_vendre = ctk.CTkButton(self, text="Vendre", fg_color="transparent", hover_color="red", font=("Arial", 15), command=lambda a=nom: self.vendre_action(a))
                bouton_vendre.grid(row=i, column=5, padx=0, pady=5)

                i += 1

            self.argent_label.configure(text=f"{self.argent:.2f} $")
            self.update_affichage()
            self.pause = False

    def retour(self):
        from watchlist import Watchlist
        self.clear_main_frame()
        Watchlist(self.master)