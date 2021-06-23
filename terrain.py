import pygame as pg
import os
import math
from math import sin, cos, sqrt
import numpy as np
import pygame.gfxdraw
import graphics3d as g3d

from perlin_numpy import (generate_perlin_noise_3d, generate_fractal_noise_3d)

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

class Terrain():
    def __init__(self, player, engine):
        self.player = player
        self.engine = engine

        self.cube_size = 100

    def render_cubes(self):
        chunk, colors = self.generate_perlin(500, 10)
        for pos in chunk:
            self.engine.add(g3d.Cube((pos[0],pos[1],pos[2]),
            (self.cube_size,self.cube_size,self.cube_size), (0,255-pos[1]/-3,0)))

    def render_triangles(self):
        chunk_size = 20
        chunk, max_color = self.generate_perlin(700, chunk_size, 2, -1)
        mult = 255/max_color

        for y in range(len(chunk)-1):
            for x in range(len(chunk[0])-1):
                color0 = (0,(int((chunk[y][x+1][1]/-1)*mult)),0)
                color1 = (0,(int((chunk[y+1][x+1][1]/-1)*mult)),0)

                if color0[1] < 20:
                    color0 = (255-color0[1],255-color0[1]*2,255-color0[1])
                if color1[1] < 20:
                    color1 = (255-color1[1],255-color1[1]*2,255-color1[1])

                self.engine.add(g3d.Triangle((chunk[y][x][0],chunk[y][x][1],chunk[y][x][2]),
                (self.cube_size,self.cube_size,self.cube_size),
                [[chunk[y][x][0],chunk[y][x][1],chunk[y][x][2]],
                [chunk[y][x+1][0],chunk[y][x+1][1],chunk[y][x+1][2]],
                [chunk[y+1][x][0],chunk[y+1][x][1],chunk[y+1][x][2]]],color0))
                self.engine.add(g3d.Triangle((chunk[y][x+1][0],chunk[y][x+1][1],chunk[y][x+1][2]),
                (self.cube_size,self.cube_size,self.cube_size),
                [[chunk[y][x+1][0],chunk[y][x+1][1],chunk[y][x+1][2]],
                [chunk[y+1][x+1][0],chunk[y+1][x+1][1],chunk[y+1][x+1][2]],
                [chunk[y+1][x][0],chunk[y+1][x][1],chunk[y+1][x][2]]],color1))

    def generate_perlin(self, amplitude, chunk_size, ndim=1, precision=-2):
        noise = generate_perlin_noise_3d((1,chunk_size,chunk_size), (True, True, True))
        noise_2 = []
        chunk = []

        for row in noise:
            for i, col in enumerate(row):
                noise_2.append([])
                for pos in col:
                    pos = round((pos * amplitude),precision)
                    noise_2[i].append(pos)

        colors = []

        if ndim == 1:
            for x_pos in range(len(noise_2)):
                for z_pos in range(len(noise_2)):
                    chunk.append((x_pos*100-chunk_size/2*100,noise_2[z_pos][x_pos]-self.get_max(noise_2), z_pos*100-chunk_size/2*100))
        elif ndim == 2:
            for x_pos in range(len(noise_2)):
                chunk.append([])
                for z_pos in range(len(noise_2)):
                    chunk[x_pos].append((x_pos*100-chunk_size/2*100,noise_2[z_pos][x_pos]-self.get_max(noise_2), z_pos*100-chunk_size/2*100))
                    colors.append((noise_2[z_pos][x_pos]-self.get_max(noise_2))*-1)
        return chunk, max(colors)

    def get_min(self, array_2d):
        mins = []
        for row in array_2d:
            mins.append(min(row))
        return min(mins)

    def get_max(self, array_2d):
        maxs = []
        for row in array_2d:
            maxs.append(max(row))
        return max(maxs)
