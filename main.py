import pygame as pg
import os
import pygame.gfxdraw
import pyautogui
import math
from numba import jit

import graphics3d as g3d
import player as pl
import terrain as ter

# work in progress

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

def main():
    ## ---------- SETUP ---------- ##
    global fps, win_width, win_height, screen_width, win_depth, ratio
    fps = 60
    win_width = 1100
    win_height = 800
    win_depth = 800

    pg.init()
    global screen, clock, font, fps_font
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (1920 / 2 - (win_width/2),30)
    screen = pg.display.set_mode((win_width, win_height))
    pg.display.set_caption("3D Game")
    clock = pg.time.Clock()
    font = pg.font.SysFont("comicsansms", 30)
    fps_font = pg.font.SysFont("comicsansms", 15)
    pg.mouse.set_visible(False)

    global player, engine, terrain
    player_camera = g3d.Camera([win_width/2, win_height/2, 0])
    player = pl.Player(player_camera, (1,150,1), win_width, win_height)
    engine = g3d.Engine3d(screen, win_width, win_height, win_depth, player.camera)
    terrain = ter.Terrain(player, engine)

    terrain.render_triangles()

    ## ---------- LOOP ---------- ##
    global run, time, borders
    run = True
    time = 0
    borders = False

    pyautogui.moveTo(1920 / 2, 30+win_height/2, 0.001)
    pg.event.get()
    pg.mouse.get_rel()
    pg.event.set_grab(True)

    while run:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
            elif event.type == pg.MOUSEMOTION:
                player.update_cursor(event)
            elif event.type == pg.KEYUP:
                if event.key == pg.K_b:
                    borders = not borders

        keys = pg.key.get_pressed()
        mouse = pg.mouse.get_pressed()
        player.move(keys)

        time += 1
        clock.tick(fps)
        draw()
        pg.display.update()

    pg.quit()

def draw():
    screen.fill(lightblue)
    engine.draw(borders=borders)
    #engine.draw_map((800,0), (300,300))
    player.draw_cursor(screen)
    screen.blit(fps_font.render(str(int(clock.get_fps())), False, black, lightblue), (10,10))

if __name__ == '__main__':
    main()
