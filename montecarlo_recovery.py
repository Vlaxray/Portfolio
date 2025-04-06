import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

# Parametri di simulazione
n_simulazioni = 1000
n_scambi = 5000
commissione_per_contratto = 1.50
valore_tick = 1.25
stop_loss_ticks = 19
take_profit_ticks = 25
win_rate = 0.53
max_contratti = 4
capitale_iniziale = 500

def simula_trade(n_contratti):
    """
    Simula un singolo trade con commissioni e stop loss/take profit fissi.
    Restituisce il profitto in dollari e se il trade è vincente.
    Le commissioni sono 1.5 in entrata e 1.5 in uscita per contratto.
    """
    is_win = np.random.rand() < win_rate
    if is_win:
        ticks = take_profit_ticks
        profitto = ticks * valore_tick * n_contratti
    else:
        ticks = -stop_loss_ticks
        profitto = ticks * valore_tick * n_contratti
    commissione = 2 * commissione_per_contratto * n_contratti
    return profitto - commissione, is_win

def max_drawdown(equity_curve):
    """
    Calcola il drawdown massimo dato un array dell'andamento del capitale.
    """
    running_max = np.maximum.accumulate(equity_curve)
    drawdowns = running_max - equity_curve
    return np.max(drawdowns)

def run_simulazione():
    """
    Esegue una simulazione completa:
      - Se il trade è vincente, il trade successivo si esegue con 1 contratto.
      - Se il trade è perdente, si accumulano i tick persi e si aumenta il numero
        di contratti secondo: n_contratti * take_profit_ticks >= tick_loss_accumulati.
    Registra inoltre le statistiche sui trade (numero, win, loss, guadagni e perdite).
    Restituisce il capitale finale, lo storico del capitale, le losing streak, il drawdown massimo
    e le statistiche sui trade.
    """
    capitale = capitale_iniziale
    storico_saldo = [capitale]
    
    # Statistiche trade
    trade_totali = 0
    win_count = 0
    loss_count = 0
    somma_wins = 0.0
    somma_losses = 0.0
    
    # Accumulo dei tick persi e gestione dei contratti
    tick_loss_accumulati = 0
    n_contratti = 1
    
    losing_streaks = []
    current_streak = 0
    current_max_contratti = 1

    for _ in range(n_scambi):
        trade_totali += 1
        trade_result, is_win = simula_trade(n_contratti)
        capitale += trade_result
        storico_saldo.append(capitale)
        
        if is_win:
            win_count += 1
            somma_wins += trade_result
            # Se c'era una losing streak, la registra prima di resettare
            if current_streak > 0:
                losing_streaks.append({
                    'length': current_streak,
                    'max_contratti': current_max_contratti,
                    'tick_loss_totali': tick_loss_accumulati
                })
            # Reset: trade vincente porta sempre al reset a 1 contratto
            current_streak = 0
            current_max_contratti = 1
            tick_loss_accumulati = 0
            n_contratti = 1
        else:
            loss_count += 1
            somma_losses += trade_result  # trade_result è negativo per le perdite
            current_streak += 1
            # Accumula i tick persi: per ogni contratto si perde stop_loss_ticks
            tick_loss_accumulati += stop_loss_ticks * n_contratti
            current_max_contratti = max(current_max_contratti, n_contratti)
            # Calcola i contratti necessari per recuperare i tick persi
            n_contratti = min(max(1, int(np.ceil(tick_loss_accumulati / take_profit_ticks))), max_contratti)
        
        if capitale <= 0:
            break

    # Se la simulazione termina con una losing streak attiva, la registra
    if current_streak > 0:
        losing_streaks.append({
            'length': current_streak,
            'max_contratti': current_max_contratti,
            'tick_loss_totali': tick_loss_accumulati
        })
    
    dd = max_drawdown(np.array(storico_saldo))
    
    # Calcola expectancy (guadagno medio per trade) e profit factor
    expectancy = (somma_wins + somma_losses) / trade_totali if trade_totali > 0 else 0
    profit_factor = abs(somma_wins / somma_losses) if somma_losses != 0 else np.nan

    return {
        'capitale_finale': capitale,
        'storico_saldo': storico_saldo,
        'losing_streaks': losing_streaks,
        'drawdown_massimo': dd,
        'trade_totali': trade_totali,
        'win_count': win_count,
        'loss_count': loss_count,
        'somma_wins': somma_wins,
        'somma_losses': somma_losses,
        'expectancy': expectancy,
        'profit_factor': profit_factor
    }

# Esecuzione delle simulazioni
risultati = [run_simulazione() for _ in range(n_simulazioni)]

# Elaborazione delle losing streaks
streak_stats = defaultdict(lambda: {
    'count': 0,
    'max_contratti': [],
    'tick_loss_totali': []
})
for res in risultati:
    for streak in res['losing_streaks']:
        length = streak['length']
        streak_stats[length]['count'] += 1
        streak_stats[length]['max_contratti'].append(streak['max_contratti'])
        streak_stats[length]['tick_loss_totali'].append(streak['tick_loss_totali'])

for length in streak_stats:
    stats = streak_stats[length]
    stats['contratti_avg'] = np.mean(stats['max_contratti']) if stats['count'] > 0 else 0
    stats['contratti_max'] = np.max(stats['max_contratti']) if stats['count'] > 0 else 0
    stats['contratti_min'] = np.min(stats['max_contratti']) if stats['count'] > 0 else 0
    stats['tick_loss_avg'] = np.mean(stats['tick_loss_totali']) if stats['count'] > 0 else 0

# Statistiche sul drawdown
drawdowns = [res['drawdown_massimo'] for res in risultati]
drawdown_massimo_medio = np.mean(drawdowns)
drawdown_massimo_totale = np.max(drawdowns)

# Numero di simulazioni perdenti (capitale finale < capitale iniziale)
n_simulazioni_perdenti = sum(1 for res in risultati if res['capitale_finale'] < capitale_iniziale)
percentuale_perdenti = n_simulazioni_perdenti / n_simulazioni * 100

# Statistiche sui trade aggregati (somma su tutte le simulazioni)
totale_trade = sum(res['trade_totali'] for res in risultati)
totale_win = sum(res['win_count'] for res in risultati)
totale_loss = sum(res['loss_count'] for res in risultati)
somma_win_totale = sum(res['somma_wins'] for res in risultati)
somma_loss_totale = sum(res['somma_losses'] for res in risultati)
expectancy_media = (somma_win_totale + somma_loss_totale) / totale_trade if totale_trade > 0 else 0
profit_factor_aggregato = abs(somma_win_totale / somma_loss_totale) if somma_loss_totale != 0 else np.nan
win_rate_osservato = totale_win / totale_trade * 100 if totale_trade > 0 else 0

# Stampa delle statistiche delle losing streaks
print("\nSTATISTICHE DETTAGLIATE DELLE LOSING STREAKS")
print("=" * 90)
print(f"{'Lunghezza':<10} | {'Occorrenze':<10} | {'Contratti Avg':<12} | {'Contratti Max':<12} | {'Contratti Min':<12} | {'Tick Loss Media':<15}")
print("-" * 90)
sorted_lengths = sorted(streak_stats.keys())
for length in sorted_lengths:
    if streak_stats[length]['count'] > 0:
        stats = streak_stats[length]
        print(f"{length:<10} | {stats['count']:<10} | {stats['contratti_avg']:<12.1f} | {stats['contratti_max']:<12} | {stats['contratti_min']:<12} | {stats['tick_loss_avg']:>10.1f}")

# Stampa delle statistiche sul drawdown
print("\nSTATISTICHE DRAWDOWN")
print("=" * 90)
print(f"Drawdown massimo medio: ${drawdown_massimo_medio:,.2f}")
print(f"Drawdown massimo totale: ${drawdown_massimo_totale:,.2f}")

# Stampa delle simulazioni perdenti
print("\nSIMULAZIONI PERDENTI")
print("=" * 90)
print(f"Numero simulazioni perdenti: {n_simulazioni_perdenti} su {n_simulazioni} ({percentuale_perdenti:.1f}%)")

# Stampa delle statistiche sui trade
print("\nSTATISTICHE SUI TRADE")
print("=" * 90)
print(f"Trade totali: {totale_trade}")
print(f"Trade vincenti: {totale_win} ({win_rate_osservato:.1f}%)")
print(f"Trade perdenti: {totale_loss}")
print(f"Guadagno medio trade vincente: ${somma_win_totale / totale_win if totale_win else 0:,.2f}")
print(f"Perdita media trade perdente: ${abs(somma_loss_totale) / totale_loss if totale_loss else 0:,.2f}")
print(f"Expectancy media (profitto medio per trade): ${expectancy_media:,.2f}")
print(f"Profit Factor: {profit_factor_aggregato:.2f}")

# Visualizzazione grafica
plt.figure(figsize=(18, 12))

# 1. Andamento dei capitali (20 simulazioni campione)
plt.subplot(2, 2, 1)
for res in risultati[:20]:
    plt.plot(res['storico_saldo'], alpha=0.4)
plt.title('Andamento del Capitale (20 simulazioni campione)')
plt.xlabel('Trade')
plt.ylabel('Capitale ($)')
plt.grid(True)

# 2. Distribuzione dei saldi finali
plt.subplot(2, 2, 2)
plt.hist([r['capitale_finale'] for r in risultati], bins=50, color='skyblue', edgecolor='black')
plt.title('Distribuzione dei Capitali Finali')
plt.xlabel('Capitale Finale ($)')
plt.ylabel('Frequenza')
plt.grid(True)

# 3. Relazione lunghezza streak - contratti medi
plt.subplot(2, 2, 3)
lengths = []
contratti_medi = []
for length in sorted_lengths:
    if streak_stats[length]['count'] > 10:  # Filtra dati significativi
        lengths.append(length)
        contratti_medi.append(streak_stats[length]['contratti_avg'])
plt.plot(lengths, contratti_medi, 'bo-')
plt.title('Relazione Lunghezza Streak - Contratti Medi Necessari')
plt.xlabel('Lunghezza Losing Streak')
plt.ylabel('Contratti Medi Necessari')
plt.grid(True)
plt.yscale('log')

# 4. Distribuzione delle losing streaks
plt.subplot(2, 2, 4)
plt.bar([str(k) for k in sorted_lengths if streak_stats[k]['count'] > 0],
        [streak_stats[k]['count'] for k in sorted_lengths if streak_stats[k]['count'] > 0],
        color='salmon')
plt.title('Distribuzione delle Losing Streaks')
plt.xlabel('Lunghezza Streak')
plt.ylabel('Occorrenze Totali')
plt.xticks(rotation=45)
plt.grid(True)

plt.tight_layout()
plt.show()
