import pygame
import random
import json
import time
import math  # Ajouté pour faire bouger le boss de gauche à droite de façon fluide

# --- INITIALISATION ---
pygame.init()
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Eco Adventures")
clock = pygame.time.Clock()

# --- COULEURS ---
WHITE = (255, 255, 255)
GREEN = (50, 200, 50)
RED = (200, 50, 50)
GRAY = (150, 150, 150)
BLUE = (50, 150, 255)
GOLD = (255, 215, 0)  # Couleur pour la Victoire
BLACK = (0, 0, 0)


# --- FONCTIONS DE DESSIN DE SPRITES ---
def create_player_sprite():
    surface = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.circle(surface, GREEN, (15, 15), 15)
    pygame.draw.circle(surface, BLACK, (10, 10), 3)
    pygame.draw.circle(surface, BLACK, (20, 10), 3)
    pygame.draw.arc(surface, BLACK, (10, 15, 10, 10), 3.14, 0, 2)
    return surface


def create_trash_sprite():
    surface = pygame.Surface((20, 20), pygame.SRCALPHA)
    pygame.draw.polygon(surface, RED, [(10, 0), (20, 10), (10, 20), (0, 10)])
    pygame.draw.rect(surface, WHITE, (5, 5, 10, 10), 2)
    pygame.draw.circle(surface, BLACK, (10, 10), 1)
    return surface


def create_boss_sprite():
    surface = pygame.Surface((80, 80), pygame.SRCALPHA)
    pygame.draw.circle(surface, BLUE, (40, 40), 40)  # Tête du boss
    # Yeux fâchés
    pygame.draw.polygon(surface, BLACK, [(20, 20), (35, 30), (20, 30)])
    pygame.draw.polygon(surface, BLACK, [(60, 20), (45, 30), (60, 30)])
    # Bouche
    pygame.draw.rect(surface, BLACK, (30, 50, 20, 10))
    return surface


# --- CLASSES ---
class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2, HEIGHT // 2, 30, 30)
        self.sprite = create_player_sprite()
        self.velocity_y = 0
        self.gravity = 0.5
        self.jump_force = -13
        self.hp = 3
        self.max_hp = 3
        self.score = 0
        self.second_chance_used = False  # NOUVEAU : Mémoire de la seconde chance

    def jump(self):
        self.velocity_y = self.jump_force

    def update(self):
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y


class Platform:
    def __init__(self):
        self.rect = pygame.Rect(random.randint(0, WIDTH - 80), -10, random.randint(60, 100), 15)
        self.is_eco = random.choice([True, False, False])
        self.visited = False  # NOUVEAU : Pour ne donner les 75 points qu'une seule fois par plateforme


class Trash:
    def __init__(self, start_x=None, start_y=-50):
        # NOUVEAU : On peut forcer le déchet à apparaître à un endroit précis (pour le Boss)
        x_pos = start_x if start_x is not None else random.randint(0, WIDTH - 20)
        self.rect = pygame.Rect(x_pos, start_y, 20, 20)
        self.sprite = create_trash_sprite()
        self.speed = random.randint(3, 6)

    def update(self):
        self.rect.y += self.speed


# --- VARIABLES GLOBALES & ÉTATS ---
player = Player()
platforms = [Platform()]
platforms[0].rect.y = HEIGHT - 50
trashes = []
state = "PLAYING"
font = pygame.font.SysFont(None, 24)
title_font = pygame.font.SysFont(None, 48)

boss_sprite = create_boss_sprite()
countdown_start = 0

trivia_q = "Quel dechet met le plus de temps a se decomposer ?"
trivia_options = ["A) Trognon de pomme", "B) Bouteille plastique", "C) Journal"]
trivia_answer = pygame.K_b


# --- FONCTIONS DE SAUVEGARDE ---
def save_game():
    data = {"score": player.score, "hp": player.hp, "max_hp": player.max_hp}
    try:
        with open("savegame.json", "w") as f:
            json.dump(data, f)
    except Exception:
        pass

    # --- BOUCLE PRINCIPALE ---


running = True

while running:
    screen.fill(WHITE)
    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            save_game()
            running = False

    if state == "PLAYING":
        # CONTRÔLES
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_q]: player.rect.x -= 5
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: player.rect.x += 5
        if keys[pygame.K_ESCAPE]:
            save_game()
            running = False

        if player.rect.right < 0:
            player.rect.left = WIDTH
        elif player.rect.left > WIDTH:
            player.rect.right = 0

        player.update()

        # Le score n'est plus calculé ici, seule la caméra bouge
        if player.rect.y < HEIGHT // 2:
            offset = (HEIGHT // 2) - player.rect.y
            player.rect.y = HEIGHT // 2

            for p in platforms: p.rect.y += offset
            for t in trashes: t.rect.y += offset

        while len(platforms) < 8:
            highest_y = min([p.rect.y for p in platforms])
            new_p = Platform()
            new_p.rect.y = highest_y - random.randint(60, 100)
            platforms.append(new_p)

        # --- GESTION DU BOSS ET DES DÉCHETS ---
        if player.score >= 10000:
            state = "VICTORY"  # On a atteint le but final !

        elif player.score >= 5000:
            # PHASE BOSS : Le boss bouge et tire 2x plus
            # math.sin permet de faire un mouvement fluide de gauche à droite
            boss_x = WIDTH // 2 - 40 + int(math.sin(time.time() * 3) * 100)
            screen.blit(boss_sprite, (boss_x, 20))

            # 6% de chance d'apparaître (2x plus qu'avant)
            if random.randint(1, 100) < 6:
                trashes.append(Trash(start_x=boss_x + 30, start_y=80))  # Tire depuis le boss
        else:
            # PHASE NORMALE
            if random.randint(1, 100) < 3:
                trashes.append(Trash())  # Apparaît aléatoirement en haut

        # --- GESTION DU SCORE ET COLLISION PLATEFORMES ---
        for p in platforms:
            if player.velocity_y > 0 and player.rect.colliderect(p.rect) and player.rect.bottom <= p.rect.bottom:
                player.jump()
                # NOUVEAU : Si on n'avait jamais touché cette plateforme, on gagne 75 pts
                if not p.visited:
                    player.score += 75
                    p.visited = True
                    if p.is_eco:
                        player.score += 50

                        # --- GESTION DES DÉGÂTS ET DE LA MORT ---
        for t in trashes[:]:
            t.update()
            if player.rect.colliderect(t.rect):
                player.hp -= 1
                trashes.remove(t)
                if player.hp <= 0:
                    # NOUVEAU : Vérification de la Seconde Chance
                    if not player.second_chance_used:
                        state = "TRIVIA"
                    else:
                        state = "GAME_OVER"

        # Mort par chute
        if player.rect.top > HEIGHT:
            if not player.second_chance_used:
                state = "TRIVIA"
            else:
                state = "GAME_OVER"

        # Nettoyage de la mémoire
        platforms = [p for p in platforms if p.rect.y < HEIGHT]
        trashes = [t for t in trashes if t.rect.y < HEIGHT]

        # DESSINER :
        screen.blit(player.sprite, player.rect)
        for p in platforms:
            color = GREEN if p.is_eco else GRAY
            pygame.draw.rect(screen, color, p.rect)
        for t in trashes:
            screen.blit(t.sprite, t.rect)

        score_txt = font.render(f"Score: {player.score} | HP: {player.hp}", True, BLACK)
        screen.blit(score_txt, (10, 10))

    # ==========================================
    # ÉTAT : SECONDE CHANCE
    # ==========================================
    elif state == "TRIVIA":
        q_txt = title_font.render("Seconde Chance !", True, GREEN)
        screen.blit(q_txt, (WIDTH // 2 - q_txt.get_width() // 2, 100))

        screen.blit(font.render(trivia_q, True, BLACK), (20, 200))
        for i, opt in enumerate(trivia_options):
            screen.blit(font.render(opt, True, BLACK), (50, 250 + i * 40))

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == trivia_answer:
                    player.hp = player.max_hp
                    player.velocity_y = -15
                    player.rect.y = HEIGHT // 2
                    player.second_chance_used = True  # L'interrupteur passe sur ON (plus le droit à l'erreur)
                    state = "COUNTDOWN"
                    countdown_start = time.time()
                elif event.key in [pygame.K_a, pygame.K_b, pygame.K_c]:
                    state = "GAME_OVER"

    # ==========================================
    # ÉTAT : COMPTE À REBOURS
    # ==========================================
    elif state == "COUNTDOWN":
        remaining = 3 - int(time.time() - countdown_start)
        if remaining <= 0:
            state = "PLAYING"
        else:
            count_txt = title_font.render(f"Reprise dans {remaining}...", True, BLUE)
            screen.blit(count_txt, (WIDTH // 2 - count_txt.get_width() // 2, HEIGHT // 2))

    # ==========================================
    # ÉTAT : GAME OVER
    # ==========================================
    elif state == "GAME_OVER":
        over_txt = title_font.render("GAME OVER", True, RED)
        screen.blit(over_txt, (WIDTH // 2 - over_txt.get_width() // 2, HEIGHT // 2 - 50))

        restart_txt = font.render("Appuyez sur Entree pour rejouer", True, BLACK)
        screen.blit(restart_txt, (WIDTH // 2 - restart_txt.get_width() // 2, HEIGHT // 2 + 50))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            player = Player()
            platforms = [Platform()]
            platforms[0].rect.y = HEIGHT - 50
            trashes = []
            state = "PLAYING"

    # ==========================================
    # ÉTAT : VICTOIRE (NOUVEAU)
    # ==========================================
    elif state == "VICTORY":
        win_txt = title_font.render("VICTOIRE !", True, GOLD)
        screen.blit(win_txt, (WIDTH // 2 - win_txt.get_width() // 2, HEIGHT // 2 - 50))

        sub_txt = font.render("La planete est sauvee !", True, GREEN)
        screen.blit(sub_txt, (WIDTH // 2 - sub_txt.get_width() // 2, HEIGHT // 2))

        restart_txt = font.render("Appuyez sur Entree pour rejouer", True, BLACK)
        screen.blit(restart_txt, (WIDTH // 2 - restart_txt.get_width() // 2, HEIGHT // 2 + 80))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            player = Player()
            platforms = [Platform()]
            platforms[0].rect.y = HEIGHT - 50
            trashes = []
            state = "PLAYING"

    pygame.display.flip()
    clock.tick(60)

pygame.quit()