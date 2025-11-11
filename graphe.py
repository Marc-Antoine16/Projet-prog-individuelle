import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplcursors
import pandas as pd
import numpy as np
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mdates


class Graph(ctk.CTkFrame):
    def __init__(self, master=None, stocks = None, nom = None, temps = None, compte = None):
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

        #Graphique initiale
        self.fig, self.ax = plt.subplots(figsize=(10, 7))
        self.fig.patch.set_facecolor("black")
        self.ax.set_facecolor("black")
        self.ax.set_title(f"Graphique de {self.nom}", color='white')

        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['left'].set_color('white')
        self.ax.spines['top'].set_color('white')
        self.ax.spines['right'].set_color('white')
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.title.set_color('white')

        self.boutton_retour = ctk.CTkButton(self, text= "⬅️", fg_color="transparent", hover_color="gray", font=("Arial", 40), command= self.retour)
        self.boutton_retour.grid(row=0, column=0, padx=5, pady=0, sticky="nsew")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().grid(row=1, column=0, columnspan=3, pady=(10, 10))

        def zoom(event):
            if event.name != 'scroll_event':
                return

            base_scale = 1.2

            # Sens du zoom
            if event.button == 'up':
                scale_factor = 1 / base_scale
            elif event.button == 'down':
                scale_factor = base_scale
            else:
                return

            # Limites actuelles
            xlim = self.ax.get_xlim()

            xdata = event.xdata if event.xdata is not None else (xlim[0] + xlim[1]) / 2

            # Nouvelle taille
            new_width = (xlim[1] - xlim[0]) * scale_factor

            # Calcul proportionnel
            relx = (xlim[1] - xdata) / (xlim[1] - xlim[0])

            # Mise à jour des axes
            self.ax.set_xlim([xdata - new_width * (1 - relx), xdata + new_width * relx])

            self.canvas.draw_idle()

        # Connecte l'événement de molette
        self.canvas.mpl_connect("scroll_event", zoom)
        
        self.dessiner_graphique(self.stocks[self.nom])

    def dessiner_graphique(self, dataf):
        self.ax.clear()

        self.ax.set_title(f"Graphique de {self.nom}", color='white')
        self.ax.set_facecolor("black")
        for spine in self.ax.spines.values():
            spine.set_color("white")
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.title.set_color('white')
        self.ax.grid(False)

        df = dataf.copy()

        df["DateNum"] = mdates.date2num(df.index)
        ohlc = df[["DateNum", "Open", "High", "Low", "Close"]].values

        candlestick_ohlc(self.ax, ohlc, width=0.6, colorup='green', colordown='red', alpha=0.9)

        price_text = self.ax.text(0.05, 0.90, "", transform=self.ax.transAxes, ha='left', va='top', fontsize=20, color='lightgray')

        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

        def on_move(event):
            if event.xdata and event.ydata:
                price_text.set_text(f"Prix : {event.ydata:.2f}")
                self.canvas.draw_idle()

        self.fig.canvas.mpl_connect("motion_notify_event", on_move)

        self.canvas.draw_idle()

    def clear_main_frame(self):
        for widget in self.winfo_children():
            widget.destroy()
        
    def retour(self):
        from watchlist import Watchlist
        self.clear_main_frame()
        self.watchlist = Watchlist(self.master, self.stocks, self.temps, self.compte)