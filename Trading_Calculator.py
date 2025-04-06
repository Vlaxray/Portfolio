import tkinter as tk
from tkinter import messagebox

# Variabili globali per il calcolo del winrate
wins = 0
losses = 0

# Funzione per calcolare il valore ATR modificato
def calcola_atr():
    try:
        atr = float(entry_atr.get())
        moltiplicatore1 = float(entry_moltiplicatore1.get())
        moltiplicatore2 = float(entry_moltiplicatore2.get())
        risultato = atr * moltiplicatore1 * moltiplicatore2
        label_atr_result.config(text=f"ATR: {risultato:.2f}")
    except ValueError:
        messagebox.showerror("Errore", "Inserisci numeri validi!")

# Funzione per calcolare il numero di contratti
def calcola_contratti():
    try:
        capitale = float(entry_capitale.get())
        valore_tick = float(entry_valore_tick.get())
        take_profit = float(entry_take_profit.get())
        contratti = (capitale / valore_tick) / take_profit
        label_contratti_result.config(text=f"Contratti: {contratti:.2f}")
    except ValueError:
        messagebox.showerror("Errore", "Inserisci numeri validi!")

# Funzione per aggiornare il winrate
def aggiorna_winrate():
    global wins, losses
    totale = wins + losses
    winrate = (wins / totale * 100) if totale > 0 else 0
    label_winrate.config(text=f"Winrate: {winrate:.2f}% ({wins}W - {losses}L)")

# Funzione per aggiungere una vittoria
def aggiungi_win():
    global wins
    wins += 1
    aggiorna_winrate()

# Funzione per aggiungere una sconfitta
def aggiungi_loss():
    global losses
    losses += 1
    aggiorna_winrate()

# Funzione per resettare il winrate
def reset_winrate():
    global wins, losses
    wins = 0
    losses = 0
    aggiorna_winrate()

# Creiamo la finestra principale
root = tk.Tk()
root.title("Calcolatore ATR & Winrate & Contratti")
root.configure(bg="#2c3e50")
root.geometry("690x400")

# Layout con frame
frame_winrate = tk.Frame(root, bg="#2c3e50")
frame_winrate.pack(side="left", padx=20, pady=20)

frame_contratti = tk.Frame(root, bg="#2c3e50")
frame_contratti.pack(side="left", padx=20, pady=20)

frame_atr = tk.Frame(root, bg="#2c3e50")
frame_atr.pack(side="left", padx=20, pady=20)

### SEZIONE WINRATE (A SINISTRA) ###
label_winrate_title = tk.Label(frame_winrate, text="Winrate", font=("Helvetica", 14, "bold"), fg="white", bg="#2c3e50")
label_winrate_title.pack()

label_winrate = tk.Label(frame_winrate, text="Winrate: 0.00% (0W - 0L)", font=("Helvetica", 12), fg="white", bg="#2c3e50")
label_winrate.pack()

win_button = tk.Button(frame_winrate, text="Win", font=("Helvetica", 12), bg="#2ecc71", fg="white", command=aggiungi_win, relief="solid")
win_button.pack(pady=5)

loss_button = tk.Button(frame_winrate, text="Loss", font=("Helvetica", 12), bg="#e74c3c", fg="white", command=aggiungi_loss, relief="solid")
loss_button.pack(pady=5)

reset_button = tk.Button(frame_winrate, text="Reset", font=("Helvetica", 12), bg="#f39c12", fg="white", command=reset_winrate, relief="solid")
reset_button.pack(pady=5)

### SEZIONE CALCOLO CONTRATTI (AL CENTRO) ###
label_contratti_title = tk.Label(frame_contratti, text="Calcolo Contratti", font=("Helvetica", 14, "bold"), fg="white", bg="#2c3e50")
label_contratti_title.pack()

label_capitale = tk.Label(frame_contratti, text="Perdita da recup. (in €):", font=("Helvetica", 12), fg="white", bg="#2c3e50")
label_capitale.pack()
entry_capitale = tk.Entry(frame_contratti, font=("Helvetica", 12), bg="#34495e", fg="white", borderwidth=2, relief="solid")
entry_capitale.pack()

label_valore_tick = tk.Label(frame_contratti, text="Valore Tick:", font=("Helvetica", 12), fg="white", bg="#2c3e50")
label_valore_tick.pack()
entry_valore_tick = tk.Entry(frame_contratti, font=("Helvetica", 12), bg="#34495e", fg="white", borderwidth=2, relief="solid")
entry_valore_tick.pack()

label_take_profit = tk.Label(frame_contratti, text="Take Profit:", font=("Helvetica", 12), fg="white", bg="#2c3e50")
label_take_profit.pack()
entry_take_profit = tk.Entry(frame_contratti, font=("Helvetica", 12), bg="#34495e", fg="white", borderwidth=2, relief="solid")
entry_take_profit.pack()

calculate_contratti_button = tk.Button(frame_contratti, text="Calcola Contratti", font=("Helvetica", 12), bg="#1abc9c", fg="white", command=calcola_contratti, relief="solid")
calculate_contratti_button.pack(pady=5)

label_contratti_result = tk.Label(frame_contratti, text="Contratti: --", font=("Helvetica", 12), fg="white", bg="#2c3e50")
label_contratti_result.pack()

### SEZIONE CALCOLO ATR (A DESTRA) ###
label_atr_title = tk.Label(frame_atr, text="Calcolo ATR", font=("Helvetica", 14, "bold"), fg="white", bg="#2c3e50")
label_atr_title.pack()

label_atr = tk.Label(frame_atr, text="Inserisci ATR:", font=("Helvetica", 12), fg="white", bg="#2c3e50")
label_atr.pack()
entry_atr = tk.Entry(frame_atr, font=("Helvetica", 12), bg="#34495e", fg="white", borderwidth=2, relief="solid")
entry_atr.pack()

label_moltiplicatore1 = tk.Label(frame_atr, text="Moltiplicatore 1 (Tick):", font=("Helvetica", 12), fg="white", bg="#2c3e50")
label_moltiplicatore1.pack()
entry_moltiplicatore1 = tk.Entry(frame_atr, font=("Helvetica", 12), bg="#34495e", fg="white", borderwidth=2, relief="solid")
entry_moltiplicatore1.pack()

label_moltiplicatore2 = tk.Label(frame_atr, text="Moltiplicatore 2:", font=("Helvetica", 12), fg="white", bg="#2c3e50")
label_moltiplicatore2.pack()
entry_moltiplicatore2 = tk.Entry(frame_atr, font=("Helvetica", 12), bg="#34495e", fg="white", borderwidth=2, relief="solid")
entry_moltiplicatore2.pack()

calculate_atr_button = tk.Button(frame_atr, text="Calcola ATR", font=("Helvetica", 12), bg="#1abc9c", fg="white", command=calcola_atr, relief="solid")
calculate_atr_button.pack(pady=5)

label_atr_result = tk.Label(frame_atr, text="ATR: --", font=("Helvetica", 12), fg="white", bg="#2c3e50")
label_atr_result.pack()

root.mainloop()
