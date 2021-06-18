import pygame
from pygame import mixer
import os
import time
import random
import cv2
import numpy as np

#Carregando sons

pygame.mixer.pre_init(44100,-16, 2, 512)
pygame.mixer.init()
LASER_SOUND = "assets/laser.wav"
BGMUSIC = "assets/bg.wav"

#tocamusica bg
pygame.mixer.music.load(BGMUSIC)
pygame.mixer.Channel(1).play(pygame.mixer.Sound(BGMUSIC))

##################video intro
cap = cv2.VideoCapture('assets/video.mp4')
if (cap.isOpened()== False): 
  print("Error opening video  file")
while(cap.isOpened()):  
  ret, frame = cap.read()
  if ret == True:
    cv2.imshow('Frame', frame)
    # Press Q on keyboard to  exit
    if cv2.waitKey(25) & 0xFF == ord('q'):
      break
   
  else: 
    break
cap.release()
cv2.destroyAllWindows()
##################

#Iniciando fontes no sistema
pygame.font.init()
WIDTH, HEIGHT = 1600, 900
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("GRUPO 12 - PCA")

# Carregando Imagens
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))
VIRUS_ENEMY = pygame.transform.scale(pygame.image.load(os.path.join("assets", "coronavirus.png")), (50, 50))


# Jogador
YELLOW_SPACE_SHIP = pygame.transform.scale(pygame.image.load(os.path.join("assets", "navepixgr.png")), (100, 90))

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "vacinapng.png"))

# Background image
BG = pygame.image.load(os.path.join("assets", "bg-earth.png"))

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
        return not(self.y <= height and self.y >= 0)
    def collision(self, obj):
        return collide(obj, self)
# Classe padrão de naves
class Nave:
    COOLDOWN = 20

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
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, velocidade, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(velocidade)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)
    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
#tocando som ao disparar
            pygame.mixer.music.load(LASER_SOUND)
            pygame.mixer.music.play()

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

    def move_lasers(self, velocidade, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(velocidade)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.lasers.remove(laser)
class Enemy(Nave):
    COLOR_MAP = {
        "red": (RED_SPACE_SHIP, RED_LASER),
        "green": (GREEN_SPACE_SHIP, GREEN_LASER),
        "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
    }

    def __init__(self, x, y, color, health = 100): # color pode ser "red", "green", "blue"
        super().__init__(x, y, health)
        #self.ship_img, self.laser_img = self.COLOR_MAP[color] # Adicionando as propriedades de cores no ship image e laser image
        self.ship_img = VIRUS_ENEMY
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
    enemy_velocidade = 2

    player_velocidade = 10

    laser_vel = 5

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
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_velocidade)
            enemy.move_lasers(laser_vel, player)
            if enemy.y + enemy.get_height() > HEIGHT:
                vidas -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)

main()
