import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from scipy.stats import norm

# Parametri di simulazione
n_simulazioni = 10000
n_scambi = 500
commissione_per_contratto = 1.50
valore_tick = 1.25
stop_loss_ticks = 15
take_profit_ticks = 20
win_rate = 0.60
capitale_iniziale = 600

def simula_trade(n_contratti):
    """Simula un trade con commissioni e stop fissi"""
    is_win = np.random.rand() < win_rate
    ticks = take_profit_ticks if is_win else -stop_loss_ticks
    profitto = ticks * valore_tick * n_contratti
    commissione = 2 * commissione_per_contratto * n_contratti
    return profitto - commissione, is_win

def max_drawdown(equity_curve):
    """Calcola il drawdown massimo"""
    running_max = np.maximum.accumulate(equity_curve)
    return np.max(running_max - equity_curve)

def run_simulazione():
    """Esegue una simulazione completa"""
    capitale = capitale_iniziale
    storico = [capitale]
    stats = {
        'trade_totali': 0,
        'win_count': 0,
        'loss_count': 0,
        'somma_wins': 0.0,
        'somma_losses': 0.0,
        'losing_streaks': [],
        'current_streak': 0,
        'tick_loss_accumulati': 0
    }

    for _ in range(n_scambi):
        stats['trade_totali'] += 1
        risultato, is_win = simula_trade(1)  # Sempre 1 contratto
        
        capitale += risultato
        storico.append(capitale)
        
        if is_win:
            stats['win_count'] += 1
            stats['somma_wins'] += risultato
            if stats['current_streak'] > 0:
                stats['losing_streaks'].append({
                    'length': stats['current_streak'],
                    'tick_loss': stats['tick_loss_accumulati']
                })
                stats['current_streak'] = 0
                stats['tick_loss_accumulati'] = 0
        else:
            stats['loss_count'] += 1
            stats['somma_losses'] += risultato
            stats['current_streak'] += 1
            stats['tick_loss_accumulati'] += stop_loss_ticks
        
        if capitale <= 0:
            break

    if stats['current_streak'] > 0:
        stats['losing_streaks'].append({
            'length': stats['current_streak'],
            'tick_loss': stats['tick_loss_accumulati']
        })

    return {
        'capitale_finale': capitale,
        'storico_saldo': storico,
        'drawdown_massimo': max_drawdown(np.array(storico)),
        'stats': stats
    }

# Esecuzione simulazioni
risultati = [run_simulazione() for _ in range(n_simulazioni)]

# Estrazione dati
capitali_finali = [r['capitale_finale'] for r in risultati]
drawdowns = [r['drawdown_massimo'] for r in risultati]
tutti_streaks = [streak for res in risultati for streak in res['stats']['losing_streaks']]

# Calcolo evoluzione media del capitale
lunghezza_massima = max(len(r['storico_saldo']) for r in risultati)
storici_allineati = np.zeros((n_simulazioni, lunghezza_massima))
storici_allineati.fill(np.nan)
for i, r in enumerate(risultati):
    storici_allineati[i, :len(r['storico_saldo'])] = r['storico_saldo']

evoluzione_media_capitale = np.nanmean(storici_allineati, axis=0)

# Calcolo statistiche
stat_globali = {
    'capitale_medio': np.mean(capitali_finali),
    'capitale_mediano': np.median(capitali_finali),
    'varianza': np.var(capitali_finali),
    'dev_std': np.std(capitali_finali),
    'q1': np.percentile(capitali_finali, 25),
    'q3': np.percentile(capitali_finali, 75),
    'max': np.max(capitali_finali),
    'min': np.min(capitali_finali),
    'drawdown_medio': np.mean(drawdowns),
    'prob_bancarotta': sum(1 for c in capitali_finali if c <= 0) / n_simulazioni,
    'sotto_capitale_iniziale': sum(1 for c in capitali_finali if c < capitale_iniziale)
}

# Stampa delle statistiche
print("Statistiche Globali:")
for k, v in stat_globali.items():
    print(f"{k}: {v}")

# Visualizzazione
plt.figure(figsize=(18, 10))

# Grafico 1: Distribuzione capitali
plt.subplot(2, 2, 1)
plt.hist(capitali_finali, bins=50, density=True, alpha=0.7)
x = np.linspace(min(capitali_finali), max(capitali_finali), 100)
plt.plot(x, norm.pdf(x, stat_globali['capitale_medio'], stat_globali['dev_std']), 'r--')
plt.title('Distribuzione Capitali Finali')
plt.xlabel('Capitale ($)')
plt.ylabel('Densità')

# Grafico 2: Evoluzione media del capitale
plt.subplot(2, 2, 2)
plt.plot(evoluzione_media_capitale, label='Evoluzione Media Capitale', color='b')
plt.title('Evoluzione Media del Capitale')
plt.xlabel('Numero di Scambi')
plt.ylabel('Capitale Medio ($)')
plt.legend()

# Grafico 3: Andamento della simulazione per ogni scambio
plt.subplot(2, 1, 2)
for storico in storici_allineati:
    plt.plot(storico, color='gray', alpha=0.1)
plt.plot(evoluzione_media_capitale, color='blue', linewidth=2, label='Media')
plt.title('Andamento della Simulazione per Ogni Scambio')
plt.xlabel('Numero di Scambi')
plt.ylabel('Capitale ($)')
plt.legend()

plt.tight_layout()
plt.show()
