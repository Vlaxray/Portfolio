import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import os
from ttkbootstrap import Style
from tkinter import font as tkfont

class BarrierOptionsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Barrier Options Trading App")
        self.root.geometry("820x940")

        # Applica un tema scuro di ttkbootstrap
        self.style = Style(theme="darkly")
        self.root.configure(bg=self.style.colors.primary)

        # Variabili
        self.capitale = 3000.0  # Capitale iniziale
        self.storia_capitale = [self.capitale]  # Storia del capitale
        self.win_count = 0  # Conteggio trade vincenti
        self.loss_count = 0  # Conteggio trade perdenti
        self.net_win = 0.0  # Guadagno totale
        self.net_loss = 0.0  # Perdita totale
        self.rischio_per_trade = 0.02  # Percentuale di rischio predefinita (2%)

        # Carica i dati salvati (se esistono)
        self.carica_dati()

        # Interfaccia grafica
        self.create_widgets()

    def create_widgets(self):
        # Frame principale
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Titolo
        title_font = tkfont.Font(family="Helvetica", size=16, weight="bold")
        ttk.Label(main_frame, text="Barrier Options Trading App", font=title_font, foreground="#00ff99").grid(row=0, column=0, columnspan=3, pady=10)

        # Etichetta capitale attuale
        self.label_capitale = ttk.Label(main_frame, text=f"💰 Capitale Attuale: €{self.capitale:.2f}", font=("Helvetica", 14))
        self.label_capitale.grid(row=1, column=0, columnspan=3, pady=10)

        # Pulsante per modificare il capitale
        ttk.Button(main_frame, text="✏️ Modifica Capitale", command=self.modifica_capitale, style="success.TButton").grid(row=2, column=0, pady=10)

        # Input percentuale di rischio
        ttk.Label(main_frame, text="📉 Rischio per Trade (%):", font=("Helvetica", 12)).grid(row=3, column=0, pady=5)
        self.rischio_entry = ttk.Entry(main_frame, width=10, font=("Helvetica", 12))
        self.rischio_entry.grid(row=3, column=1, pady=5)
        self.rischio_entry.insert(0, str(self.rischio_per_trade * 100))  # Valore predefinito

        # Pulsante per aggiornare la percentuale di rischio
        ttk.Button(main_frame, text="🔄 Aggiorna Rischio", command=self.aggiorna_rischio, style="info.TButton").grid(row=3, column=2, pady=5)

        # Etichetta puntata suggerita
        self.label_puntata = ttk.Label(main_frame, text=f"💡 Puntata Suggerita: €{self.capitale * self.rischio_per_trade:.2f}", font=("Helvetica", 12))
        self.label_puntata.grid(row=4, column=0, columnspan=3, pady=10)

        # Input importo vinto/perso
        ttk.Label(main_frame, text="💸 Importo Vinto/Perduto (€):", font=("Helvetica", 12)).grid(row=5, column=0, pady=5)
        self.importo_entry = ttk.Entry(main_frame, width=10, font=("Helvetica", 12))
        self.importo_entry.grid(row=5, column=1, pady=5)

        # Selezione risultato trade
        ttk.Label(main_frame, text="📊 Risultato Trade:", font=("Helvetica", 12)).grid(row=6, column=0, pady=5)
        self.trade_result = ttk.Combobox(main_frame, values=["Successo", "Fallimento"], font=("Helvetica", 12))
        self.trade_result.grid(row=6, column=1, pady=5)
        self.trade_result.set("Successo")  # Default

        # Pulsante per registrare il trade
        ttk.Button(main_frame, text="📝 Registra Trade", command=self.registra_trade, style="primary.TButton").grid(row=7, column=0, columnspan=3, pady=10)

        # Statistiche Win/Loss
        self.label_statistiche = ttk.Label(main_frame, text="📈 Win/Loss: 0% | Net Win: €0.00 | Net Loss: €0.00", font=("Helvetica", 12))
        self.label_statistiche.grid(row=8, column=0, columnspan=3, pady=10)

        # Grafico del capitale nel tempo
        self.fig, self.ax = plt.subplots(figsize=(8, 5), facecolor="#2e3440")
        self.ax.set_facecolor("#2e3440")
        self.ax.tick_params(colors="white")
        self.ax.xaxis.label.set_color("white")
        self.ax.yaxis.label.set_color("white")
        self.ax.title.set_color("white")
        self.canvas = FigureCanvasTkAgg(self.fig, master=main_frame)
        self.canvas.get_tk_widget().grid(row=9, column=0, columnspan=3, pady=10)
        self.aggiorna_grafico()

    def modifica_capitale(self):
        # Finestra per modificare il capitale
        def salva_capitale():
            try:
                nuovo_capitale = float(capitale_entry.get())
                self.capitale = nuovo_capitale
                self.storia_capitale.append(self.capitale)
                self.label_capitale.config(text=f"💰 Capitale Attuale: €{self.capitale:.2f}")
                self.label_puntata.config(text=f"💡 Puntata Suggerita: €{self.capitale * self.rischio_per_trade:.2f}")
                self.aggiorna_grafico()
                modifica_window.destroy()
            except ValueError:
                messagebox.showerror("Errore", "Inserisci un valore numerico valido.")

        modifica_window = tk.Toplevel(self.root)
        modifica_window.title("Modifica Capitale")
        ttk.Label(modifica_window, text="Nuovo Capitale (€):", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=10)
        capitale_entry = ttk.Entry(modifica_window, width=10, font=("Helvetica", 12))
        capitale_entry.grid(row=0, column=1, padx=10, pady=10)
        ttk.Button(modifica_window, text="💾 Salva", command=salva_capitale, style="success.TButton").grid(row=1, column=0, columnspan=2, pady=10)

    def aggiorna_rischio(self):
        # Aggiorna la percentuale di rischio
        try:
            self.rischio_per_trade = float(self.rischio_entry.get()) / 100
            self.label_puntata.config(text=f"💡 Puntata Suggerita: €{self.capitale * self.rischio_per_trade:.2f}")
        except ValueError:
            messagebox.showerror("Errore", "Inserisci un valore numerico valido per la percentuale di rischio.")

    def registra_trade(self):
        # Ottieni l'importo inserito
        try:
            importo = float(self.importo_entry.get())
        except ValueError:
            messagebox.showerror("Errore", "Inserisci un importo valido.")
            return

        # Aggiorna il capitale in base al risultato
        risultato = self.trade_result.get()
        if risultato == "Successo":
            self.capitale += importo
            self.win_count += 1
            self.net_win += importo
        else:
            self.capitale -= importo
            self.loss_count += 1
            self.net_loss += importo

        # Aggiungi il capitale alla storia
        self.storia_capitale.append(self.capitale)

        # Aggiorna l'interfaccia
        self.label_capitale.config(text=f"💰 Capitale Attuale: €{self.capitale:.2f}")
        self.label_puntata.config(text=f"💡 Puntata Suggerita: €{self.capitale * self.rischio_per_trade:.2f}")
        self.aggiorna_statistiche()
        self.aggiorna_grafico()

        # Salva i dati
        self.salva_dati()

        # Mostra un messaggio se il capitale è esaurito
        if self.capitale <= 0:
            messagebox.showwarning("Attenzione", "Il capitale è esaurito. Ricarica per continuare.")

    def aggiorna_statistiche(self):
        # Calcola le statistiche Win/Loss
        total_trades = self.win_count + self.loss_count
        win_rate = (self.win_count / total_trades * 100) if total_trades > 0 else 0
        self.label_statistiche.config(
            text=f"📈 Win/Loss: {win_rate:.2f}% | Net Win: €{self.net_win:.2f} | Net Loss: €{self.net_loss:.2f}"
        )

    def aggiorna_grafico(self):
        # Aggiorna il grafico del capitale
        self.ax.clear()
        self.ax.plot(self.storia_capitale, marker='o', linestyle='-', color='#00ff99')
        self.ax.set_title("Andamento del Capitale", color="white")
        self.ax.set_xlabel("Trade", color="white")
        self.ax.set_ylabel("Capitale (€)", color="white")
        self.canvas.draw()

    def salva_dati(self):
        # Salva i dati in un file JSON
        dati = {
            "capitale": self.capitale,
            "storia_capitale": self.storia_capitale,
            "win_count": self.win_count,
            "loss_count": self.loss_count,
            "net_win": self.net_win,
            "net_loss": self.net_loss,
            "rischio_per_trade": self.rischio_per_trade
        }
        with open("dati_trading.json", "w") as file:
            json.dump(dati, file)

    def carica_dati(self):
        # Carica i dati da un file JSON (se esiste)
        if os.path.exists("dati_trading.json"):
            with open("dati_trading.json", "r") as file:
                dati = json.load(file)
                self.capitale = dati["capitale"]
                self.storia_capitale = dati["storia_capitale"]
                self.win_count = dati["win_count"]
                self.loss_count = dati["loss_count"]
                self.net_win = dati["net_win"]
                self.net_loss = dati["net_loss"]
                self.rischio_per_trade = dati["rischio_per_trade"]

# Avvia l'app
if __name__ == "__main__":
    root = tk.Tk()
    app = BarrierOptionsApp(root)
    root.mainloop()