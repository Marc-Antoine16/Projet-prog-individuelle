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

        self._motion_cid = None
        self._scroll_cid = None

        self.canvas = None
        self.fig = None
        self.ax = None
        self.price_text = None

        self.bind("<Destroy>", self._on_destroy, add=True)

        self.create_widgets()

    def create_widgets(self):
        self.grid(row=0, column=0, padx=50, pady=50, sticky="nsew")

        try:
            self.master.grid_rowconfigure(0, weight=1)
            self.master.grid_columnconfigure(0, weight=1)
        except Exception:
            pass

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

        self.boutton_retour = ctk.CTkButton(
            self, text="⬅️", fg_color="transparent", hover_color="gray",
            font=("Arial", 40), command=self.retour
        )
        self.boutton_retour.grid(row=0, column=0, padx=5, pady=0, sticky="nsew")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().grid(row=1, column=0, columnspan=3, pady=(10, 10))

        def zoom(event):
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
                try:
                    self.canvas.draw_idle()
                except Exception:
                    pass
            except Exception:
                traceback.print_exc()

        try:
            self._scroll_cid = self.canvas.mpl_connect("scroll_event", zoom)
        except Exception:
            self._scroll_cid = None

        try:
            self.dessiner_graphique(self.master.stocks[self.nom])
        except Exception:
            traceback.print_exc()

    def dessiner_graphique(self, dataf):
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
            self.ax.plot(df["DateNum"], df["Close"], linestyle="-", linewidth=1, alpha=0.15, color="black")
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

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
                    try:
                        self.price_text = self.ax.text(
                            0.01, 0.95, f"{dernier_prix:.2f} $",
                            color="white", fontsize=20,
                            transform=self.ax.transAxes, ha="left", va="top"
                        )
                    except Exception:
                        pass

            def _on_move(event):
                if self.master.app_is_active is False:
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
                        try:
                            self.price_text.set_text(f"{prix:.2f} $")
                            self.canvas.draw_idle()
                        except Exception:
                            pass
                except Exception:
                    traceback.print_exc()

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

            try:
                self.canvas.draw_idle()
            except Exception:
                pass

        except Exception:
            traceback.print_exc()

    def _on_destroy(self, event):
        if event.widget is not self:
            return
        self.cleanup()

    def cleanup(self):
        try:
            if getattr(self, "_motion_cid", None) is not None and getattr(self, "canvas", None) is not None:
                try:
                    self.canvas.mpl_disconnect(self._motion_cid)
                except Exception:
                    pass
                self._motion_cid = None
        except Exception:
            pass

        try:
            if getattr(self, "_scroll_cid", None) is not None and getattr(self, "canvas", None) is not None:
                try:
                    self.canvas.mpl_disconnect(self._scroll_cid)
                except Exception:
                    pass
                self._scroll_cid = None
        except Exception:
            pass

        try:
            if getattr(self, "price_text", None) is not None:
                try:
                    self.price_text.remove()
                except Exception:
                    pass
                self.price_text = None
        except Exception:
            pass

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
        self.cleanup()
        for widget in list(self.winfo_children()):
            try:
                widget.destroy()
            except Exception:
                pass

    def retour(self):
        self.clear_main_frame()
        from watchlist import Watchlist
        Watchlist(self.master)