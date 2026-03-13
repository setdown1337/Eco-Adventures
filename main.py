import pygame
import random
import json
import time
import os
import math

# --- INITIALISATION DE PYGAME ---
pygame.init()
# --- MODIFICATION ICI : Fenêtre de jeu augmentée (500x750) ---
WIDTH, HEIGHT = 500, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Eco Adventures - Version Finale")
clock = pygame.time.Clock()

# --- COULEURS ---
WHITE = (255, 255, 255)
GREEN = (50, 200, 50)
RED = (200, 50, 50)
GRAY = (150, 150, 150)
BLUE = (50, 150, 255)
GOLD = (255, 215, 0)
BLACK = (0, 0, 0)


# --- FONCTIONS DE DESSIN ET ASSETS ---
def create_bag_fallback():
    # Sécurité ultime : dessine un sac plastique si l'image manque
    surface = pygame.Surface((30, 30), pygame.SRCALPHA)
    # Fond blanc/gris du sac
    pygame.draw.polygon(surface, (240, 240, 240), [(6, 12), (24, 12), (28, 28), (2, 28)])
    # Contours noirs pour bien le voir sur le ciel
    pygame.draw.polygon(surface, BLACK, [(6, 12), (24, 12), (28, 28), (2, 28)], 2)
    pygame.draw.arc(surface, BLACK, (2, 2, 12, 15), 0, 3.14, 2)
    pygame.draw.arc(surface, BLACK, (16, 2, 12, 15), 0, 3.14, 2)
    return surface


def load_image(name):
    fullname = os.path.join("assets", name)
    try:
        image = pygame.image.load(fullname)
        image = image.convert_alpha()
        image = pygame.transform.scale(image, (30, 30))
        return image
    except (pygame.error, FileNotFoundError):
        return create_bag_fallback()


# Charge l'image, ou utilise le dessin de secours
TRASH_IMG = load_image("sac.jpg")


def create_player_sprite():
    # Dessin du petit bonhomme
    surface = pygame.Surface((30, 40), pygame.SRCALPHA)
    pygame.draw.circle(surface, BLACK, (15, 8), 7)  # Tête
    pygame.draw.line(surface, BLACK, (15, 15), (15, 28), 4)  # Corps
    pygame.draw.line(surface, BLACK, (5, 20), (25, 20), 3)  # Bras
    pygame.draw.line(surface, BLACK, (15, 28), (8, 38), 3)  # Jambe G
    pygame.draw.line(surface, BLACK, (15, 28), (22, 38), 3)  # Jambe D
    return surface


def draw_heart(screen, x, y):
    # Dessin d'un vrai coeur
    pygame.draw.circle(screen, RED, (x + 6, y + 6), 6)
    pygame.draw.circle(screen, RED, (x + 14, y + 6), 6)
    pygame.draw.polygon(screen, RED, [(x, y + 8), (x + 20, y + 8), (x + 10, y + 20)])
    pygame.draw.circle(screen, BLACK, (x + 6, y + 6), 6, 1)
    pygame.draw.circle(screen, BLACK, (x + 14, y + 6), 6, 1)
    pygame.draw.polygon(screen, BLACK, [(x, y + 8), (x + 20, y + 8), (x + 10, y + 20)], 1)


def draw_gradient_background(screen):
    for y in range(HEIGHT):
        # Correction de l'erreur de couleur : on bloque le maximum à 255
        color = (135, min(255, 206 + y // 5), 235)
        pygame.draw.line(screen, color, (0, y), (WIDTH, y))
    pygame.draw.rect(screen, (34, 139, 34), pygame.Rect(0, HEIGHT - 50, WIDTH, 50))


def create_boss_sprite():
    surface = pygame.Surface((80, 80), pygame.SRCALPHA)
    pygame.draw.circle(surface, BLUE, (40, 40), 40)
    pygame.draw.polygon(surface, BLACK, [(20, 20), (35, 30), (20, 30)])
    pygame.draw.polygon(surface, BLACK, [(60, 20), (45, 30), (60, 30)])
    pygame.draw.rect(surface, BLACK, (30, 50, 20, 10))
    return surface


# --- POLICES ---
font = pygame.font.SysFont(None, 24)
title_font = pygame.font.SysFont(None, 48)
# --- MODIFICATION ICI : Police augmentée pour le Game Over (22) ---
small_font = pygame.font.SysFont(None, 22)


# --- CLASSES ---
class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2, HEIGHT // 2, 30, 40)
        self.sprite = create_player_sprite()
        self.velocity_y = 0
        self.gravity = 0.5
        # La force du saut à -13 avec une gravité de 0.5 permet de monter d'environ 170 pixels.
        # C'est largement suffisant pour un espacement de 110 pixels.
        self.jump_force = -13
        self.hp = 3
        self.max_hp = 3
        self.score = 0
        self.second_chance_used = False

    def jump(self):
        self.velocity_y = self.jump_force

    def update(self):
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y


class Platform:
    def __init__(self):
        # Dimensions aléatoires adaptées à la nouvelle fenêtre (largeur 80-130)
        self.rect = pygame.Rect(random.randint(0, WIDTH - 80), -10, random.randint(80, 130), 15)
        self.is_eco = random.choice([True, False, False])
        self.visited = False


class Trash:
    def __init__(self, start_x=None, start_y=-50):
        x_pos = start_x if start_x is not None else random.randint(0, WIDTH - 30)
        self.rect = pygame.Rect(x_pos, start_y, 30, 30)
        self.sprite = TRASH_IMG
        self.speed = random.randint(3, 6)

    def update(self):
        self.rect.y += self.speed


# --- VARIABLES GLOBALES ---
player = Player()
platforms = [Platform()]
platforms[0].rect.y = HEIGHT - 50
trashes = []
state = "PLAYING"

boss_sprite = create_boss_sprite()
countdown_start = 0

trivia_q = "Quel dechet met le plus de temps a se decomposer ?"
trivia_options = ["A) Trognon de pomme", "B) Bouteille plastique", "C) Journal"]
trivia_answer = pygame.K_b

# --- BOUCLE PRINCIPALE ---
running = True

while running:
    draw_gradient_background(screen)
    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            running = False

    if state == "PLAYING":
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_q]: player.rect.x -= 5
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: player.rect.x += 5

        if player.rect.right < 0:
            player.rect.left = WIDTH
        elif player.rect.left > WIDTH:
            player.rect.right = 0

        player.update()

        # Scrolling de la caméra commence à y < HEIGHT // 2
        if player.rect.y < HEIGHT // 2:
            offset = (HEIGHT // 2) - player.rect.y
            player.rect.y = HEIGHT // 2

            for p in platforms: p.rect.y += offset
            for t in trashes: t.rect.y += offset

        while len(platforms) < 8:
            highest_y = min([p.rect.y for p in platforms])
            new_p = Platform()
            # Ecart corrigé : espacement maximal Y de 110 pour s'assurer que le joueur peut monter
            new_p.rect.y = highest_y - random.randint(60, 110)
            platforms.append(new_p)

        if player.score >= 10000:
            state = "VICTORY"

        elif player.score >= 5000:
            boss_x = WIDTH // 2 - 40 + int(math.sin(time.time() * 3) * 100)
            screen.blit(boss_sprite, (boss_x, 20))
            if random.randint(1, 100) < 6:
                trashes.append(Trash(start_x=boss_x + 30, start_y=80))
        else:
            if random.randint(1, 100) < 3:
                trashes.append(Trash())

        for p in platforms:
            if player.velocity_y > 0 and player.rect.colliderect(p.rect) and player.rect.bottom <= p.rect.bottom:
                player.jump()
                if not p.visited:
                    player.score += 75
                    p.visited = True
                    if p.is_eco: player.score += 50

        for t in trashes[:]:
            t.update()
            if player.rect.colliderect(t.rect):
                player.hp -= 1
                trashes.remove(t)
                if player.hp <= 0:
                    if not player.second_chance_used:
                        state = "TRIVIA"
                    else:
                        state = "GAME_OVER"

        if player.rect.top > HEIGHT:
            if not player.second_chance_used:
                state = "TRIVIA"
            else:
                state = "GAME_OVER"

        platforms = [p for p in platforms if p.rect.y < HEIGHT]
        trashes = [t for t in trashes if t.rect.y < HEIGHT]

        # Dessins
        screen.blit(player.sprite, player.rect)
        for p in platforms:
            color = GREEN if p.is_eco else GRAY
            pygame.draw.rect(screen, color, p.rect)
        for t in trashes:
            screen.blit(t.sprite, t.rect)

        score_val = f"Score : {int(player.score)}"
        score_txt = font.render(score_val, True, BLACK)
        score_rect = score_txt.get_rect(topleft=(10, 10))
        pygame.draw.rect(screen, WHITE, score_rect.inflate(10, 5), 0)
        pygame.draw.rect(screen, BLACK, score_rect.inflate(10, 5), 2)
        screen.blit(score_txt, score_rect)

        # Dessiner les VRAIS COEURS
        for i in range(player.hp):
            draw_heart(screen, WIDTH - 90 + i * 25, 10)

    elif state == "TRIVIA":
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        q_txt = title_font.render("Seconde Chance !", True, GREEN)
        screen.blit(q_txt, (WIDTH // 2 - q_txt.get_width() // 2, 100))
        pygame.draw.rect(screen, WHITE, (20, 180, WIDTH - 40, 200), 0)
        pygame.draw.rect(screen, GREEN, (20, 180, WIDTH - 40, 200), 4)
        screen.blit(font.render(trivia_q, True, BLACK), (40, 200))
        for i, opt in enumerate(trivia_options):
            screen.blit(font.render(opt, True, BLACK), (70, 250 + i * 40))

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == trivia_answer:
                    player.hp = player.max_hp
                    player.velocity_y = -15
                    player.rect.y = HEIGHT // 2
                    player.second_chance_used = True
                    state = "COUNTDOWN"
                    countdown_start = time.time()
                elif event.key in [pygame.K_a, pygame.K_b, pygame.K_c]:
                    state = "GAME_OVER"

    elif state == "COUNTDOWN":
        remaining = 3 - int(time.time() - countdown_start)
        if remaining <= 0:
            state = "PLAYING"
        else:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            count_txt = title_font.render(f"Reprise dans {remaining}...", True, BLUE)
            screen.blit(count_txt, (WIDTH // 2 - count_txt.get_width() // 2, HEIGHT // 2))

    elif state == "BOSS":
        screen.fill((10, 10, 20))
        boss_txt = title_font.render("TRASH BEAST !", True, RED)
        screen.blit(boss_txt, (WIDTH // 2 - boss_txt.get_width() // 2, HEIGHT // 2))
        info_txt = font.render("(Appuie sur ESPACE pour le vaincre)", True, WHITE)
        screen.blit(info_txt, (WIDTH // 2 - info_txt.get_width() // 2, HEIGHT // 2 + 50))

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                player.score += 1000
                state = "PLAYING"

    elif state == "GAME_OVER":
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        over_txt = title_font.render("GAME OVER", True, RED)
        over_txt_rect = over_txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(over_txt, over_txt_rect)

        # Texte avec small_font augmentée à 22
        restart_txt = small_font.render("Appuyez sur Entree pour rejouer", True, WHITE)
        restart_txt_rect = restart_txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        screen.blit(restart_txt, restart_txt_rect)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            player = Player()
            platforms = [Platform()]
            platforms[0].rect.y = HEIGHT - 50
            trashes = []
            state = "PLAYING"

    elif state == "VICTORY":
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        win_txt = title_font.render("VICTOIRE !", True, GOLD)
        win_txt_rect = win_txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(win_txt, win_txt_rect)

        # Texte avec small_font augmentée à 22
        restart_txt = small_font.render("Appuyez sur Entree pour rejouer", True, WHITE)
        restart_txt_rect = restart_txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        screen.blit(restart_txt, restart_txt_rect)

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