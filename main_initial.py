import pygame as pg
import random
from settings import *
from spritesheet import *
import os

vec = pg.math.Vector2


class Player(pg.sprite.Sprite):
    #sprite for player
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.fillr = 255
        self.fillg = 255
        self.fillb = 255

        # self.image = pg.Surface((50,50))
        self.image = inky_ship
        self.direction = 'up'
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH *4/5, HEIGHT /2)
        self.pos = vec(self.rect.x, self.rect.y)
        self.vel = vec(0,0)
        self.acc = vec(0,0)
        self.vx = 0
        self.vy = 0
        
        self.exp = 0
        self.level = 0
        self.shield = 400
        self.powerup = 200
        self.power = 0
        self.power_drain = 0.5
        self.shoot_delay = 55
        self.red_spread = 1
        self.shoot_delay2 = 20
        self.shoot_delay3 = 300
        self.last_shot = pg.time.get_ticks()
        # self.radius = 19
        self.dmgr = 17
        self.dmgg = 55
        self.dmgb = 12
        self.dmgs = 2
        self.specialradius = 1

        self.shotcostr = 2
        self.shotcostg = 15
        self.shotcostb = 1
        #pg.draw.circle(self.image, RED, self.rect.center, self.radius)
        
    def update(self):            #movement
        # self.image.fill((255-self.fillr, 255-self.fillg, 255-self.fillb))
        if self.powerup > 500:
            self.powerup = 500        
        elif self.powerup > 0:
            self.powerup -= self.power_drain
        else:
            self.powerup = 0
        
        # Movement
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.direction = 'left'                 
            self.acc.x = -PLAYER_ACC
            self.image = pg.transform.rotate(inky_ship, 90)
            self.image.set_colorkey(WHITE)     
      
        if keys[pg.K_RIGHT]:
            self.direction = 'right' 
            self.acc.x = PLAYER_ACC
            self.image = pg.transform.rotate(inky_ship, 270)
            self.image.set_colorkey(WHITE)           
                       
        if keys[pg.K_UP]:
            self.direction = 'up'
            self.acc.y = -PLAYER_ACC
            self.image = pg.transform.rotate(inky_ship, 0)
            self.image.set_colorkey(WHITE)  
            
        if keys[pg.K_DOWN]:
            self.direction = 'down'
            self.acc.y = PLAYER_ACC
            self.image = pg.transform.rotate(inky_ship, 180)
            self.image.set_colorkey(WHITE)  
            
        if not (keys[pg.K_LEFT] or keys[pg.K_RIGHT] or keys[pg.K_UP] or keys[pg.K_DOWN]):
            self.acc.x = 0
            self.acc.y = 0


        # apply acceleration
        self.vel.x += self.acc.x
        self.vel.y += self.acc.y

        # apply velo
        self.pos.x += self.vel.x #+ 0.5 * self.acc.x
        self.pos.y += self.vel.y #+ 0.5 * self.acc.y

        # apply friction
        self.vel.x += self.vel.x * PLAYER_FRICTION
        self.vel.y += self.vel.y * PLAYER_FRICTION
        
        # wraparound    
        if self.pos.x > WIDTH:
            self.pos.x = 0
        elif self.pos.x < 0:
            self.pos.x = WIDTH
        elif self.pos.y > HEIGHT:
            self.pos.y = 0
        elif self.pos.y < 0:
            self.pos.y = HEIGHT

        self.rect.center = self.pos

        # shooting
        if keys[pg.K_z]:
            self.shoot()
        if keys[pg.K_x]:
            self.shoot2()
        if keys[pg.K_c]:
            self.shoot3()
        
        # special
        if keys[pg.K_SPACE]:
            if self.power == 255:
                self.special()
                self.power = 0

        # die on contact
        hits = pg.sprite.spritecollide(self, Game.mob, True, pg.sprite.collide_rect_ratio(0.7)) 
        if hits:
            Game.reset()   
            Game.show_go_screen()
        
        # collect potion
        hits = pg.sprite.spritecollide(Game.player, Game.all_potion, True)
        for hit in hits:
            if type(hit) is Red_potion:
                hit.kill()
                if self.fillr < (255-75):
                    self.fillr += 75
                else:
                    self.fillr = 255
            if type(hit) is Green_potion:
                hit.kill()
                if self.fillg < (255-75):
                    self.fillg += 75
                else:
                    self.fillg = 255
            if type(hit) is Blue_potion:
                hit.kill()
                if self.fillb < (255-75):
                    self.fillb += 75
                else:
                    self.fillb = 255

        self.level = self.exp//1200

            
    # Red Shot
    def shoot(self):
        now = pg.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = BulletRed(self.rect.centerx, self.rect.centery, Game.player)
            Game.all_sprites.add(bullet)
            Game.redbullets.add(bullet)

            # Fade own color
            if self.fillr > 5:
                self.fillr -= self.shotcostr

    # Green Shot
    def shoot2(self):
        now = pg.time.get_ticks()        
        if now - self.last_shot > self.shoot_delay3:
            self.last_shot = now
            bullet = BulletGreen(self.rect.centerx, self.rect.centery, Game.player)
            Game.all_sprites.add(bullet)
            Game.greenbullets.add(bullet)

            # Fade own color
            if self.fillg > 10:
                self.fillg -= self.shotcostg

            if self.level >= 3:
                bullet = BulletGreen(self.rect.centerx, self.rect.centery, Game.player)
                bullet.speed2 = 3
                Game.all_sprites.add(bullet)
                Game.greenbullets.add(bullet)

                bullet = BulletGreen(self.rect.centerx, self.rect.centery, Game.player)
                bullet.speed2 = -3
                Game.all_sprites.add(bullet)
                Game.greenbullets.add(bullet)

    # Blue Laser
    def shoot3(self):
        now = pg.time.get_ticks()        
        if now - self.last_shot > self.shoot_delay2:
            self.last_shot = now
            bullet = BulletBlue(self.rect.centerx, self.rect.centery, Game.player)
            Game.all_sprites.add(bullet)
            Game.bluebullets.add(bullet)

            # Fade own color            
            if self.fillb > 10:
                self.fillb -= self.shotcostb
    
    def special(self):
        bullet = BulletSpecial(self.rect.centerx, self.rect.centery, Game.player)
        Game.all_sprites.add(bullet)
  

    def refill(self, category, num):
        if category == 'all':
            self.fillr = num
            self.fillg = num
            self.fillb = num

class Reds(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.fillr = 0         
        self.fillg = 0
        self.fillb = 0
        self.color = (self.fillr, self.fillg , self.fillb)
        # Random Sizes
        self.image_orig = pg.Surface ((random.randint(70,180), random.randint(70,180)))
        self.image_orig.fill(self.color)
        self.rect = self.image_orig.get_rect()
        self.rect.center = (HEIGHT/2, WIDTH/4)
        
        self.speedy = random.randrange(-5 , 6)
        self.speedx = random.randrange(-5 , 5 )
        self.radius = 5
        self.image = self.image_orig.copy()
        # self.marker = pg.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rot = 0
        self.rot_speed = random.randint(-8, 8)
        self.last_update = pg.time.get_ticks()

    def update(self):
        # self.marker = pg.draw.circle(self.image, RED, self.rect.center, self.radius)
        # self.rotate()

        self.rect.y += self.speedy
        self.rect.x += self.speedx        

        # fill & kill mechanism & leaving paint mark behind
        if self.fillr < 255:
            self.color = (self.fillr, 0 , 0)
            self.image.fill(self.color)
        elif self.fillr > 250:
            self.kill()
            Game.player.exp += 100
            Game.all_hits.append((random.choice(redpaint_images), self.rect.topleft, (self.rect.width + self.rect.height)))
        # and spwaning potion
            i = Red_potion()
            i.rect.center = self.rect.center
            Game.all_sprites.add(i)
            Game.all_potion.add(i)

        # bounce around
        if self.rect.right >= WIDTH + 10:
            self.speedx = -self.speedx
        elif self.rect.left < -10:
            self.speedx = -self.speedx
        elif self.rect.bottom > HEIGHT + 10:
            self.speedy = -self.speedy
        elif self.rect.top < 0:
            self.speedy = -self.speedy

        # hit by bullets (slow and gain player power)
        hits = pg.sprite.spritecollide(self, Game.redbullets, True, pg.sprite.collide_rect)
        for hit in hits:
            self.fillr += Game.player.dmgr

            if Game.player.power < 255:
                Game.player.power += 1
            else:
                Game.player.power = 255     

            if self.speedx < -2:
                self.speedx += 1
            if self.speedx > 2:
                self.speedx -= 1
            if self.speedy < -2:
                self.speedy += 1
            if self.speedy > 2:
                self.speedy -=1
 
            # Game.all_hits.append((RED, self.rect.center, random.randint(15, 20)))
            Game.all_hits.append((random.choice(redpaint_images), self.rect.topleft, (self.rect.width + self.rect.height)//2)) #[(image, pos, size)]
            hits.clear()

        hits = pg.sprite.spritecollide(self, Game.greenbullets, True, pg.sprite.collide_rect)
        for hit in hits:
            hits.clear()

        hits = pg.sprite.spritecollide(self, Game.bluebullets, True, pg.sprite.collide_rect)
        for hit in hits:
            hits.clear()
        

        # self.rotate()
        
    def rotate(self):
        now = pg.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = self.rot + self.rot_speed % 360
            new_image = pg.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center                           

class Greens(Reds):
    def __init__(self):
        Reds.__init__(self)
        self.color = (self.fillr, self.fillg, self.fillb)
        self.image_orig = pg.Surface ((random.randint(50,200), random.randint(50,200)))
        self.image_orig.fill(self.color)
        self.rect = self.image_orig.get_rect()
        self.radius = 5
        self.image = self.image_orig.copy()        

    def update(self):
        # self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx        

        # Fill & kill mechanism
        if self.fillg < 255:
            self.color = (0, self.fillg, 0)
            self.image.fill(self.color)
        elif self.fillg > 250:
            self.kill()
            Game.player.exp += 100
            Game.all_hits.append((random.choice(greenpaint_images), self.rect.topleft, (self.rect.width + self.rect.height)))
        # and spwaning potion
            i = Green_potion()
            i.rect.center = self.rect.center
            Game.all_sprites.add(i)
            Game.all_potion.add(i)            

        # bounce around
        if self.rect.right >= WIDTH + 10:
            self.speedx = -self.speedx
        elif self.rect.left < -10:
            self.speedx = -self.speedx
        elif self.rect.bottom > HEIGHT + 10:
            self.speedy = -self.speedy
        elif self.rect.top < 0:
            self.speedy = -self.speedy

        # hit by bullets slow and player power
        hits = pg.sprite.spritecollide(self, Game.greenbullets, True, pg.sprite.collide_rect)
        for hit in hits:
            self.fillr += Game.player.dmgr

            if Game.player.power < 255:
                Game.player.power += 8
            else:
                Game.player.power = 255
                            
            if self.speedx < -2:
                self.speedx += 1
            if self.speedx > 2:
                self.speedx -= 1
            if self.speedy < -2:
                self.speedy += 1
            if self.speedy > 2:
                self.speedy -=1

            self.fillg += Game.player.dmgg
            # painting screen
            # Game.all_hits.append((random.choice(greenpaint_images), self.rect.topleft, (self.rect.width + self.rect.height)//2)) #[(image, pos, size)]
            hits.clear()

        hits = pg.sprite.spritecollide(self, Game.redbullets, True, pg.sprite.collide_rect)
        for hit in hits:
            hits.clear()

        hits = pg.sprite.spritecollide(self, Game.bluebullets, True, pg.sprite.collide_rect)
        for hit in hits:
            hits.clear()                    

class Blues(Reds):
    def __init__(self):
        Reds.__init__(self)
        self.color = (self.fillr, self.fillg, self.fillb)
        self.image_orig = pg.Surface ((random.randint(50,200), random.randint(50,200)))
        self.image_orig.fill(self.color)
        self.rect = self.image_orig.get_rect()
        self.rect.center = (HEIGHT/2, WIDTH/2)
        self.radius = 5
        self.image = self.image_orig.copy()        

        self.rot = 0
        self.rot_speed = random.randint(-8, 8)
        self.last_update = pg.time.get_ticks()       

    def update(self):
        # self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx        

        #fill & kill mechanism
        if self.fillb < 255:
            self.color = (0, 0, self.fillb)
            self.image.fill(self.color)
        elif self.fillb > 250:
            self.kill()
            Game.player.exp += 100
            # Game.all_hits.append((random.choice(bluepaint_images), self.rect.topleft, (self.rect.width + self.rect.height)))
        # and spwaning potion
            i = Blue_potion()
            i.rect.center = self.rect.center
            Game.all_sprites.add(i)
            Game.all_potion.add(i)            

        # bounce around
        if self.rect.right >= WIDTH + 10:
            self.speedx = -self.speedx
        elif self.rect.left < -10:
            self.speedx = -self.speedx
        elif self.rect.bottom > HEIGHT + 10:
            self.speedy = -self.speedy
        elif self.rect.top < 0:
            self.speedy = -self.speedy

        # hit by bullets, slow and player power gain
        hits = pg.sprite.spritecollide(self, Game.bluebullets, True, pg.sprite.collide_rect)
        for hit in hits:
            self.fillb += Game.player.dmgb

            if Game.player.power < 255:
                Game.player.power += 1
            else:
                Game.player.power = 255   

            if self.speedx < -2:
                self.speedx += 1
            if self.speedx > 2:
                self.speedx -= 1
            if self.speedy < -2:
                self.speedy += 1
            if self.speedy > 2:
                self.speedy -=1                 

            hits.clear()
            # Game.all_hits.append((random.choice(bluepaint_images), self.rect.topleft, (self.rect.width + self.rect.height)//2)) #[(image, pos, size)]


        hits = pg.sprite.spritecollide(self, Game.redbullets, True, pg.sprite.collide_rect)
        for hit in hits:
            hits.clear()

        hits = pg.sprite.spritecollide(self, Game.greenbullets, True, pg.sprite.collide_rect)
        for hit in hits:
            hits.clear()                  

class Purples(Reds):
    def __init__(self):
        Reds.__init__(self)
        self.color = (self.fillr, self.fillg, self.fillb)
        self.image_orig = pg.Surface ((random.randint(50,200), random.randint(50,200)))
        self.image_orig.fill(self.color)
        self.rect = self.image_orig.get_rect()
        self.rect.center = (HEIGHT/2, WIDTH/2)

        self.image = self.image_orig.copy()        

        self.rot = 0
        self.rot_speed = random.randint(-8, 8)
        self.last_update = pg.time.get_ticks()       

    def update(self):
        # self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx        

        #fill & kill mechanism
        self.color = (self.fillr, 0, self.fillb)
        self.image.fill(self.color)

        if self.fillb > (128-Game.player.dmgb) and self.fillr > (128-Game.player.dmgr):
            self.kill()
            Game.player.exp += 200
            # Game.all_hits.append((self.color, self.rect.center, self.rect.width//2))

        # bounce around
        if self.rect.right >= WIDTH + 10:
            self.speedx = -self.speedx
        elif self.rect.left < -10:
            self.speedx = -self.speedx
        elif self.rect.bottom > HEIGHT + 10:
            self.speedy = -self.speedy
        elif self.rect.top < 0:
            self.speedy = -self.speedy


        # hit by bullets
        hits = pg.sprite.spritecollide(self, Game.bluebullets, True, pg.sprite.collide_rect)
        for hit in hits:
            if self.fillb < 128 - Game.player.dmgb:        
                self.fillb += Game.player.dmgb
            
            if Game.player.power < 255:
                Game.player.power += 1
            else:
                Game.player.power = 255                
                hits.clear()
                # Game.all_hits.append((PURPLE, self.rect.center, random.randint(15, 20)))
            
        hits = pg.sprite.spritecollide(self, Game.redbullets, True, pg.sprite.collide_rect)
        for hit in hits:
            if self.fillr < 128 - Game.player.dmgr:
                self.fillr += Game.player.dmgr

            if Game.player.power < 255:
                Game.player.power += 1
            else:
                Game.player.power = 255                
                hits.clear()
                # Game.all_hits.append((PURPLE, self.rect.center, random.randint(15, 20))) 
            
class BulletRed(pg.sprite.Sprite):
    def __init__(self, x, y, ship):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.transform.scale(bullet_img, (10,30))
        self.rect = self.image.get_rect()
        self.rect.inflate(-5, -5)
        
        self.rect.center = (x, y)
        self.speed = 10
        self.speed2 = random.randint(-Game.player.red_spread, Game.player.red_spread)
        self.direction = ship.direction
        self.fill = 50
        
    def update(self):
        if self.direction == 'up':
            self.rect.y -= self.speed
            self.rect.x += self.speed2
            self.image = pg.transform.rotate(bullet_img, 0)
            self.image.set_colorkey(WHITE) 

        if self.direction == 'down':
            self.rect.y += self.speed
            self.rect.x += self.speed2
            self.image = pg.transform.rotate(bullet_img, 180)
            self.image.set_colorkey(WHITE)

        if self.direction == 'right':
            self.rect.x += self.speed
            self.rect.y += self.speed2
            self.image = pg.transform.rotate(bullet_img, 270)
            self.image.set_colorkey(WHITE)             
            
        if self.direction == 'left':
            self.rect.x -= self.speed
            self.rect.y += self.speed2
            self.image = pg.transform.rotate(bullet_img, 90)
            self.image.set_colorkey(WHITE)             
            
        
        # if self.rect.top < 0 or self.rect.right < 0 or self.rect.left > WIDTH or self.rect.top > HEIGHT:
        #     self.kill()

        # Wrap Around
        # if self.rect.centery < 0:
        #     self.rect.centery = HEIGHT
        # if self.rect.centery > HEIGHT:
        #     self.rect.centery = 0
        # if self. rect.centerx < 0:
        #     self.rect.centerx = WIDTH
        # if self.rect.centerx > WIDTH:
        #     self.rect.centerx = 0

class BulletBlue(BulletRed):
    def __init__(self, x, y, ship):
        BulletRed.__init__(self, x, y, ship)
        self.image = pg.transform.scale(shot_blue, (10,30))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 25
        self.direction = ship.direction
        
    def update(self):
        if self.direction == 'up':
            self.rect.y -= self.speed
            self.image = pg.transform.scale(shot_blue, (20,60))
            self.image.set_colorkey(BLACK) 
        if self.direction == 'down':
            self.rect.y += self.speed
            self.image = pg.transform.scale(shot_blue, (20,60))
            self.image.set_colorkey(BLACK)             
        if self.direction == 'right':
            self.image = pg.transform.scale(shot_blue, (40,20))
            self.image.set_colorkey(BLACK)             
            self.rect.x += self.speed
        if self.direction == 'left':
            self.image = pg.transform.scale(shot_blue, (40,20))
            self.image.set_colorkey(BLACK)             
            self.rect.x -= self.speed
        
        # if self.rect.top < 0 or self.rect.right < 0 or self.rect.left > WIDTH or self.rect.top > HEIGHT:
        #     self.kill()

        # Wrap Around
        # if self.rect.centery < 0:
        #     self.rect.centery = HEIGHT
        # if self.rect.centery > HEIGHT:
        #     self.rect.centery = 0
        # if self. rect.centerx < 0:
        #     self.rect.centerx = WIDTH
        # if self.rect.centerx > WIDTH:
        #     self.rect.centerx = 0

class BulletGreen(BulletRed):
    def __init__(self, x, y, ship):
        BulletRed.__init__(self, x, y, ship)
        self.image = shot_green
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.rect.inflate(-5, -5)
        
        self.rect.center = (x, y)
        self.speed = 6
        self.speed2 = 0
        self.direction = ship.direction
        
    def update(self):
        if self.direction == 'up':
            self.rect.y -= self.speed
            self.rect.x += self.speed2
        if self.direction == 'down':
            self.rect.y += self.speed 
            self.rect.x += self.speed2          
        if self.direction == 'right':        
            self.rect.x += self.speed
            self.rect.y += self.speed2
        if self.direction == 'left':     
            self.rect.x -= self.speed
            self.rect.y += self.speed2
        
        # if self.rect.top < 0 or self.rect.right < 0 or self.rect.left > WIDTH or self.rect.top > HEIGHT:
        #     self.kill()

        # Wrap Around
        # if self.rect.centery < 0:
        #     self.rect.centery = HEIGHT
        # if self.rect.centery > HEIGHT:
        #     self.rect.centery = 0
        # if self. rect.centerx < 0:
        #     self.rect.centerx = WIDTH
        # if self.rect.centerx > WIDTH:
        #     self.rect.centerx = 0
        
        # Bounce Around
        if self.rect.right >= WIDTH + 10:
            self.speed = -self.speed
        elif self.rect.left < -10:
            self.speed = -self.speed
        elif self.rect.bottom > HEIGHT + 10:
            self.speed = -self.speed
        elif self.rect.top < 0:
            self.speed = -self.speed 

class BulletSpecial(BulletRed):
    def __init__(self, x, y, ship):
        BulletRed.__init__(self, x, y, ship)
        self.ship = ship
        self.image = shot_special
        self.rect = self.image.get_rect()
        self.rect.center = (0, HEIGHT/2)

    def update(self):
        self.rect.x += 10

        hits = pg.sprite.spritecollide(self, Game.mob, False, pg.sprite.collide_circle)
        for hit in hits:
            if type(hit) == Reds:
                hit.fillr += Game.player.dmgs
            if type(hit) == Blues:
                hit.fillb += Game.player.dmgs
            if type(hit) == Greens:
                hit.fillg += Game.player.dmgs
            if type(hit) == Purples:
                hit.fillr += Game.player.dmgs
                hit.fillb += Game.player.dmgs
            
        if self.rect.x > WIDTH + 50:
            self.kill()



class Red_potion(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.image.load(os.path.join(img_folder, 'red_potion.png')).convert()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.speed = random.randint(-2, -2)

    def update(self):
        self.rect.y += self.speed
        self.rect.x += self.speed
        if self.rect.right >= WIDTH + 10:
            self.speed = -self.speed
        elif self.rect.left < -10:
            self.speed = -self.speed
        elif self.rect.bottom > HEIGHT + 10:
            self.speed = -self.speed
        elif self.rect.top < 0:
            self.speed = -self.speed

class Green_potion(Red_potion):
    def __init__(self):
        Red_potion.__init__(self)
        self.image = pg.image.load(os.path.join(img_folder, 'green_potion.png')).convert()
        self.image.set_colorkey(BLACK)

class Blue_potion(Red_potion):
    def __init__(self):
        Red_potion.__init__(self)
        self.image = pg.image.load(os.path.join(img_folder, 'blue_potion.png')).convert()
        self.image.set_colorkey(BLACK)

class Powerup(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.image.load(os.path.join(img_folder,'laserRedShot.png')).convert()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(20, WIDTH - 20), 0)
        self.speedy = 4
            
    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom > HEIGHT:
            self.kill()
            

# initialize pg and create window
# pg.mixer.init()                                            

pg.init()                                                  #need this for anything
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("INKY!")
clock = pg.time.Clock()
font_name = pg.font.match_font('georgia')

# set up asset folder
game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, "Images")

# Load all game graphics

inky_ship = pg.image.load(os.path.join(img_folder, "inkydog.png")).convert()
inky_ship = pg.transform.scale(inky_ship, (90,90))
shot_special = pg.image.load(os.path.join(img_folder, "shot_special.png")).convert()
shot_special.set_colorkey(WHITE)
ammo_and_life = pg.image.load(os.path.join(img_folder,'ammo_and_life.png')).convert()
ammo_and_life.set_colorkey(WHITE)

ss = Spritesheet("paintsheet.png")
rects = [(0, 1217, 480, 1589), (513, 1190, 920, 1560), (1030, 1190, 1500, 1550), 
         (1550, 1140, 2000, 1600), (1310, 800, 1680, 1120), (1680, 740, 2000, 1140)]
         
# redpaint_images = [ss.images_at(rects, BLACK)]


redpaint1 = pg.image.load(os.path.join(img_folder, "redpaint1.png")).convert()
redpaint1.set_colorkey(WHITE)
redpaint2 = pg.image.load(os.path.join(img_folder, "redpaint2.png")).convert()
redpaint2.set_colorkey(WHITE)
redpaint3 = pg.image.load(os.path.join(img_folder, "redpaint3.png")).convert()
redpaint3.set_colorkey(WHITE)
redpaint4 = pg.image.load(os.path.join(img_folder, "redpaint4.png")).convert()
redpaint4.set_colorkey(WHITE)
redpaint5 = pg.image.load(os.path.join(img_folder, "redpaint5.png")).convert()
redpaint5.set_colorkey(WHITE)
redpaint6 = pg.image.load(os.path.join(img_folder, "redpaint6.png")).convert()
redpaint6.set_colorkey(WHITE)
redpaint_images = [redpaint1, redpaint2, redpaint3, redpaint4, redpaint5, redpaint6]

greenpaint1 = pg.image.load(os.path.join(img_folder, "greenpaint1.png")).convert()
greenpaint1.set_colorkey(WHITE)
greenpaint2 = pg.image.load(os.path.join(img_folder, "greenpaint2.png")).convert()
greenpaint2.set_colorkey(WHITE)
greenpaint3 = pg.image.load(os.path.join(img_folder, "greenpaint3.png")).convert()
greenpaint3.set_colorkey(WHITE)
greenpaint4 = pg.image.load(os.path.join(img_folder, "greenpaint4.png")).convert()
greenpaint4.set_colorkey(WHITE)
greenpaint5 = pg.image.load(os.path.join(img_folder, "greenpaint5.png")).convert()
greenpaint5.set_colorkey(WHITE)
greenpaint6 = pg.image.load(os.path.join(img_folder, "greenpaint6.png")).convert()
greenpaint6.set_colorkey(WHITE)
greenpaint_images = [greenpaint1, greenpaint1, greenpaint3, greenpaint4, greenpaint5, greenpaint6]


bullet_img = pg.image.load(os.path.join(img_folder, "shot_red.png")).convert()
shot_orange = pg.image.load(os.path.join(img_folder, "shot_orange.png")).convert()
shot_green = pg.image.load(os.path.join(img_folder, "shot_green.png")).convert()
shot_blue = pg.image.load(os.path.join(img_folder, "shot_blue.png")).convert()



class Game:
    def __init__(self):
        # Initialise game window etc
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.background = pg.Rect(0,0, WIDTH, HEIGHT)
        self.clock = pg.time.Clock()
        self.running = True
        self.font_name = pg.font.match_font(FONT_NAME)
        self.highscore = 0
        self.level = 0
        self.all_hits = []      #list of: [(image, pos, size), (image, pos, size)]
        
        # Class Game Graphics
        self.arrow1_rect = pg.Rect(40,100, 200, 600)

        # Class Game sprites
        self.all_sprites = pg.sprite.Group()
        self.redbullets = pg.sprite.Group()
        self.greenbullets = pg.sprite.Group()
        self.bluebullets = pg.sprite.Group()
        self.all_bullets = pg.sprite.Group()
        self.all_potion = pg.sprite.Group()
        self.mob = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.player = Player()        
        self.all_sprites.add(self.player)
        self.all_sprites.add(self.powerups)
        self.all_sprites.add(self.redbullets)
        self.all_sprites.add(self.greenbullets)
        self.all_sprites.add(self.bluebullets)
        self.all_sprites.add(self.mob)
        self.all_sprites.add(self.all_potion)

    def newmob(self, color):
        i = color
        self.all_sprites.add(i)
        self.mob.add(i)
    
    def newpotion(self, potiontype):
        i = potiontype
        self.all_sprites.add(i)
        self.all_potion.add(i)
    
    def create_level(self, num_enemies, enemy_type):
        for i in range(num_enemies):
            self.newmob(enemy_type)

    def start_level(self, num):
        if num == 0:
            for i in range(1):
                self.newmob(Reds())
                self.newmob(Blues())
                self.newmob(Greens())
        
        if num == 1:
            self.create_level(7, Reds())
            self.create_level(7, Reds())
            self.create_level(7, Reds())
            self.create_level(7, Reds())
 
        
        if num == 2:
            for i in range(4):
                self.newmob(Greens())
                self.newmob(Reds())

        if num == 3:
            for i in range(4):
                self.newmob(Greens())
                self.newmob(Blues())
        
        if num == 4:
            for i in range(3):
                self.newmob(Reds())
                self.newmob(Blues())
                self.newmob(Purples())

        self.run()

    def run(self):
        # Game Loops
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

            # Win level (killed all mob)
            if len(self.mob) == 0:
                Game.reset()
                self.playing = False
                self.show_levelcomplete_screen()


    def update(self):
        self.all_sprites.update()
        # Powerup hit player        
        empowered = pg.sprite.spritecollide(self.player, self.powerups, True)
        for x in empowered:
            self.player.powerup += 180


    def events(self):
        # Game loop - Events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

    def draw(self):
        # Game Loop - Draw
        pg.draw.rect(self.screen, WHITE, self.background)
        # self.draw_hits(self.all_hits) 
        self.all_sprites.draw(self.screen)
        self.draw_color_bar(30, 30, self.player.fillr, RED)
        self.draw_color_bar(30, 50, self.player.fillg, GREEN)
        self.draw_color_bar(30, 70, self.player.fillb, BLUE)
        self.draw_color_bar(30, 90, self.player.power, GOLD)
        # exp bar, repeats everytime it reaches 1000
        self.draw_exp_bar(0,770, self.player.exp, GOLD)
        self.draw_text('Level ' + str(self.player.level), 20, BLACK, WIDTH/2, HEIGHT - 25)
        # self.draw_text('Exp: ' + str(self.player.exp), 20, BLACK, WIDTH/2 - 40, HEIGHT - 25)

        pg.display.flip()    

    def draw_hits(self, all_hits):  #[(image, pos, size), (image, pos, size)]
        for hit in all_hits:
            self.screen.blit(pg.transform.scale(hit[0], (hit[2], hit[2])), hit[1])
        

    def show_start_screen(self):
        # game splash/start screen
        if not self.running:
            return
        self.screen.fill(LIGHTGREY)
        self.draw_text(TITLE, 90, GOLD, WIDTH/2, HEIGHT * 1/8)
        self.draw_text("Shoot ink at the black boxes to add colour to them", 26, BLACK, WIDTH/2, HEIGHT * 4/13)
        self.draw_text("They explode when they reach their 'true' colour", 26, BLACK, WIDTH/2, HEIGHT * 5/13)
        self.draw_text("The only way to find out their true colour is to shoot them", 26, BLACK, WIDTH/2, HEIGHT * 6/13)
        self.draw_text("You're dead if they touch you or you run out of ink", 26, BLACK, WIDTH/2, HEIGHT * 7/13)

        self.draw_text("'z' to shoot red ink", 35, RED, WIDTH/2 - 350, HEIGHT * 6/9)
        self.draw_text("'x' to shoot green", 35, GREEN, WIDTH/2, HEIGHT * 6/9)
        self.draw_text("'c' to shoot blue", 35, BLUE, WIDTH/2 + 350, HEIGHT * 6/9)
        self.draw_text("Press Enter to start trial level", 25, WHITE, WIDTH/2, HEIGHT * 4/5)

        self.screen.blit(ammo_and_life, self.arrow1_rect)
        self.draw_color_bar(30, 30, self.player.fillr, RED)
        self.draw_color_bar(30, 50, self.player.fillg, GREEN)
        self.draw_color_bar(30, 70, self.player.fillb, BLUE)
        # exp bar, repeats everytime it reaches 1000
        self.draw_exp_bar(0,770, 1199, WHITE)
        self.draw_text('Level ' + str(self.player.level), 20, BLACK, WIDTH/2, HEIGHT - 25)

        pg.display.flip()
        self.waiting_for_key()

    
    def show_go_screen(self):
        # game over/continue
        self.screen.fill(PINK)
        self.draw_text("INKED", 150, RED, WIDTH/2, HEIGHT/4)
        self.draw_text("Press 'r' to try again", 30, WHITE, WIDTH/2, HEIGHT * 9/14)
        self.draw_text("Press Backspace to return to previous level", 30, WHITE, WIDTH/2, HEIGHT * 10/14)
        self.draw_text("But you're encouraged not to give up (:", 22, WHITE, WIDTH/2, HEIGHT * 11/14)
        pg.display.flip()
        self.waiting_for_key()
        self.start_level(self.level)
        self.player.refill('all', 255)


    def show_levelcomplete_screen(self):
        self.screen.fill(GREY)
        self.draw_text("LEVEL COMPLETE", 52, GOLD, WIDTH/2, HEIGHT/5)
        self.draw_text("Press 'n' for next level", 30, WHITE, WIDTH/2, HEIGHT * 7/10)
        self.draw_text("Press 'r' to repeat level to gain exp!", 30, WHITE, WIDTH/2, HEIGHT * 8/10)

        # Show next round's enemies
        if self.level == 0:
            self.draw_text("Enemies ahead:", 40, WHITE, WIDTH/2 - 100, HEIGHT/2)
            self.draw_enemy(RED, WIDTH/2 + 70, HEIGHT/2)        
        if self.level == 1:
            self.draw_text("Enemies ahead:", 40, WHITE, WIDTH/2 - 100, HEIGHT/2)
            self.draw_enemy(RED, WIDTH/2 + 70, HEIGHT/2)
            self.draw_enemy(GREEN, WIDTH/2 + 120, HEIGHT/2)
        if self.level == 2:
            self.draw_text("Enemies ahead:", 40, WHITE, WIDTH/2 - 100, HEIGHT/2)
            self.draw_enemy(GREEN, WIDTH/2 + 70, HEIGHT/2)
            self.draw_enemy(BLUE, WIDTH/2 + 120, HEIGHT/2)
        if self.level == 3:
            self.draw_text("Enemies ahead:", 40, WHITE, WIDTH/2 - 100, HEIGHT/2)
            self.draw_enemy(RED, WIDTH/2 + 70, HEIGHT/2)
            self.draw_enemy(BLUE, WIDTH/2 +120, HEIGHT/2)
            self.draw_enemy(PURPLE, WIDTH/2 + 170, HEIGHT/2)
            self.draw_text("Hint: What two", 30, RED, WIDTH/2 - 200, HEIGHT * 3/5)
            self.draw_text("colours make", 30, BLUE, WIDTH/2 + 25, HEIGHT * 3/5)
            self.draw_text("Purple?", 30, PURPLE, WIDTH/2 + 192, HEIGHT * 3/5)
        
        pg.display.flip()
        self.waiting_for_key()
        self.start_level(self.level)
        self.player.refill('all', 255)

    def waiting_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                
                keys = pg.key.get_pressed()    
                if keys[pg.K_RETURN]:
                    waiting = False
                elif keys[pg.K_n]:
                    self.level += 1
                    waiting = False
                elif keys[pg.K_r]:
                    waiting = False
                elif keys[pg.K_BACKSPACE]:
                    self.level -= 1
                    waiting = False


    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)         #true/false is anti-alias. true for yes.
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def draw_enemy(self, color, x, y):
        enemy = pg.Rect(x, y, 40, 40)
        pg.draw.rect(self.screen, color, enemy)

    def draw_color_bar(self, x, y, fillamt, color):
        if fillamt < 0:
            fillamt = 0
        BAR_LENGTH = 255
        BAR_HEIGHT = 15
        fill = (fillamt/255) * BAR_LENGTH
        outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
        fill_rect = pg.Rect(x, y, fill, BAR_HEIGHT)
        pg.draw.rect(self.screen, color, fill_rect)
        pg.draw.rect(self.screen, BLACK, outline_rect, 2)

    def draw_exp_bar(self, x, y, fillamt, color):
        if fillamt < 0:
            fillamt = 0
        BAR_LENGTH = 1200
        BAR_HEIGHT = 30
        fill = (fillamt % 1200)
        outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
        fill_rect = pg.Rect(x, y, fill, BAR_HEIGHT)
        pg.draw.rect(self.screen, color, fill_rect)
        pg.draw.rect(self.screen, BLACK, outline_rect, 2)
    
    def reset(self):
        for i in self.mob:
            i.kill()
        for i in self.redbullets:
            i.kill()
        for i in self.bluebullets:
            i.kill()
        for i in self.greenbullets:
            i.kill()                            
        for i in self.all_potion:
            i.kill()            
        self.player.pos.x = (WIDTH * 4/5)
        self.player.pos.y = (HEIGHT/2)
        self.player.refill('all', 255)        
        


Game = Game()
Game.show_start_screen()
while Game.running:
    Game.start_level(Game.level)

pg.quit()

