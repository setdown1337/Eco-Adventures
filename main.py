import pygame
import random
import json
import time

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
BLACK = (0, 0, 0)


# --- FONCTIONS DE DESSIN DE SPRITES ---
# Ces fonctions créent des images simples direktement en code
def create_player_sprite():
    surface = pygame.Surface((30, 30), pygame.SRCALPHA)
    # Tête (Cercle vert)
    pygame.draw.circle(surface, GREEN, (15, 15), 15)
    # Yeux (Cercles noirs)
    pygame.draw.circle(surface, BLACK, (10, 10), 3)
    pygame.draw.circle(surface, BLACK, (20, 10), 3)
    # Bouche (Petit arc)
    pygame.draw.arc(surface, BLACK, (10, 15, 10, 10), 3.14, 0, 2)
    return surface


def create_trash_sprite():
    surface = pygame.Surface((20, 20), pygame.SRCALPHA)
    # Partie rouge du trognon (Losange)
    pygame.draw.polygon(surface, RED, [(10, 0), (20, 10), (10, 20), (0, 10)])
    # Partie blanche centrale
    pygame.draw.rect(surface, WHITE, (5, 5, 10, 10), 2)
    # Pépins (Petits points noirs)
    pygame.draw.circle(surface, BLACK, (10, 10), 1)
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

    def jump(self):
        self.velocity_y = self.jump_force

    def update(self):
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y


class Platform:
    def __init__(self):
        self.rect = pygame.Rect(random.randint(0, WIDTH - 80), -10, random.randint(60, 100), 15)
        self.is_eco = random.choice([True, False, False])


class Trash:
    def __init__(self):
        self.rect = pygame.Rect(random.randint(0, WIDTH - 20), -50, 20, 20)
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

next_boss_score = 5000
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
        pass  # Ignorer les erreurs de sauvegarde


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
        # CONTRÔLES : Flèches ET ZQSD
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_q]: player.rect.x -= 5
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: player.rect.x += 5
        # (Z pour sauter si un jour on ajoute le saut manuel)
        if keys[pygame.K_ESCAPE]:
            save_game()
            running = False

        if player.rect.right < 0:
            player.rect.left = WIDTH
        elif player.rect.left > WIDTH:
            player.rect.right = 0

        player.update()

        if player.rect.y < HEIGHT // 2:
            offset = (HEIGHT // 2) - player.rect.y
            player.rect.y = HEIGHT // 2
            player.score += offset

            for p in platforms: p.rect.y += offset
            for t in trashes: t.rect.y += offset

        while len(platforms) < 8:
            highest_y = min([p.rect.y for p in platforms])
            new_p = Platform()
            new_p.rect.y = highest_y - random.randint(60, 100)
            platforms.append(new_p)

        if random.randint(1, 100) < 3:
            trashes.append(Trash())

        for p in platforms:
            if player.velocity_y > 0 and player.rect.colliderect(p.rect) and player.rect.bottom <= p.rect.bottom:
                player.jump()
                if p.is_eco: player.score += 50

        for t in trashes[:]:
            t.update()
            if player.rect.colliderect(t.rect):
                player.hp -= 1
                trashes.remove(t)
                if player.hp <= 0:
                    state = "TRIVIA"

        if player.rect.top > HEIGHT:
            state = "TRIVIA"

        platforms = [p for p in platforms if p.rect.y < HEIGHT]
        trashes = [t for t in trashes if t.rect.y < HEIGHT]

        if player.score >= next_boss_score:
            state = "BOSS"

        # DESSINER : Le bonhomme et les trognons de pomme
        screen.blit(player.sprite, player.rect)
        for p in platforms:
            color = GREEN if p.is_eco else GRAY
            pygame.draw.rect(screen, color, p.rect)
        for t in trashes:
            screen.blit(t.sprite, t.rect)

        score_txt = font.render(f"Score: {int(player.score)} | HP: {player.hp}", True, BLACK)
        screen.blit(score_txt, (10, 10))

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
                    state = "COUNTDOWN"
                    countdown_start = time.time()
                elif event.key in [pygame.K_a, pygame.K_b, pygame.K_c]:
                    state = "GAME_OVER"

    elif state == "COUNTDOWN":
        remaining = 3 - int(time.time() - countdown_start)
        if remaining <= 0:
            state = "PLAYING"
        else:
            count_txt = title_font.render(f"Reprise dans {remaining}...", True, BLUE)
            screen.blit(count_txt, (WIDTH // 2 - count_txt.get_width() // 2, HEIGHT // 2))

    elif state == "BOSS":
        boss_txt = title_font.render("BOSS TRASH BEAST !", True, RED)
        screen.blit(boss_txt, (WIDTH // 2 - boss_txt.get_width() // 2, HEIGHT // 2))
        info_txt = font.render("(Appuie sur ESPACE pour le vaincre)", True, BLACK)
        screen.blit(info_txt, (WIDTH // 2 - info_txt.get_width() // 2, HEIGHT // 2 + 50))

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                next_boss_score += 5000
                player.score += 1000
                state = "PLAYING"

    elif state == "GAME_OVER":
        over_txt = title_font.render("GAME OVER", True, RED)
        screen.blit(over_txt, (WIDTH // 2 - over_txt.get_width() // 2, HEIGHT // 2))

        restart_txt = font.render("Appuyez sur Entree pour rejouer", True, BLACK)
        screen.blit(restart_txt, (WIDTH // 2 - restart_txt.get_width() // 2, HEIGHT // 2 + 50))

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