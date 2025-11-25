import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mdates
import traceback

class Graph(ctk.CTkFrame):
    def __init__(self, master=None, nom=None):
        super().__init__(master)
        self.master = master
        self.nom = nom

        # ids des callbacks mpl (initialisés à None)
        self._motion_cid = None
        self._scroll_cid = None

        # références sûres
        self.canvas = None
        self.fig = None
        self.ax = None
        self.price_text = None

        # bind destroy (proprement)
        self.bind("<Destroy>", self._on_destroy, add=True)

        self.create_widgets()

    def create_widgets(self):
        self.grid(row=0, column=0, padx=50, pady=50, sticky="nsew")

        try:
            self.master.grid_rowconfigure(0, weight=1)
            self.master.grid_columnconfigure(0, weight=1)
        except Exception:
            pass

        # --- figure & axes ---
        self.fig, self.ax = plt.subplots(figsize=(10, 7))
        self.fig.patch.set_facecolor("black")
        self.ax.set_facecolor("black")
        self.ax.set_title(f"Graphique de {self.nom}", color='white')

        for spine in self.ax.spines.values():
            spine.set_color("white")
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.title.set_color('white')
        self.ax.grid(False)

        # retour
        self.boutton_retour = ctk.CTkButton(
            self, text="⬅️", fg_color="transparent", hover_color="gray",
            font=("Arial", 40), command=self.retour
        )
        self.boutton_retour.grid(row=0, column=0, padx=5, pady=0, sticky="nsew")

        # canvas TK
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().grid(row=1, column=0, columnspan=3, pady=(10, 10))

        # connect scroll (zoom) et sauvegarde l'id
        def zoom(event):
            # sécurité : si l'app est en train de fermer, ne rien faire
            if not getattr(self.master, "app_is_active", True):
                return
            if getattr(event, "name", None) != 'scroll_event':
                return

            try:
                base_scale = 1.2
                if event.button == 'up':
                    scale_factor = 1 / base_scale
                elif event.button == 'down':
                    scale_factor = base_scale
                else:
                    return

                xlim = self.ax.get_xlim()
                xdata = event.xdata if event.xdata is not None else (xlim[0] + xlim[1]) / 2
                new_width = (xlim[1] - xlim[0]) * scale_factor
                relx = (xlim[1] - xdata) / (xlim[1] - xlim[0])
                self.ax.set_xlim([xdata - new_width * (1 - relx), xdata + new_width * relx])
                # draw sans exception si canvas détruit
                try:
                    self.canvas.draw_idle()
                except Exception:
                    pass
            except Exception:
                # jamais laisser une exception sortir d'un callback tkinter/mpl
                traceback.print_exc()

        try:
            self._scroll_cid = self.canvas.mpl_connect("scroll_event", zoom)
        except Exception:
            # fallback : canvas indisponible
            self._scroll_cid = None

        # dessine le graphique
        try:
            self.dessiner_graphique(self.master.stocks[self.nom])
        except Exception:
            traceback.print_exc()

    def dessiner_graphique(self, dataf):
        # sécurité : ne rien faire si la frame a été détruite
        if not getattr(self, "ax", None):
            return

        try:
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

            candlestick_ohlc(self.ax, ohlc, width=0.6, colorup='green', colordown='red', alpha=1.0)
            # une ligne légèrement visible (ou invisible) pour référence
            self.ax.plot(df["DateNum"], df["Close"], linestyle="-", linewidth=1, alpha=0.15, color="black")
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

            # prix affiché en haut-gauche (transform = axes)
            dernier_prix = float(df["Close"].iloc[-1])
            if self.price_text is None:
                self.price_text = self.ax.text(
                    0.01, 0.95, f"{dernier_prix:.2f} $",
                    color="white", fontsize=20,
                    transform=self.ax.transAxes, ha="left", va="top"
                )
            else:
                try:
                    self.price_text.set_text(f"{dernier_prix:.2f} $")
                except Exception:
                    # si price_text est invalide, recrée-le
                    try:
                        self.price_text = self.ax.text(
                            0.01, 0.95, f"{dernier_prix:.2f} $",
                            color="white", fontsize=20,
                            transform=self.ax.transAxes, ha="left", va="top"
                        )
                    except Exception:
                        pass

            # mouvement souris : update du texte (mais on ne crée pas d'annotation mobile)
            def _on_move(event):
                if not getattr(self.master, "app_is_active", True):
                    return
                try:
                    if event.inaxes is not self.ax:
                        return
                    x = event.xdata
                    if x is None:
                        return
                    arr = df["DateNum"].values
                    idx = int(np.argmin(np.abs(arr - x)))
                    prix = float(df["Close"].iloc[idx])
                    if self.price_text is not None:
                        # protège draw_idle contre exceptions après destruction
                        try:
                            self.price_text.set_text(f"{prix:.2f} $")
                            self.canvas.draw_idle()
                        except Exception:
                            pass
                except Exception:
                    traceback.print_exc()

            # (re)connecte le motion handler en stockant l'id
            try:
                if self._motion_cid is not None:
                    try:
                        self.canvas.mpl_disconnect(self._motion_cid)
                    except Exception:
                        pass
                    self._motion_cid = None
                self._motion_cid = self.canvas.mpl_connect("motion_notify_event", _on_move)
            except Exception:
                self._motion_cid = None

            # draw initial
            try:
                self.canvas.draw_idle()
            except Exception:
                pass

        except Exception:
            traceback.print_exc()

    # called automatically on Destroy events; event.widget may be child widgets too
    def _on_destroy(self, event):
        # ne déclencher cleanup que si c'est la frame elle-même qui est détruite
        if event.widget is not self:
            return
        self.cleanup()

    def cleanup(self):
        """Déconnecte proprement tous les callbacks et ferme la figure."""
        # déconnecte motion
        try:
            if getattr(self, "_motion_cid", None) is not None and getattr(self, "canvas", None) is not None:
                try:
                    self.canvas.mpl_disconnect(self._motion_cid)
                except Exception:
                    pass
                self._motion_cid = None
        except Exception:
            pass

        # déconnecte scroll
        try:
            if getattr(self, "_scroll_cid", None) is not None and getattr(self, "canvas", None) is not None:
                try:
                    self.canvas.mpl_disconnect(self._scroll_cid)
                except Exception:
                    pass
                self._scroll_cid = None
        except Exception:
            pass

        # retire le texte si présent
        try:
            if getattr(self, "price_text", None) is not None:
                try:
                    self.price_text.remove()
                except Exception:
                    pass
                self.price_text = None
        except Exception:
            pass

        # close figure (dernière étape)
        try:
            if getattr(self, "fig", None) is not None:
                try:
                    plt.close(self.fig)
                except Exception:
                    pass
                self.fig = None
                self.ax = None
        except Exception:
            pass

    def clear_main_frame(self):
        # utilisé quand on change de page volontairement
        self.cleanup()
        for widget in list(self.winfo_children()):
            try:
                widget.destroy()
            except Exception:
                pass

    def retour(self):
        # cleanup + retour à Watchlist
        self.clear_main_frame()
        from watchlist import Watchlist
        Watchlist(self.master)