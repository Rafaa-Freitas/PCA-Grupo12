import pygame
import os
import time
import random

#Iniciando fontes no sistema
pygame.font.init()

WIDTH, HEIGHT = 1600, 900
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter GRUPO 12")

# Carregando Imagens
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

# Jogador
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))

# Classe de Lasers

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

        def draw(self, window):
            window.blit(self.img, (self.x, self.y))

        def move(self, velocidade):
            self.y += velocidade

        def off_screen(self, height):
            return self.y <= height and self.y >= 0

        def collision(self, obj):
            return collide(obj, self)

# Classe padrão de naves
class Nave:
    def __init__(self, x, y, health = 100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

class Player(Nave):
    def __init__(self, x, y, health = 100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

class Enemy(Nave):
    COLOR_MAP = {
        "red": (RED_SPACE_SHIP, RED_LASER),
        "green": (GREEN_SPACE_SHIP, GREEN_LASER),
        "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
    }

    def __init__(self, x, y, color, health = 100): # color pode ser "red", "green", "blue"
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color] # Adicionando as propriedades de cores no ship image e laser image
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, velocidade):
        self.y += velocidade

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    run = True
    FPS = 60
    level = 0
    vidas = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    enemies = []
    wave_lenght = 5
    enemy_velocidade = 3

    player_velocidade = 10

    player = Player(750, 800)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        #Colocando o Background através da variável WIN de window e BG de background
        WIN.blit(BG, (0,0))

        #Colocando Texto na Tela
        vidas_label = main_font.render(f'Vidas: {vidas}', 1, (255, 255, 255))
        level_label = main_font.render(f'Level: {level}', 1, (255, 255, 255))

        WIN.blit(vidas_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("Você Perdeu!", 1, (255, 255, 255))
            WIN.blit(lost_label, ((WIDTH/2 - lost_label.get_width()/2), (HEIGHT/2 - lost_label.get_height()/2)))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if vidas <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_lenght += 2

            for i in range(wave_lenght):
                enemy = Enemy(random.randrange(50, WIDTH-50), random.randrange(-1500, -50), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_velocidade > 0: #Esquerda
            player.x -= player_velocidade
        if keys[pygame.K_d] and player.x + player_velocidade + player.get_width() < WIDTH: #Direita
            player.x += player_velocidade
        if keys[pygame.K_w] and player.y - player_velocidade > 0: #Cima
            player.y -= player_velocidade
        if keys[pygame.K_s] and player.y + player_velocidade + player.get_height() < HEIGHT: #Baixo
            player.y += player_velocidade
        if keys[pygame.K_ESCAPE]:
            run = False

        for enemy in enemies[:]:
            enemy.move(enemy_velocidade)

            if enemy.y + enemy.get_height() > HEIGHT:
                vidas -= 1
                enemies.remove(enemy)

main()