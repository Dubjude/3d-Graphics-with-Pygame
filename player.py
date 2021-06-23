import pygame as pg
import os
import math
from math import sin, cos, sqrt
import pygame.gfxdraw

black = (0,0,0)
white = (255,255,255)
red = (255, 0, 0)
green = (0, 255, 0)
darkgreen = (0, 150, 0)
darkgrey = (96,96,96)
lightgrey = (192,192,192)
grey = (150,150,150)
yellow = (255,255,0)
blue = (0,0,255)
lightblue = (127, 223, 255)
brown = (76, 41, 0)
beige = (245,245,220)


class Player():
    def __init__(self, camera, size, win_width, win_height):
        self.camera = camera
        self.dpi = 500

        self.camera.position[1] += 300

        self.size = size
        self.speed = 1.25
        self.sprint = self.speed*2.5

        self.win_width = win_width
        self.win_height = win_height

    def update_cursor(self, event):
        x,y = event.rel
        x /= self.dpi
        y /= self.dpi
        if self.camera.rotation[0] > math.pi/2:
            if y < 0:
                y *= -1
        elif self.camera.rotation[0] < -math.pi/2:
            if y > 0:
                y *= -1
        self.camera.rotation[0] -= y
        self.camera.rotation[1] -= x

    def move(self, keys):
        x,y = 5*math.sin(self.camera.rotation[1]), 5*math.cos(self.camera.rotation[1])

        if keys[pg.K_LSHIFT]:
            speed = self.sprint
        else:
            speed = self.speed

        if keys[pg.K_a]:
            self.camera.position[0] += y*speed
            self.camera.position[2] -= x*speed
        elif keys[pg.K_d]:
            self.camera.position[0] -= y*speed
            self.camera.position[2] += x*speed
        elif keys[pg.K_q]:
            self.camera.position[1] -= 20
        elif keys[pg.K_e]:
            self.camera.position[1] += 20
        elif keys[pg.K_w]:
            self.camera.position[0] += x*speed
            self.camera.position[2] += y*speed
        elif keys[pg.K_s]:
            self.camera.position[0] -= x*speed
            self.camera.position[2] -= y*speed

    def draw_cursor(self, screen):
        pg.draw.line(screen, black, (self.win_width/2-10,self.win_height/2),(self.win_width/2+10,self.win_height/2), 2)
        pg.draw.line(screen, black, (self.win_width/2,self.win_height/2-10),(self.win_width/2,self.win_height/2+10), 2)
