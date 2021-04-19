# Spritesheet

import pygame as pg
import os

game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, "Images")

class Spritesheet(object):
    def __init__(self, filename):
        self.sheet = pg.image.load(os.path.join(img_folder, "paintsheet.png")).convert()
    
    def image_at(self, rectangle, colorkey = None):
        # loads image from x, y, x+offset, y+offset
        rect = pg.Rect(rectangle)
        image = pg.Surface((50,50)).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            image.set_colorkey(colorkey)
        return image

    def images_at(self, rects, colorkey = None):
        # loads multiple images, supply a list of coordinates
        return [self.image_at(rect, colorkey) for rect in rects]

    def load_strip(self, rect, image_count, colorkey = None):
        # Loads a strip of images and returns them as a list
        tups = [(rect[0] + rect[2]*x, rect[1], rect[2], rect[3])
            for x in range(image_count)]
        
        return self.images_at(tups, colorkey)
