import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt

# Add these color constants at the start of your script, after your imports
DARK_BG = "#2C2F33"
DARK_FG = "#FFFFFF"
ACCENT_BLUE = "#7289DA"
ACCENT_GREEN = "#43B581"
ACCENT_RED = "#F04747"
ACCENT_ORANGE = "#FAA61A"

def calcola_cumulativo(tab):
    try:
        capitale_iniziale = float(tab.entry_capitale.get())
        tasso_crescita = float(tab.entry_tasso.get()) / 100
        periodi = int(tab.entry_periodi.get())
        etichetta = tab.entry_etichetta.get()

        valori = [capitale_iniziale * (1 + tasso_crescita) ** i for i in range(periodi + 1)]
        mostra_grafico(valori, etichetta)
        mostra_valori(valori, etichetta, tab)
    except ValueError:
        messagebox.showerror("Errore", "Inserisci valori validi.")

def mostra_grafico(valori, etichetta):
    plt.plot(valori, label=etichetta)
    plt.title("Crescita Cumulativa")
    plt.xlabel("Periodi")
    plt.ylabel("Valore Cumulativo")
    plt.grid()
    plt.legend()
    plt.show()

def mostra_valori(valori, etichetta, tab):
    tab.text_output.insert(tk.END, f"\nRisultati per '{etichetta}':\n")
    for i, valore in enumerate(valori):
        tab.text_output.insert(tk.END, f"Periodo {i}: {valore:.2f}\n")
    tab.text_output.insert(tk.END, "\n")

def aggiungi_tab():
    tab = ttk.Frame(tab_control)
    tab_control.add(tab, text="Nuova Simulazione")

    # Style for labels
    label_style = {"bg": DARK_BG, "fg": DARK_FG, "font": ("Helvetica", 10, "bold")}
    
    # Style for entry fields
    entry_style = {"bg": "#40444B", "fg": DARK_FG, "insertbackground": DARK_FG}

    # Create and style widgets
    label_etichetta = tk.Label(tab, text="Etichetta Simulazione:", **label_style)
    label_etichetta.pack(pady=5)
    entry_etichetta = tk.Entry(tab, **entry_style)
    entry_etichetta.pack()

    label_capitale = tk.Label(tab, text="Capitale Iniziale:", **label_style)
    label_capitale.pack(pady=5)
    entry_capitale = tk.Entry(tab, **entry_style)
    entry_capitale.pack()

    label_tasso = tk.Label(tab, text="Tasso di Crescita (%):", **label_style)
    label_tasso.pack(pady=5)
    entry_tasso = tk.Entry(tab, **entry_style)
    entry_tasso.pack()

    label_periodi = tk.Label(tab, text="Numero di Periodi:", **label_style)
    label_periodi.pack(pady=5)
    entry_periodi = tk.Entry(tab, **entry_style)
    entry_periodi.pack()

    # Button styles
    button_style = {"font": ("Helvetica", 9, "bold"), "borderwidth": 0, "padx": 20, "pady": 5}

    tab.button_calcola = tk.Button(tab, text="CALCOLA", command=lambda: calcola_cumulativo(tab),
                                 bg=ACCENT_BLUE, fg=DARK_FG, **button_style)
    tab.button_calcola.pack(pady=10)

    tab.button_rinomina = tk.Button(tab, text="RINOMINA", command=lambda: rinomina_tab(tab),
                                  bg=ACCENT_ORANGE, fg=DARK_FG, **button_style)
    tab.button_rinomina.pack(pady=5)

    tab.button_chiudi = tk.Button(tab, text="CHIUDI", command=lambda: chiudi_tab(tab),
                                bg=ACCENT_RED, fg=DARK_FG, **button_style)
    tab.button_chiudi.pack(pady=5)

    # Style text output
    text_output = tk.Text(tab, height=15, width=50, bg="#40444B", fg=DARK_FG,
                         insertbackground=DARK_FG, font=("Consolas", 10))
    text_output.pack(pady=10)

    # Save references
    tab.entry_etichetta = entry_etichetta
    tab.entry_capitale = entry_capitale
    tab.entry_tasso = entry_tasso
    tab.entry_periodi = entry_periodi
    tab.text_output = text_output

def rinomina_tab(tab):
    nuova_etichetta = tab.entry_etichetta.get()
    if nuova_etichetta:
        tab_control.tab(tab, text=nuova_etichetta)

def chiudi_tab(tab):
    tab_control.forget(tab)

# Creazione della finestra principale
root = tk.Tk()
root.title("Calcolatore Cumulativo")
root.configure(bg=DARK_BG)
style = ttk.Style()
style.theme_use('default')
style.configure('TNotebook.Tab', background=DARK_BG, foreground='black')
style.configure('TFrame', background=DARK_BG)
style.configure('TNotebook', background=DARK_BG)

# Creazione del controllo delle schede
tab_control = ttk.Notebook(root)
tab_control.pack(expand=1, fill="both")

# Aggiungi la prima scheda
aggiungi_tab()

# Pulsante per aggiungere nuove schede
button_nuova_simulazione = tk.Button(root, text="NUOVA SIMULAZIONE",
                                   command=aggiungi_tab,
                                   bg=ACCENT_GREEN, fg=DARK_FG,
                                   font=("Helvetica", 9, "bold"),
                                   borderwidth=0, padx=20, pady=5)
button_nuova_simulazione.pack(pady=10)

root.mainloop()
