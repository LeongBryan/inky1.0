import pygame as pg
import random
from settings import *
from main import *
import os
vec = pg.math.Vector2

class Game:
    def __init__(self):
        # Initialise game window etc
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.font_name = pg.font.match_font(FONT_NAME)
        self.highscore = 0

        self.all_sprites = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.mob = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.player = Player()        
        self.all_sprites.add(self.player)
        self.all_sprites.add(self.powerups)
        self.all_sprites.add(self.bullets)
        self.all_sprites.add(self.mob)    

    def newmob_red(self):
        i = Reds()
        self.all_sprites.add(i)
        self.mob.add(i)    
        
    def newpowerup(self):
        bonus = Powerup()
        self.all_sprites.add(bonus)
        self.powerups.add(bonus)    
    
    def level1(self):
        # Sprites      
        self.newpowerup()

        for i in range(8):
            self.newmob_red()
        
        self.run()

    def run(self):
        # Game Loops
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
            self.draw_power_bar
            self.draw_shield_bar

    def update(self):
        self.all_sprites.update()
        # Powerup hit player        
        empowered = pg.sprite.spritecollide(self.player, self.powerups, True)
        for x in empowered:
            self.player.powerup += 180

        for m in self.mob:        
            hits = pg.sprite.spritecollide(m, self.bullets, False, True)
            if hits:
                m.fillx += player.dmgx


    def events(self):
        # Game loop - Events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

    def draw(self):
        # Game Loop - Draw
        self.screen.fill(CYAN)
        self.all_sprites.draw(self.screen)
        pg.display.flip()    

    def show_start_screen(self):
        # game splash/start screen
        if not self.running:
            return
        self.screen.fill(CYAN)
        self.draw_text(TITLE, 48, WHITE, WIDTH/2, HEIGHT/4)
        self.draw_text("z for red, x for blue, c for green", 22, WHITE, WIDTH/2, HEIGHT/2)
        self.draw_text("Press a key to play", 22, WHITE, WIDTH/2, HEIGHT * 3/4)
        pg.display.flip()
        self.waiting_for_key()
    
    def show_go_screen(self):
        # game over/continue
        self.screen.fill(CYAN)
        self.draw_text("INK RAN DRY", 48, WHITE, WIDTH/2, HEIGHT/4)
        self.draw_text("Press a key to try again", 22, WHITE, WIDTH/2, HEIGHT * 3/4)
        pg.display.flip()
        self.waiting_for_key()

    def waiting_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.KEYUP:
                    waiting = False

    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)         #true/false is anti-alias. true for yes.
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def draw_shield_bar(self, x, y, pct):
        if pct <0:
            pct = 0
        BAR_LENGTH = 250
        BAR_HEIGHT = 15
        fill = (pct/100) * BAR_LENGTH
        outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
        fill_rect = pg.Rect(x, y, fill, BAR_HEIGHT)
        pg.draw.rect(surface, GREEN, fill_rect)
        pg.draw.rect(surface, WHITE, outline_rect, 2)
        if Bry.shield <= 20:
            pg.draw.rect(surface, RED, fill_rect)

    def draw_power_bar(self, x, y, pct):
        if pct <0:
            pct = 0
        BAR_LENGTH = 740
        BAR_HEIGHT = 15
        fill = (pct/500) * BAR_LENGTH
        outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
        fill_rect = pg.Rect(x, y, fill, BAR_HEIGHT)
        pg.draw.rect(surface, MAGENTA, fill_rect)
        pg.draw.rect(surface, MAGENTA, outline_rect, 1)

Game = Game()
Game.show_start_screen()
while Game.running:
    Game.level1()
    Game.show_go_screen()

pg.quit()

