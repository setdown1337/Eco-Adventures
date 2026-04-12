"""
ECO ADVENTURES - Jeu éducatif sur l'écologie
Public visé : 5-8 ans
Équipe : Mohamed Aziz Zouaoui, Itoua Lebo Rohi Lebo Nathan,
         Christopher Barbour, Rayan Baderedinne
Module TI250 - EFREI Paris 2025-2026
"""

import pygame
import random
import math
import time

pygame.init()
pygame.mixer.init()

WIDTH,  HEIGHT = 500, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Eco Adventures")
clock = pygame.time.Clock()

# ─────────────────────────────────────────────
# COULEURS
# ─────────────────────────────────────────────
SKY_POLLUTED_TOP = (70,  70,  80)
SKY_POLLUTED_BOT = (110, 105, 100)
SKY_CLEAN_TOP    = (135, 206, 250)
SKY_CLEAN_BOT    = (200, 240, 255)

GRASS_GREEN  = (34,  139,  34)
LEAF_GREEN   = (50,  205,  50)
DARK_GREEN   = (0,   100,   0)
DIRT_BROWN   = (139,  69,  19)
GOLD         = (255, 215,   0)
RED          = (231,  76,  60)
WHITE        = (255, 255, 255)
BLACK        = (0,     0,   0)
BONUS_YELLOW = (255, 230,  50)
BONUS_GLOW   = (200, 255, 100)

OM_GREEN  = (80,  200,  50)
OM_DARK   = (40,  130,  20)
OM_LIGHT  = (160, 240, 100)

# ─────────────────────────────────────────────
# POLICES
# ─────────────────────────────────────────────
font_big   = pygame.font.SysFont("Arial", 30, bold=True)
font_med   = pygame.font.SysFont("Arial", 22, bold=True)
font_small = pygame.font.SysFont("Arial", 17, bold=True)
font_title = pygame.font.SysFont("Arial", 44, bold=True)

# ─────────────────────────────────────────────
# 10 QUESTIONS ECOLOGIQUES
# ─────────────────────────────────────────────
ALL_QUIZ = [
    {
        "question": "Quel déchet met le plus de\ntemps à se décomposer ?",
        "options":  ["A) Trognon de pomme", "B) Bouteille plastique", "C) Journal"],
        "answer":   pygame.K_b,
    },
    {
        "question": "Que signifie le symbole\ndes 3 flèches en cercle ?",
        "options":  ["A) Danger", "B) Recyclable", "C) Fragile"],
        "answer":   pygame.K_b,
    },
    {
        "question": "Quelle action économise\nle plus l'eau ?",
        "options":  ["A) Prendre un bain", "B) Laisser couler", "C) Prendre une douche"],
        "answer":   pygame.K_c,
    },
    {
        "question": "Combien d'années met\nune bouteille plastique\nà se décomposer ?",
        "options":  ["A) 10 ans", "B) 100 ans", "C) 450 ans"],
        "answer":   pygame.K_c,
    },
    {
        "question": "Quel gaz contribue\nle plus au réchauffement ?",
        "options":  ["A) L'oxygène", "B) Le CO2", "C) L'azote"],
        "answer":   pygame.K_b,
    },
    {
        "question": "Recycler du papier sauve\ncombien d'arbres par tonne ?",
        "options":  ["A) 3 arbres", "B) 17 arbres", "C) 50 arbres"],
        "answer":   pygame.K_b,
    },
    {
        "question": "Quel transport est\nle plus écologique ?",
        "options":  ["A) La voiture", "B) L'avion", "C) Le vélo"],
        "answer":   pygame.K_c,
    },
    {
        "question": "Quel animal est menacé\npar les sacs plastique ?",
        "options":  ["A) Le lion", "B) La tortue marine", "C) Le chien"],
        "answer":   pygame.K_b,
    },
    {
        "question": "Combien de fois peut-on\nrecycler le verre ?",
        "options":  ["A) 3 fois", "B) 10 fois", "C) A l'infini"],
        "answer":   pygame.K_c,
    },
    {
        "question": "Un arbre absorbe combien\nde CO2 par an ?",
        "options":  ["A) 2 kg", "B) 22 kg", "C) 200 kg"],
        "answer":   pygame.K_b,
    },
]

ECO_MESSAGES = [
    ("Le savais-tu ?",  "Une bouteille en plastique met\n450 ans a se decomposer !"),
    ("Le savais-tu ?",  "Recycler 1 tonne de papier\nsauve 17 arbres !"),
    ("Le savais-tu ?",  "1 robinet qui goutte gaspille\n40 litres d'eau par jour !"),
    ("Le savais-tu ?",  "Les tortues confondent\nles sacs plastique avec des meduses."),
    ("Le savais-tu ?",  "Un arbre absorbe environ\n22 kg de CO2 par an !"),
    ("Le savais-tu ?",  "Le velo reduit la pollution\nbien plus que la voiture !"),
    ("Le savais-tu ?",  "Le verre peut etre recycle\na l'infini sans perte de qualite !"),
]

# ─────────────────────────────────────────────
# ENVIRONNEMENT PROGRESSIF
# 0.0 = pollué (gris + pluie)   1.0 = propre (bleu + vert)
# ─────────────────────────────────────────────

def env_ratio(score):
    # Commence à changer vers 3000, propre total vers 16000 (après le boss)
    return min(1.0, max(0.0, (score - 3000) / 13000))

def lerp(a, b, t):
    return a + (b - a) * t

def lerp_color(c1, c2, t):
    return (int(lerp(c1[0], c2[0], t)),
            int(lerp(c1[1], c2[1], t)),
            int(lerp(c1[2], c2[2], t)))

def draw_sky(surface, ratio):
    top = lerp_color(SKY_POLLUTED_TOP, SKY_CLEAN_TOP, ratio)
    bot = lerp_color(SKY_POLLUTED_BOT, SKY_CLEAN_BOT, ratio)
    for y in range(HEIGHT):
        t = y / HEIGHT
        pygame.draw.line(surface, lerp_color(top, bot, t), (0, y), (WIDTH, y))

# Pluie
rain_drops = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(90)]

def draw_rain(surface, ratio):
    if ratio >= 1.0:
        return
    intensity = int(200 * (1 - ratio))
    for i, (rx, ry) in enumerate(rain_drops):
        rain_drops[i] = (rx, (ry + 14) % HEIGHT)
        pygame.draw.line(surface, (140, 170, 215), (rx, ry), (rx + 2, ry + 12), 1)

# Nuages de pollution
smoke_offsets = [random.randint(0, WIDTH) for _ in range(5)]
smoke_y       = [random.randint(30, 150) for _ in range(5)]

def draw_smog(surface, ratio):
    if ratio >= 0.85:
        return
    alpha = int(90 * (1 - ratio / 0.85))
    smog = pygame.Surface((WIDTH, HEIGHT // 3), pygame.SRCALPHA)
    for i in range(5):
        r = random.randint(55, 65)
        cx = (smoke_offsets[i] + int(time.time() * 15)) % (WIDTH + 80) - 40
        pygame.draw.ellipse(smog, (100, 100, 100, alpha),
                            (cx, smoke_y[i], 120, 45))
    surface.blit(smog, (0, 0))

# ─────────────────────────────────────────────
# DESSIN DES OBSTACLES (déchets)
# ─────────────────────────────────────────────

def draw_can(surface, x, y):
    """Canette renversée."""
    pygame.draw.rect(surface, (150, 150, 160), (x+4, y+4, 18, 22), border_radius=3)
    pygame.draw.rect(surface, (200, 200, 210), (x+6, y+6, 5, 16), border_radius=2)
    pygame.draw.ellipse(surface, (130, 130, 140), (x+4, y+2,  18, 6))
    pygame.draw.ellipse(surface, (110, 110, 120), (x+4, y+22, 18, 6))
    pygame.draw.line(surface, (110, 110, 120), (x+4, y+14), (x+22, y+14), 1)
    # étiquette rouge
    pygame.draw.rect(surface, (200, 50, 50), (x+6, y+8, 12, 8))
    pygame.draw.line(surface, WHITE, (x+8, y+10), (x+16, y+10), 1)
    pygame.draw.line(surface, WHITE, (x+8, y+13), (x+16, y+13), 1)

def draw_bottle(surface, x, y):
    """Bouteille plastique."""
    pygame.draw.rect(surface, (60, 100, 190), (x+9, y, 8, 5), border_radius=2)
    pygame.draw.rect(surface, (190, 220, 255), (x+4, y+5, 18, 23), border_radius=5)
    pygame.draw.rect(surface, (220, 240, 255), (x+6, y+7, 5, 17), border_radius=3)
    pygame.draw.rect(surface, (200, 40, 40), (x+8, y-2, 10, 4), border_radius=2)

def draw_bag(surface, x, y):
    """Sac poubelle noir bien visible."""
    # Corps principal noir brillant
    pygame.draw.ellipse(surface, (30, 30, 33),  (x,   y+10, 30, 22))
    # Reflet sur le sac
    pygame.draw.ellipse(surface, (65, 65, 70),  (x+4, y+12,  8, 10))
    # Nœud du haut
    pygame.draw.polygon(surface, (20, 20, 22),
        [(x+7, y+10), (x+15, y+2), (x+23, y+10)])
    pygame.draw.ellipse(surface, (50, 50, 55),  (x+9, y+1, 12, 11))
    # Contour léger pour le faire ressortir
    pygame.draw.ellipse(surface, (80, 80, 85),  (x, y+10, 30, 22), 2)

def draw_trash(surface, kind, rect):
    x, y = rect.x, rect.y
    if   kind == "can":    draw_can(surface, x, y)
    elif kind == "bottle": draw_bottle(surface, x, y)
    else:                  draw_bag(surface, x, y)

# ─────────────────────────────────────────────
# DESSIN BONUS (feuille)
# ─────────────────────────────────────────────

def draw_bonus(surface, rect, pulse):
    """Vraie feuille verte avec tige, nervures et brillance animée."""
    cx, cy = rect.centerx, rect.centery
    scale = 1.0 + 0.15 * pulse

    # Couleurs de la feuille
    leaf_color  = lerp_color((30, 160, 30), (80, 220, 60), pulse)
    vein_color  = lerp_color((10, 100, 10), (40, 160, 30), pulse)
    shine_color = lerp_color((120, 230, 80), (200, 255, 140), pulse)

    # Forme de la feuille en polygone pointu
    w = int(11 * scale)
    h = int(16 * scale)
    leaf_pts = [
        (cx,      cy - h),      # pointe haute
        (cx + w,  cy - h//3),   # droite haut
        (cx + w,  cy + h//3),   # droite bas
        (cx,      cy + h//2),   # base basse (légère)
        (cx - w,  cy + h//3),   # gauche bas
        (cx - w,  cy - h//3),   # gauche haut
    ]
    pygame.draw.polygon(surface, leaf_color, leaf_pts)

    # Nervure centrale
    pygame.draw.line(surface, vein_color, (cx, cy - h + 2), (cx, cy + h//2 - 2), 2)
    # Nervures latérales
    for dy in [-h//3, 0, h//4]:
        pygame.draw.line(surface, vein_color, (cx, cy + dy), (cx + w - 3, cy + dy - 4), 1)
        pygame.draw.line(surface, vein_color, (cx, cy + dy), (cx - w + 3, cy + dy - 4), 1)

    # Reflet brillant
    pygame.draw.ellipse(surface, shine_color,
                        (cx - w//2, cy - h + 3, w//2, h//4))

    # Tige
    pygame.draw.line(surface, vein_color,
                     (cx, cy + h//2), (cx, cy + h//2 + 7), 2)

# ─────────────────────────────────────────────
# DESSIN PLATEFORME
# ─────────────────────────────────────────────

def draw_platform(surface, rect, ratio):
    grass = lerp_color((90, 90, 90), GRASS_GREEN, ratio)
    dirt  = lerp_color((70, 65, 60), DIRT_BROWN,  ratio)
    pygame.draw.rect(surface, dirt, rect, border_radius=4)
    pygame.draw.rect(surface, grass, pygame.Rect(rect.x, rect.y, rect.width, 7), border_radius=4)
    if ratio > 0.25:
        leaf = lerp_color(grass, LEAF_GREEN, ratio)
        for i in range(0, rect.width, 18):
            pygame.draw.circle(surface, leaf, (rect.x + i + 5, rect.y + 2), 4)

# ─────────────────────────────────────────────
# SPRITE OM NOM (profil)
# ─────────────────────────────────────────────

def make_omnnom(facing_right=True):
    W, H = 52, 58
    s = pygame.Surface((W, H), pygame.SRCALPHA)

    LIME    = (96,  196,  34)
    LIME_HI = (152, 232,  72)
    LIME_SH = (50,  130,  16)
    OUTLINE = (22,   72,   6)

    # ── Corps principal ──
    pygame.draw.ellipse(s, OUTLINE, (0,  6, 40, 46))
    pygame.draw.ellipse(s, LIME,    (2,  8, 36, 42))
    pygame.draw.ellipse(s, LIME_HI, (18, 10, 14, 16))  # reflet
    pygame.draw.ellipse(s, LIME_SH, (2,  34,  36, 16)) # ombre

    # ── Bras gauche (petite boule) ──
    pygame.draw.circle(s, OUTLINE, (4, 38), 6)
    pygame.draw.circle(s, LIME,    (4, 38), 4)

    # ── 2 petites pattes ──
    pygame.draw.ellipse(s, OUTLINE, (5,  50, 14, 8))
    pygame.draw.ellipse(s, OUTLINE, (20, 51, 13, 7))
    pygame.draw.ellipse(s, LIME,    (6,  51, 12, 6))
    pygame.draw.ellipse(s, LIME,    (21, 52, 11, 5))

    # ── Blob blanc de l'oeil (organique, pas trop grand) ──
    eye_pts = [
        (4, 10), (10,  5), (22,  4), (30,  8),
        (32, 18), (30, 30), (22, 35), (10, 33),
        (4, 24), (2, 16),
    ]
    pygame.draw.polygon(s, OUTLINE, eye_pts)
    eye_in = [
        (6, 11), (11,  7), (21,  6), (28, 10),
        (30, 18), (28, 29), (21, 33), (11, 31),
        (6, 23), (4, 16),
    ]
    pygame.draw.polygon(s, WHITE, eye_in)
    # Reflet bleu-blanc bas du blob
    pygame.draw.ellipse(s, (195, 228, 255), (5, 24, 22, 8))

    # ── Pupille haute (petite) ──
    pygame.draw.circle(s, (8, 8, 14),     (17, 13), 5)
    pygame.draw.circle(s, BLACK,           (17, 13), 4)
    pygame.draw.circle(s, (75, 178, 225),  (15, 16), 2)  # reflet cyan

    # ── Pupille basse (légèrement plus grande) ──
    pygame.draw.circle(s, (8, 8, 14),     (18, 23), 6)
    pygame.draw.circle(s, BLACK,           (18, 23), 5)
    pygame.draw.circle(s, (75, 178, 225),  (16, 26), 2)  # reflet cyan

    # ── Bouche ouverte – forme organique (pas de rectangle) ──
    # Mâchoire sup : arc vert qui suit le corps
    pygame.draw.arc(s, OUTLINE, (14, 28, 38, 28), math.pi * 1.55, math.pi * 2.0, 3)
    # Mâchoire inf : arc vert arrondi
    pygame.draw.arc(s, OUTLINE, (14, 36, 36, 26), math.pi * 0.0,  math.pi * 0.5, 3)
    # Intérieur rouge (bouche)
    pygame.draw.ellipse(s, (160, 18, 18), (22, 32, 28, 22))
    # Langue rouge arrondie uniquement
    pygame.draw.ellipse(s, (225, 52, 52), (24, 38, 22, 12))
    pygame.draw.ellipse(s, (240, 80, 80), (26, 39, 14,  7))  # reflet

    if not facing_right:
        s = pygame.transform.flip(s, True, False)
    return s

# ─────────────────────────────────────────────
# UI HELPERS
# ─────────────────────────────────────────────

def draw_text_centered(surface, text, font, color, cx, y, line_h=28):
    for i, line in enumerate(text.split("\n")):
        surf = font.render(line, True, color)
        surface.blit(surf, (cx - surf.get_width() // 2, y + i * line_h))

def draw_panel(surface, rect, alpha=220, radius=12, border=(34,139,34)):
    s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(s, (255, 255, 255, alpha), s.get_rect(), border_radius=radius)
    pygame.draw.rect(s, (*border, 255), s.get_rect(), 3, border_radius=radius)
    surface.blit(s, (rect.x, rect.y))

def draw_overlay(surface, alpha=160):
    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, alpha))
    surface.blit(s, (0, 0))

def draw_button(surface, rect, text, font, bg, fg=WHITE, border=(0,80,0)):
    pygame.draw.rect(surface, bg, rect, border_radius=12)
    pygame.draw.rect(surface, border, rect, 3, border_radius=12)
    t = font.render(text, True, fg)
    surface.blit(t, (rect.centerx - t.get_width()//2,
                     rect.centery - t.get_height()//2))

def draw_heart(surface, x, y):
    pygame.draw.circle(surface, RED, (x+6,  y+6), 6)
    pygame.draw.circle(surface, RED, (x+14, y+6), 6)
    pygame.draw.polygon(surface, RED, [(x, y+8), (x+20, y+8), (x+10, y+20)])

# ─────────────────────────────────────────────
# MINI-BOSS
# ─────────────────────────────────────────────

boss_x   = float(WIDTH // 2)
boss_dir = 1   # direction de déplacement

def draw_boss(surface, x, y, t):
    """
    Mini-boss : gros monstre pollueur rouge/noir qui flotte en haut.
    t = time.time() pour l'animation de flottement.
    """
    float_y = int(y + math.sin(t * 2.5) * 6)   # flottement vertical

    # Corps principal – ellipse rouge foncé
    pygame.draw.ellipse(surface, (160, 20, 20),  (x-36, float_y,    72, 56))
    # Reflet sur le corps
    pygame.draw.ellipse(surface, (210, 60, 60),  (x-22, float_y+4,  28, 16))
    # Ombre bas
    pygame.draw.ellipse(surface, (90,   0,  0),  (x-36, float_y+38, 72, 20))

    # Cornes
    pygame.draw.polygon(surface, (100, 10, 10),
        [(x-28, float_y+4), (x-36, float_y-18), (x-18, float_y+2)])
    pygame.draw.polygon(surface, (100, 10, 10),
        [(x+28, float_y+4), (x+36, float_y-18), (x+18, float_y+2)])

    # Yeux jaunes menaçants
    pygame.draw.ellipse(surface, (255, 220, 0), (x-26, float_y+12, 20, 14))
    pygame.draw.ellipse(surface, (255, 220, 0), (x+ 6, float_y+12, 20, 14))
    # Pupilles verticales
    pygame.draw.ellipse(surface, BLACK, (x-19, float_y+13,  6, 12))
    pygame.draw.ellipse(surface, BLACK, (x+13, float_y+13,  6, 12))

    # Bouche méchante (sourcils froncés)
    pygame.draw.arc(surface, BLACK,
        (x-24, float_y+30, 48, 20), math.pi*1.1, math.pi*1.9, 4)
    # Petites dents
    for dx in [-14, -5, 4, 13]:
        pygame.draw.polygon(surface, WHITE,
            [(x+dx, float_y+38), (x+dx+6, float_y+38), (x+dx+3, float_y+44)])

    # Nuage de pollution autour
    smk_alpha = int(120 + 60 * math.sin(t * 3))
    for ox, oy, r in [(-45, 10, 14), (45, 8, 13), (-40, 26, 11), (42, 24, 12)]:
        smk = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.circle(smk, (80, 80, 80, smk_alpha), (r, r), r)
        surface.blit(smk, (x + ox - r, float_y + oy - r))

    # Label "BOSS" au-dessus
    lbl = pygame.font.SysFont("Arial", 14, bold=True).render("!! BOSS !!", True, (255, 80, 0))
    surface.blit(lbl, (x - lbl.get_width()//2, float_y - 28))



class Player:
    def __init__(self):
        self.rect = pygame.Rect(0, HEIGHT - 150, 52, 58)
        self.rect.centerx = WIDTH // 2
        self.vel_y = 0
        self.hp = 3
        self.score = 0
        self.facing_right = True
        self.second_chance_used = False
        self.img_r = make_omnnom(True)
        self.img_l = make_omnnom(False)

    def jump(self):   self.vel_y = -14
    def update(self):
        self.vel_y += 0.6
        self.rect.y += int(self.vel_y)
    def draw(self, surf):
        surf.blit(self.img_r if self.facing_right else self.img_l, self.rect)


class Platform:
    def __init__(self, y):
        w = random.randint(110, 145)
        self.rect    = pygame.Rect(random.randint(0, WIDTH - w), y, w, 15)
        self.visited = False


class Trash:
    def __init__(self):
        self.kind  = random.choice(["can", "bottle", "bag"])
        self.rect  = pygame.Rect(random.randint(0, WIDTH - 30), -50, 30, 30)
        self.speed = random.randint(2, 4)
    def update(self): self.rect.y += self.speed


class Bonus:
    POINTS = 200
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 12, y - 8, 24, 16)
        self._t   = random.uniform(0, 6.28)
    def update(self, dt, scroll):
        self._t += dt * 2.5
        self.rect.y += scroll
    @property
    def pulse(self): return (math.sin(self._t) + 1) / 2
    def draw(self, surf): draw_bonus(surf, self.rect, self.pulse)

# ─────────────────────────────────────────────
# INITIALISATION / RESET
# ─────────────────────────────────────────────

def reset_game():
    global player, platforms, trashes, bonuses, state
    global countdown_start, current_quiz, eco_message
    global boss_x, boss_dir

    boss_x   = float(WIDTH // 2)
    boss_dir = 1

    player = Player()

    fp = Platform(HEIGHT - 50)
    fp.rect.centerx = WIDTH // 2
    platforms = [fp] + [Platform(HEIGHT - 50 - i * 90) for i in range(1, 12)]
    trashes, bonuses = [], []
    state = "MENU"
    countdown_start = 0
    current_quiz = None
    eco_message = random.choice(ECO_MESSAGES)

def pick_quiz():
    global current_quiz
    current_quiz = random.choice(ALL_QUIZ)

# ─────────────────────────────────────────────
reset_game()
high_score = 0
dt = 0.016

# ─────────────────────────────────────────────
# BOUCLE PRINCIPALE
# ─────────────────────────────────────────────
running = True

while running:
    events = pygame.event.get()
    for e in events:
        if e.type == pygame.QUIT:
            running = False

    ratio = env_ratio(player.score)

    # --- Fond dynamique ---
    draw_sky(screen, ratio)
    draw_smog(screen, ratio)
    draw_rain(screen, ratio)

    # ══════════════════════════════════════════
    # MENU
    # ══════════════════════════════════════════
    if state == "MENU":
        # Titre avec ombre
        sh = font_title.render("Eco Adventures", True, (0, 60, 0))
        screen.blit(sh, (WIDTH//2 - sh.get_width()//2 + 2, 72))
        ti = font_title.render("Eco Adventures", True, LEAF_GREEN)
        screen.blit(ti, (WIDTH//2 - ti.get_width()//2, 70))

        # Emoji feuille
        em = pygame.font.SysFont("Segoe UI Emoji", 38).render("🌿", True, WHITE)
        screen.blit(em, (WIDTH//2 - em.get_width()//2, 118))

        sub = font_small.render("Grimpe le plus haut possible !", True, WHITE)
        screen.blit(sub, (WIDTH//2 - sub.get_width()//2, 158))

        # Panel instructions
        draw_panel(screen, pygame.Rect(30, 195, WIDTH-60, 210), alpha=215)
        draw_text_centered(screen, "Fleches / Q D  :  se deplacer",
                           font_small, BLACK, WIDTH//2, 212)
        draw_text_centered(screen, "Evite les dechets !",
                           font_small, BLACK, WIDTH//2, 242)
        draw_text_centered(screen, "Collecte les feuilles (+200 pts)",
                           font_small, BLACK, WIDTH//2, 270)
        draw_text_centered(screen, "3 vies disponibles",
                           font_small, BLACK, WIDTH//2, 298)
        draw_text_centered(screen, "Reponds bien et tu reviens !",
                           font_small, BLACK, WIDTH//2, 326)
        draw_text_centered(screen, "L'environnement s'ameliore en montant !",
                           font_small, DARK_GREEN, WIDTH//2, 358)

        btn_play = pygame.Rect(WIDTH//2-110, 440, 220, 55)
        draw_button(screen, btn_play, "  JOUER", font_big, LEAF_GREEN)

        btn_quit = pygame.Rect(WIDTH//2-90, 515, 180, 45)
        draw_button(screen, btn_quit, "  Quitter", font_med, (180,55,55), WHITE, (110,25,25))

        if high_score > 0:
            hs = font_small.render(f"Record : {high_score}", True, GOLD)
            screen.blit(hs, (WIDTH//2 - hs.get_width()//2, 590))

        mouse = pygame.mouse.get_pos()
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if btn_play.collidepoint(mouse): state = "PLAYING"
                if btn_quit.collidepoint(mouse): running = False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN: state = "PLAYING"
                if e.key == pygame.K_ESCAPE: running = False

    # ══════════════════════════════════════════
    # JEU
    # ══════════════════════════════════════════
    elif state == "PLAYING":
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]  or keys[pygame.K_q]:
            player.rect.x -= 7; player.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.rect.x += 7; player.facing_right = True
        player.rect.x %= WIDTH
        player.update()

        # Scrolling
        scroll = 0
        if player.rect.y < HEIGHT // 2:
            scroll = HEIGHT // 2 - player.rect.y
            player.rect.y = HEIGHT // 2
            for p in platforms: p.rect.y += scroll
            for t in trashes:   t.rect.y += scroll
            for b in bonuses:   b.rect.y += scroll
            player.score += scroll // 5

        # Génération plateformes
        while platforms[-1].rect.y > -100:
            ny = platforms[-1].rect.y - random.randint(80, 110)
            platforms.append(Platform(ny))
            if random.randint(1, 3) == 1:
                p = platforms[-1]
                bonuses.append(Bonus(p.rect.centerx + random.randint(-20,20), p.rect.y - 20))

        platforms = [p for p in platforms if p.rect.y < HEIGHT + 50]
        trashes   = [t for t in trashes   if t.rect.y < HEIGHT + 50]
        bonuses   = [b for b in bonuses   if b.rect.y < HEIGHT + 50]

        # Spawn déchets (réduit)
        if random.randint(1, 90) == 1:
            trashes.append(Trash())

        # Mini-boss actif entre 10000 et 12500 → double les déchets
        boss_active = 10000 <= player.score < 12500
        if boss_active and random.randint(1, 90) == 1:
            trashes.append(Trash())

        # Mise à jour déchets
        for t in trashes[:]:
            t.update()
            if player.rect.colliderect(t.rect):
                player.hp -= 1
                trashes.remove(t)
                if player.hp <= 0:
                    if not player.second_chance_used:
                        pick_quiz(); state = "TRIVIA"
                    else:
                        state = "GAME_OVER"

        # Mise à jour bonus
        for b in bonuses[:]:
            b.update(dt, 0)
            if player.rect.colliderect(b.rect):
                player.score += Bonus.POINTS
                bonuses.remove(b)

        # Collisions plateformes
        for p in platforms:
            if (player.vel_y > 0
                    and player.rect.colliderect(p.rect)
                    and player.rect.bottom < p.rect.bottom + 12):
                player.jump()
                if not p.visited:
                    player.score += 100
                    p.visited = True

        # Chute hors écran
        if player.rect.y > HEIGHT:
            if not player.second_chance_used:
                pick_quiz(); state = "TRIVIA"
            else:
                state = "GAME_OVER"

        # --- Dessin ---
        for p in platforms: draw_platform(screen, p.rect, ratio)
        for t in trashes:   draw_trash(screen, t.kind, t.rect)
        for b in bonuses:   b.draw(screen)
        player.draw(screen)

        # Mini-boss : apparait entre 10000 et 12500
        if boss_active:
            boss_x += boss_dir * 1.8
            if boss_x > WIDTH - 40: boss_dir = -1
            if boss_x < 40:         boss_dir =  1
            draw_boss(screen, int(boss_x), 60, time.time())

            # Alerte rouge clignotante
            if int(time.time() * 3) % 2 == 0:
                alert = font_med.render("ATTENTION ! Le boss envoie plus de dechets !", True, RED)
                screen.blit(alert, (WIDTH//2 - alert.get_width()//2, HEIGHT - 38))

        # HUD score
        sp = pygame.Surface((165, 38), pygame.SRCALPHA)
        pygame.draw.rect(sp, (0,0,0,110), sp.get_rect(), border_radius=8)
        screen.blit(sp, (8, 8))
        st = font_big.render(f"Score : {player.score}", True, WHITE)
        screen.blit(st, (16, 13))

        # Vies
        for i in range(player.hp):
            draw_heart(screen, WIDTH - 35 - i * 30, 15)

        # Barre environnement (haut centre)
        bw = 110
        bx = WIDTH//2 - bw//2
        pygame.draw.rect(screen, (70,70,70), (bx, 10, bw, 14), border_radius=7)
        fw = int(bw * ratio)
        if fw > 0:
            ec = lerp_color((140,140,140), LEAF_GREEN, ratio)
            pygame.draw.rect(screen, ec, (bx, 10, fw, 14), border_radius=7)
        pygame.draw.rect(screen, WHITE, (bx, 10, bw, 14), 2, border_radius=7)

    # ══════════════════════════════════════════
    # TRIVIA (seconde chance)
    # ══════════════════════════════════════════
    elif state == "TRIVIA":
        for p in platforms: draw_platform(screen, p.rect, ratio)
        player.draw(screen)
        draw_overlay(screen, 175)

        # En-tête
        draw_text_centered(screen, "SECONDE CHANCE !", font_big, GOLD, WIDTH//2, 75)
        draw_text_centered(screen,
            "Reponds correctement pour continuer !",
            font_small, WHITE, WIDTH//2, 115)

        # Panel question
        draw_panel(screen, pygame.Rect(18, 148, WIDTH-36, 195), alpha=235, border=GOLD)
        draw_text_centered(screen, current_quiz["question"],
                           font_med, DARK_GREEN, WIDTH//2, 168, 30)

        # Options colorées
        opt_colors  = [(55,110,200), (50,155,55), (190,75,55)]
        opt_borders = [(30, 70,150), (25,100,30), (130,40,30)]
        for i, opt in enumerate(current_quiz["options"]):
            r = pygame.Rect(35, 303 + i * 54, WIDTH-70, 44)
            pygame.draw.rect(screen, opt_colors[i], r, border_radius=9)
            pygame.draw.rect(screen, opt_borders[i], r, 2, border_radius=9)
            ot = font_med.render(opt, True, WHITE)
            screen.blit(ot, (r.x + 14, r.centery - ot.get_height()//2))

        hint = font_small.render("Appuie sur  A  B  ou  C", True, (210,210,210))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, 472))

        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == current_quiz["answer"]:
                    player.hp = 3
                    player.vel_y = 0
                    player.rect.centerx = WIDTH // 2
                    player.rect.y = HEIGHT // 2
                    safe = Platform(HEIGHT//2 + 60)
                    safe.rect.centerx = WIDTH // 2
                    platforms.append(safe)
                    player.second_chance_used = True
                    countdown_start = time.time()
                    state = "COUNTDOWN"
                elif e.key in (pygame.K_a, pygame.K_b, pygame.K_c):
                    state = "GAME_OVER"

    # ══════════════════════════════════════════
    # COUNTDOWN
    # ══════════════════════════════════════════
    elif state == "COUNTDOWN":
        for p in platforms: draw_platform(screen, p.rect, ratio)
        player.draw(screen)
        draw_overlay(screen, 100)

        remaining = 3 - int(time.time() - countdown_start)
        if remaining <= 0:
            state = "PLAYING"
            player.jump()
        else:
            circle_s = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(circle_s, (0,0,0,120), (60,60), 60)
            screen.blit(circle_s, (WIDTH//2-60, HEIGHT//2-60))
            fn = pygame.font.SysFont("Arial", 90, bold=True)
            nt = fn.render(str(remaining), True, GOLD)
            screen.blit(nt, (WIDTH//2 - nt.get_width()//2, HEIGHT//2 - 45))
            rt = font_med.render("Pret a repartir !", True, WHITE)
            screen.blit(rt, (WIDTH//2 - rt.get_width()//2, HEIGHT//2 + 58))

    # ══════════════════════════════════════════
    # GAME OVER
    # ══════════════════════════════════════════
    elif state == "GAME_OVER":
        if player.score > high_score:
            high_score = player.score

        draw_overlay(screen, 165)

        sh = font_title.render("Game Over !", True, (100,0,0))
        screen.blit(sh, (WIDTH//2 - sh.get_width()//2+2, 52))
        gt = font_title.render("Game Over !", True, RED)
        screen.blit(gt, (WIDTH//2 - gt.get_width()//2, 50))

        sf = font_big.render(f"Score : {player.score}", True, WHITE)
        screen.blit(sf, (WIDTH//2 - sf.get_width()//2, 112))
        ht = font_med.render(f"Record : {high_score}", True, GOLD)
        screen.blit(ht, (WIDTH//2 - ht.get_width()//2, 150))

        # Message éducatif
        draw_panel(screen, pygame.Rect(22, 200, WIDTH-44, 185), alpha=230)
        title_eco, msg_eco = eco_message
        te = font_med.render(title_eco, True, DARK_GREEN)
        screen.blit(te, (WIDTH//2 - te.get_width()//2, 218))
        draw_text_centered(screen, msg_eco, font_small, BLACK, WIDTH//2, 258, 26)

        btn2 = pygame.Rect(WIDTH//2-120, 415, 240, 55)
        draw_button(screen, btn2, "  Rejouer", font_big, LEAF_GREEN)

        btn3 = pygame.Rect(WIDTH//2-100, 490, 200, 45)
        draw_button(screen, btn3, "Menu principal", font_med, (65,110,195), WHITE, (35,65,140))

        btn4 = pygame.Rect(WIDTH//2-80, 553, 160, 42)
        draw_button(screen, btn4, "  Quitter", font_med, (180,55,55), WHITE, (110,25,25))

        mouse = pygame.mouse.get_pos()
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                saved = high_score
                if btn2.collidepoint(mouse):
                    reset_game(); high_score = saved; state = "PLAYING"
                if btn3.collidepoint(mouse):
                    reset_game(); high_score = saved; state = "MENU"
                if btn4.collidepoint(mouse):
                    running = False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    saved = high_score; reset_game(); high_score = saved; state = "PLAYING"
                if e.key == pygame.K_ESCAPE:
                    running = False

    # ─────────────────────────────────────────
    pygame.display.flip()
    dt = clock.tick(60) / 1000.0

pygame.quit()