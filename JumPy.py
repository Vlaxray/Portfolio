import pygame
import random
import math
import sys

# Costanti
LARGHEZZA = 800
ALTEZZA = 600
LARGHEZZA_MONDO = LARGHEZZA * 3
ALTEZZA_LIVELLO = ALTEZZA * 150
SPAZIO_VERTICALE = 120

# Colori
NERO = (0, 0, 0)
BIANCO = (255, 255, 255)
ROSSO = (255, 0, 0)
VERDE = (34, 139, 34)
VERDE_CHIARO = (50, 205, 50)
BLU = (0, 0, 255)
ARANCIONE = (255, 165, 0)
GRIGIO = (128, 128, 128)
GIALLO = (255, 255, 0)
ROSSO_CHIARO = (255, 150, 150)

# Fisica
GRAVITA = 0.7

class Giocatore:
    def __init__(self, x, y):
        self.width = 30
        self.height = 30
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.punto_contatto = pygame.math.Vector2(self.width // 2, self.height)
        self.velocita_x = 0
        self.velocita_y = 0
        self.max_velocita_x = 8
        self.accelerazione = 0.5
        self.decelerazione = 0.3
        self.forza_salto_min = -12
        self.forza_salto_max = -18
        self.tempo_salto = 0
        self.max_tempo_salto = 15
        self.sta_caricando_salto = False
        self.sta_saltando = False
        self.ha_paracadute = False
        self.usando_paracadute = False
        self.velocita_paracadute = 2
        self.no_clip = False
        self.target_y = ALTEZZA_LIVELLO - 100  # Posizione finale di atterraggio
        self.ha_mosso = False
        self.vittoria_animazione_iniziata = False
        self.tempo_vittoria = 0
        self.piattaforma_lancio = None
        self.fase_vittoria = 0  # 0: salita, 1: ricerca piattaforma, 2: paracadute
        self.velocita_salita = 8
    
    def update(self, gravita, tasti):
        if self.vittoria_animazione_iniziata:
            self.gestisci_animazione_vittoria()
        else:
            # Controlla il primo movimento
            if not self.ha_mosso and (tasti[pygame.K_LEFT] or tasti[pygame.K_RIGHT] or tasti[pygame.K_UP]):
                self.ha_mosso = True
            
            if self.usando_paracadute:
                # Movimento con paracadute
                self.velocita_x *= 0.95  # Rallentamento graduale
                self.velocita_y = self.velocita_paracadute
                
                # Verifica atterraggio
                if self.rect.y >= self.target_y:
                    self.rect.y = self.target_y
                    self.usando_paracadute = False
                    self.no_clip = False
                    self.velocita_y = 0
                    self.velocita_x = 0
            else:
                # Movimento normale
                if not self.no_clip:
                    # Movimento orizzontale con smoothing
                    target_velocita_x = 0
                    if tasti[pygame.K_LEFT]:
                        target_velocita_x = -self.max_velocita_x
                    if tasti[pygame.K_RIGHT]:
                        target_velocita_x = self.max_velocita_x
                    
                    # Applica accelerazione/decelerazione
                    if target_velocita_x != 0:
                        self.velocita_x += (target_velocita_x - self.velocita_x) * self.accelerazione
                    else:
                        self.velocita_x *= (1 - self.decelerazione)
                    
                    # Gestione del salto
                    if tasti[pygame.K_UP] and not self.sta_saltando:
                        if not self.sta_caricando_salto:
                            self.sta_caricando_salto = True
                            self.tempo_salto = 0
                        else:
                            self.tempo_salto = min(self.tempo_salto + 1, self.max_tempo_salto)
                    elif self.sta_caricando_salto:
                        forza = self.forza_salto_min + (
                            (self.forza_salto_max - self.forza_salto_min) * 
                            (self.tempo_salto / self.max_tempo_salto)
                        )
                        self.velocita_y = forza
                        self.sta_caricando_salto = False
                        self.sta_saltando = True
                    
                    # Applica movimento e gravità
                    self.rect.x += self.velocita_x
                    self.velocita_y += gravita
                    self.rect.y += self.velocita_y
                    
                    # Mantieni il giocatore dentro il mondo
                    if self.rect.left < 0:
                        self.rect.left = 0
                        self.velocita_x = 0
                    if self.rect.right > LARGHEZZA_MONDO:
                        self.rect.right = LARGHEZZA_MONDO
                        self.velocita_x = 0
    
    def attiva_modalita_vittoria(self):
        self.ha_paracadute = True
        self.velocita_y = -15  # Salto iniziale di vittoria
    
    def draw(self, surface, camera):
        pos_x = self.rect.x - camera.x
        pos_y = self.rect.y - camera.y
        
        # Corpo del giocatore
        pygame.draw.rect(surface, (139, 69, 19), 
                        (pos_x, pos_y, self.width, self.height))
        
        # Occhi
        occhio_sx = pygame.draw.circle(surface, BIANCO, 
                                     (pos_x + 8, pos_y + 10), 4)
        occhio_dx = pygame.draw.circle(surface, BIANCO, 
                                     (pos_x + 22, pos_y + 10), 4)
        # Pupille (seguono la direzione del movimento)
        offset_x = 1 if self.velocita_x > 0 else (-1 if self.velocita_x < 0 else 0)
        pygame.draw.circle(surface, NERO, (pos_x + 8 + offset_x, pos_y + 10), 2)
        pygame.draw.circle(surface, NERO, (pos_x + 22 + offset_x, pos_y + 10), 2)
        
        # Bocca (sorridente durante il paracadute)
        if self.usando_paracadute:
            pygame.draw.arc(surface, NERO, 
                          (pos_x + 7, pos_y + 12, 16, 10), 0, math.pi, 2)
        else:
            pygame.draw.arc(surface, NERO, 
                          (pos_x + 7, pos_y + 15, 16, 10), 0, math.pi, 2)
        
        # Paracadute
        if self.usando_paracadute:
            # Cupola del paracadute
            pygame.draw.arc(surface, ROSSO,
                          (pos_x - 15, pos_y - 30, 60, 40), 0, math.pi, 3)
            # Corde del paracadute
            pygame.draw.line(surface, ROSSO, (pos_x, pos_y),
                           (pos_x - 15, pos_y - 25), 2)
            pygame.draw.line(surface, ROSSO, (pos_x + self.width, pos_y),
                           (pos_x + 45, pos_y - 25), 2)

    def trova_piattaforma_piu_alta(self, piattaforme):
        piattaforma_piu_alta = None
        y_min = float('inf')
        
        for piatt in piattaforme:
            if piatt.tipo != "fragile" and piatt.rect.y < y_min:
                y_min = piatt.rect.y
                piattaforma_piu_alta = piatt
        
        return piattaforma_piu_alta
    
    def gestisci_animazione_vittoria(self, piattaforme):
        if self.fase_vittoria == 0:  # Fase di salita veloce
            self.velocita_y = -self.velocita_salita
            self.velocita_x = 0
            
            # Trova la piattaforma più alta se non l'abbiamo ancora fatto
            if not self.piattaforma_lancio:
                self.piattaforma_lancio = self.trova_piattaforma_piu_alta(piattaforme)
            
            # Quando raggiungiamo l'altezza della piattaforma più alta
            if self.rect.y <= self.piattaforma_lancio.rect.y:
                self.fase_vittoria = 1
                self.velocita_y = 0
        
        elif self.fase_vittoria == 1:  # Fase di posizionamento sulla piattaforma
            target_x = self.piattaforma_lancio.rect.centerx - self.width/2
            
            # Muovi verso il centro della piattaforma
            if abs(self.rect.x - target_x) > 2:
                if self.rect.x < target_x:
                    self.velocita_x = 5
                else:
                    self.velocita_x = -5
            else:
                self.rect.x = target_x
                self.velocita_x = 0
                self.fase_vittoria = 2
                self.tempo_vittoria = pygame.time.get_ticks()
        
        elif self.fase_vittoria == 2:  # Fase di attesa e lancio
            tempo_trascorso = pygame.time.get_ticks() - self.tempo_vittoria
            
            if tempo_trascorso > 500:  # Aspetta mezzo secondo prima del lancio
                self.usando_paracadute = True
                self.no_clip = True
                self.velocita_y = self.velocita_paracadute
    
    def inizia_animazione_vittoria(self):
        if not self.vittoria_animazione_iniziata:
            self.vittoria_animazione_iniziata = True
            self.fase_vittoria = 0
            self.piattaforma_lancio = None
            self.no_clip = True  # Attiva no-clip durante tutta l'animazione

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.smooth_speed = 0.1
    
    def update(self, giocatore):
        # Segue il giocatore orizzontalmente
        target_x = giocatore.rect.x - LARGHEZZA/2
        self.x += (target_x - self.x) * self.smooth_speed
        
        # Segue il giocatore verticalmente
        target_y = giocatore.rect.y - ALTEZZA/2
        self.y += (target_y - self.y) * self.smooth_speed
        
        # Limiti della camera
        self.x = max(0, min(self.x, LARGHEZZA_MONDO - LARGHEZZA))
        self.y = max(0, min(self.y, ALTEZZA_LIVELLO - ALTEZZA))

class PiattaformaNormale:
    def __init__(self, x, y, larghezza):
        self.rect = pygame.Rect(x, y, larghezza, 20)
        self.tipo = "normale"
        self.colore = BLU

    def update(self, dt):
        pass

    def draw(self, surface, camera):
        piatt_visibile = pygame.Rect(
            self.rect.x - camera.x,
            self.rect.y - camera.y,
            self.rect.width,
            self.rect.height
        )
        pygame.draw.rect(surface, self.colore, piatt_visibile)

class PiattaformaRimbalzante(PiattaformaNormale):
    def __init__(self, x, y, larghezza):
        super().__init__(x, y, larghezza)
        self.tipo = "rimbalzante"
        self.moltiplicatore_rimbalzo = 1.5
        self.attiva = True
        self.tempo_disintegrazione = 0
        self.tempo_riattivazione = 1000
        self.colore = GIALLO
    
    def update(self, dt):
        if not self.attiva:
            tempo_corrente = pygame.time.get_ticks()
            if tempo_corrente - self.tempo_disintegrazione > self.tempo_riattivazione:
                self.attiva = True

class PiattaformaMobile(PiattaformaNormale):
    def __init__(self, x, y, larghezza):
        super().__init__(x, y, larghezza)
        self.tipo = "mobile"
        self.velocita = 2
        self.direzione = 1
        self.distanza_percorsa = 0
        self.max_distanza = 100
        self.colore = ARANCIONE
    
    def update(self, dt):
        self.rect.x += self.velocita * self.direzione
        self.distanza_percorsa += abs(self.velocita)
        if self.distanza_percorsa >= self.max_distanza:
            self.direzione *= -1
            self.distanza_percorsa = 0

class PiattaformaFragile(PiattaformaNormale):
    def __init__(self, x, y, larghezza):
        super().__init__(x, y, larghezza)
        self.tipo = "fragile"
        self.tempo_contatto = 0
        self.tempo_massimo = 30  # Ridotto per una risposta più rapida
        self.rotta = False
        self.colore = ROSSO_CHIARO
    
    def update(self, dt):
        if self.tempo_contatto > 0 and not self.rotta:
            self.tempo_contatto += 1
            if self.tempo_contatto >= self.tempo_massimo:
                self.rotta = True
    
    def draw(self, surface, camera):
        if not self.rotta:
            piatt_visibile = pygame.Rect(
                self.rect.x - camera.x,
                self.rect.y - camera.y,
                self.rect.width,
                self.rect.height
            )
            # Cambia colore gradualmente mentre si rompe
            if self.tempo_contatto > 0:
                percentuale = self.tempo_contatto / self.tempo_massimo
                colore = (
                    int(ROSSO_CHIARO[0] + (ROSSO[0] - ROSSO_CHIARO[0]) * percentuale),
                    int(ROSSO_CHIARO[1] + (ROSSO[1] - ROSSO_CHIARO[1]) * percentuale),
                    int(ROSSO_CHIARO[2] + (ROSSO[2] - ROSSO_CHIARO[2]) * percentuale)
                )
            else:
                colore = self.colore
            pygame.draw.rect(surface, colore, piatt_visibile)

class Terreno(PiattaformaNormale):
    def __init__(self):
        super().__init__(0, ALTEZZA_LIVELLO - 40, LARGHEZZA)
        self.tipo = "terreno"
        self.colore = VERDE
    
    def draw(self, surface, camera):
        piatt_visibile = pygame.Rect(
            self.rect.x - camera.x,
            self.rect.y - camera.y,
            self.rect.width,
            self.rect.height
        )
        pygame.draw.rect(surface, self.colore, piatt_visibile)
        # Striscia d'erba
        pygame.draw.rect(surface, VERDE_CHIARO, 
                        (piatt_visibile.x, piatt_visibile.y, 
                         piatt_visibile.width, 5))

class Monetina:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 15, 15)
        self.raccolto = False
        self.angolo = 0
        
    def update(self):
        self.angolo += 5
        if self.angolo >= 360:
            self.angolo = 0
    
    def draw(self, surface, camera):
        if not self.raccolto:
            pos_x = self.rect.x - camera.x
            pos_y = self.rect.y - camera.y
            larghezza = abs(math.cos(math.radians(self.angolo)) * 15)
            if larghezza < 3:
                larghezza = 3
            pygame.draw.ellipse(surface, (255, 215, 0),  # Colore oro
                              (pos_x + (15-larghezza)/2, pos_y, larghezza, 15))

class ContatoreMonetin:
    def __init__(self, totale_monetine=40):
        self.monetine_raccolte = 0
        self.totale_monetine = totale_monetine
        self.font = pygame.font.Font(None, 36)
        self.necessarie = 2
        self.livello_completato = False
        
    def aggiungi_monetina(self):
        self.monetine_raccolte += 1
        if self.monetine_raccolte >= self.necessarie and not self.livello_completato:
            self.livello_completato = True
            return True
        return False
    
    def draw(self, surface):
        testo = f'Monetine: {self.monetine_raccolte}/{self.totale_monetine}'
        render = self.font.render(testo, True, (255, 215, 0))
        padding = 5
        sfondo = pygame.Surface((render.get_width() + padding*2, 
                               render.get_height() + padding*2))
        sfondo.fill((0, 0, 0))
        sfondo.set_alpha(128)
        surface.blit(sfondo, (8, 8))
        surface.blit(render, (10, 10))
        
        if self.livello_completato:
            testo_vittoria = 'Livello Completato!'
            render_vittoria = self.font.render(testo_vittoria, True, (0, 255, 0))
            pos_x = (LARGHEZZA - render_vittoria.get_width()) // 2
            pos_y = (ALTEZZA - render_vittoria.get_height()) // 2
            sfondo_vittoria = pygame.Surface((render_vittoria.get_width() + 20, 
                                            render_vittoria.get_height() + 20))
            sfondo_vittoria.fill((0, 0, 0))
            sfondo_vittoria.set_alpha(200)
            surface.blit(sfondo_vittoria, (pos_x - 10, pos_y - 10))
            surface.blit(render_vittoria, (pos_x, pos_y))

class Timer:
    def __init__(self):
        self.tempo_iniziale = None
        self.tempo_pausa = 0
        self.in_pausa = False
        self.font = pygame.font.Font(None, 36)
        self.avviato = False
        
    def avvia(self):
        if not self.avviato:
            self.tempo_iniziale = pygame.time.get_ticks()
            self.avviato = True
    
    def get_tempo(self):
        if not self.avviato:
            return 0
        if self.in_pausa:
            return self.tempo_pausa
        tempo_attuale = pygame.time.get_ticks()
        return tempo_attuale - self.tempo_iniziale
    
    def pausa(self):
        if not self.in_pausa and self.avviato:
            self.tempo_pausa = self.get_tempo()
            self.in_pausa = True
    
    def formatta_tempo(self, millisecondi):
        secondi = int(millisecondi / 1000)
        minuti = int(secondi / 60)
        secondi = secondi % 60
        centesimi = int((millisecondi % 1000) / 10)
        return f"{minuti:02d}:{secondi:02d}.{centesimi:02d}"
    
    def draw(self, surface):
        tempo = self.get_tempo()
        testo = f"Tempo: {self.formatta_tempo(tempo)}"
        render = self.font.render(testo, True, (255, 255, 255))
        
        # Sfondo semi-trasparente
        padding = 5
        sfondo = pygame.Surface((render.get_width() + padding*2, 
                               render.get_height() + padding*2))
        sfondo.fill((0, 0, 0))
        sfondo.set_alpha(128)
        
        # Posiziona il timer in alto a destra
        pos_x = LARGHEZZA - render.get_width() - padding*2 - 10
        pos_y = 10
        
        surface.blit(sfondo, (pos_x, pos_y))
        surface.blit(render, (pos_x + padding, pos_y + padding))
        
        # Se il livello è completato, mostra il tempo finale
        if contatore.livello_completato:
            testo_finale = f"Tempo Finale: {self.formatta_tempo(self.get_tempo())}"
            render_finale = self.font.render(testo_finale, True, (255, 215, 0))
            pos_x = (LARGHEZZA - render_finale.get_width()) // 2
            pos_y = ALTEZZA // 2 + 40  # Sotto il messaggio di completamento
            
            sfondo_finale = pygame.Surface((render_finale.get_width() + padding*2,
                                          render_finale.get_height() + padding*2))
            sfondo_finale.fill((0, 0, 0))
            sfondo_finale.set_alpha(200)
            
            surface.blit(sfondo_finale, (pos_x - padding, pos_y - padding))
            surface.blit(render_finale, (pos_x, pos_y))

def genera_monetine(piattaforme, num_monetine=20):
    monetine = []
    piattaforme_disponibili = [p for p in piattaforme 
                             if p.tipo == "normale" or p.tipo == "mobile"]
    
    if len(piattaforme_disponibili) >= num_monetine:
        piattaforme_scelte = random.sample(piattaforme_disponibili, num_monetine)
        for piatt in piattaforme_scelte:
            x = piatt.rect.centerx - 7
            y = piatt.rect.top - 30
            monetine.append(Monetina(x, y))
    else:
        for piatt in piattaforme_disponibili:
            x = piatt.rect.centerx - 7
            y = piatt.rect.top - 30
            monetine.append(Monetina(x, y))
    return monetine

def genera_livello(seed):
    random.seed(seed)
    piattaforme = []
    
    # Terreno base con buco
    larghezza_buco = 200
    posizione_buco = LARGHEZZA_MONDO // 2 - larghezza_buco // 2
    
    # Crea due parti del terreno lasciando il buco al centro
    terreno_sx = PiattaformaNormale(0, ALTEZZA_LIVELLO - 40, posizione_buco)
    terreno_dx = PiattaformaNormale(posizione_buco + larghezza_buco, 
                                   ALTEZZA_LIVELLO - 40, 
                                   LARGHEZZA_MONDO - (posizione_buco + larghezza_buco))
    terreno_sx.colore = VERDE
    terreno_dx.colore = VERDE
    piattaforme.append(terreno_sx)
    piattaforme.append(terreno_dx)
    
    # Genera livelli verso l'alto
    ultima_y_su = ALTEZZA_LIVELLO - 150
    for livello in range(int(ALTEZZA_LIVELLO/(SPAZIO_VERTICALE*2))):
        y_base = ultima_y_su - SPAZIO_VERTICALE
        ultima_y_su = y_base
        
        num_piattaforme = random.randint(2, 3)
        larghezza_sezione = LARGHEZZA_MONDO / num_piattaforme
        
        for i in range(num_piattaforme):
            x_base = i * larghezza_sezione
            larghezza = random.randint(70, int(larghezza_sezione * 0.8))
            x = x_base + random.randint(0, int(larghezza_sezione - larghezza))
            y = y_base + random.randint(-30, 30)
            
            tipo = random.random()
            if tipo < 0.7:
                piattaforme.append(PiattaformaNormale(x, y, larghezza))
            elif tipo < 0.8:
                piattaforme.append(PiattaformaRimbalzante(x, y, larghezza))
            elif tipo < 0.9:
                piattaforme.append(PiattaformaMobile(x, y, larghezza))
            else:
                piattaforme.append(PiattaformaFragile(x, y, larghezza))
    
    # Genera livelli verso il basso
    ultima_y_giu = ALTEZZA_LIVELLO - 40
    for livello in range(20):  # Numero di livelli sotto il terreno
        y_base = ultima_y_giu + SPAZIO_VERTICALE
        ultima_y_giu = y_base
        
        # Genera più piattaforme intorno al buco
        num_piattaforme = random.randint(3, 4)
        larghezza_sezione = LARGHEZZA_MONDO / num_piattaforme
        
        for i in range(num_piattaforme):
            x_base = i * larghezza_sezione
            larghezza = random.randint(70, int(larghezza_sezione * 0.8))
            x = x_base + random.randint(0, int(larghezza_sezione - larghezza))
            y = y_base + random.randint(-30, 30)
            
            # Sotto il terreno, più piattaforme normali per facilitare la risalita
            tipo = random.random()
            if tipo < 0.8:
                piattaforme.append(PiattaformaNormale(x, y, larghezza))
            elif tipo < 0.9:
                piattaforme.append(PiattaformaRimbalzante(x, y, larghezza))
            else:
                piattaforme.append(PiattaformaMobile(x, y, larghezza))
            # No piattaforme fragili sotto il terreno per non intrappolare il giocatore
    
    return piattaforme

# Inizializzazione Pygame
pygame.init()
schermo = pygame.display.set_mode((LARGHEZZA, ALTEZZA))
pygame.display.set_caption("Platform Game")
clock = pygame.time.Clock()

# Creazione oggetti di gioco
piattaforme = genera_livello(42)  # Usa un seed fisso per generazione consistente
giocatore = Giocatore(LARGHEZZA//2, ALTEZZA_LIVELLO - 100)
camera = Camera()
monetine = genera_monetine(piattaforme, 20)
contatore = ContatoreMonetin(20)
timer = Timer()

# Loop principale del gioco
while True:
    dt = clock.tick(60) / 1000.0  # Delta time in secondi
    
    # Gestione eventi
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    # Input e update
    tasti = pygame.key.get_pressed()
    giocatore.update(GRAVITA, tasti)
    
    # Update piattaforme e collisioni
    for piattaforma in piattaforme:
        if piattaforma.tipo == "mobile":
            piattaforma.update(dt)
        elif piattaforma.tipo == "fragile":
            piattaforma.update(dt)
        
        if not getattr(piattaforma, 'rotta', False):  # Controlla solo piattaforme non rotte
            collisione = giocatore.rect.colliderect(piattaforma.rect)
            if collisione and giocatore.velocita_y > 0:
                if piattaforma.tipo == "rimbalzante" and piattaforma.attiva:
                    giocatore.velocita_y = giocatore.forza_salto_max * piattaforma.moltiplicatore_rimbalzo
                    piattaforma.attiva = False
                    piattaforma.tempo_disintegrazione = pygame.time.get_ticks()
                else:
                    giocatore.rect.bottom = piattaforma.rect.top
                    giocatore.velocita_y = 0
                    giocatore.sta_saltando = False
                    if piattaforma.tipo == "fragile":
                        piattaforma.tempo_contatto += 1
    
    # Update monetine
    for monetina in monetine:
        if not monetina.raccolto:
            monetina.update()
            if monetina.rect.colliderect(giocatore.rect):
                monetina.raccolto = True
                if contatore.aggiungi_monetina():
                    pass  # Qui puoi aggiungere effetti per il completamento
    
    # Update camera
    camera.update(giocatore)
    
    # Disegno
    schermo.fill(NERO)
    
    # Disegna piattaforme
    for piattaforma in piattaforme:
        piattaforma.draw(schermo, camera)
    
    # Disegna monetine
    for monetina in monetine:
        monetina.draw(schermo, camera)
    
    # Disegna giocatore
    giocatore.draw(schermo, camera)
    
    # Disegna UI
    contatore.draw(schermo)
    timer.draw(schermo)
    
    # Gestione vittoria e paracadute
    if contatore.livello_completato:
        if not timer.in_pausa:
            timer.pausa()  # Ferma il timer
        if not giocatore.vittoria_animazione_iniziata:
            giocatore.inizia_animazione_vittoria()
        
        # Passa le piattaforme per trovare quella più alta
        if giocatore.vittoria_animazione_iniziata:
            giocatore.gestisci_animazione_vittoria(piattaforme)
    
    # Update della camera
    if giocatore.vittoria_animazione_iniziata:
        # Camera più fluida durante l'animazione di vittoria
        camera.smooth_speed = 0.05
    else:
        camera.smooth_speed = 0.1
    
    # Gestione collisioni solo se non in modalità no-clip e non in vittoria
    if not giocatore.no_clip and not giocatore.vittoria_animazione_iniziata:
        for piattaforma in piattaforme:
            if piattaforma.tipo == "mobile":
                piattaforma.update(dt)
            elif piattaforma.tipo == "fragile":
                piattaforma.update(dt)
            
            if not getattr(piattaforma, 'rotta', False):
                collisione = giocatore.rect.colliderect(piattaforma.rect)
                if collisione and giocatore.velocita_y > 0:
                    if piattaforma.tipo == "rimbalzante" and piattaforma.attiva:
                        giocatore.velocita_y = giocatore.forza_salto_max * piattaforma.moltiplicatore_rimbalzo
                        piattaforma.attiva = False
                        piattaforma.tempo_disintegrazione = pygame.time.get_ticks()
                    else:
                        giocatore.rect.bottom = piattaforma.rect.top
                        giocatore.velocita_y = 0
                        giocatore.sta_saltando = False
                        if piattaforma.tipo == "fragile":
                            piattaforma.tempo_contatto += 1
    
    pygame.display.flip()
