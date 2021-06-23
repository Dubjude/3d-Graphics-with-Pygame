import pygame as pg
import os
import math
from math import sin, cos, tan, sqrt
import pygame.gfxdraw
import numpy as np
from numba import jit, njit, jitclass, types

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


class Engine3d():
    def __init__(self, screen, screen_width, screen_height, screen_depth, camera):
        self.screen = screen
        self.width = screen_width
        self.height = screen_height
        self.depth = screen_depth
        self.camera = camera
        self.shapes = []

        self.font = pg.font.SysFont("comicsansms", 30)

    def matrix_multiplication(self, a, b):
        columns_a = len(a[0])
        rows_a = len(a)
        columns_b = len(b[0])
        rows_b = len(b)
        result_matrix = [[j for j in range(columns_b)] for i in range(rows_a)]
        if columns_a == rows_b:
            for x in range(rows_a):
                for y in range(columns_b):
                    sum = 0
                    for k in range(columns_a):
                        sum += a[x][k] * b[k][y]
                    result_matrix[x][y] = sum
            return result_matrix
        else:
            return None

    def flatten_point(self, point):
        point = [
        [point[0]-(self.camera.position[0]-self.camera.start_pos[0])],
        [point[1]-(self.camera.position[1]-self.camera.start_pos[1])],
        [point[2]-(self.camera.position[2]-self.camera.start_pos[2])]]

        scale = self.depth/2

        rotation_x = [[1, 0, 0],
                      [0, cos(self.camera.rotation[0]), -sin(self.camera.rotation[0])],
                      [0, sin(self.camera.rotation[0]), cos(self.camera.rotation[0])]]

        rotation_y = [[cos(self.camera.rotation[1]), 0, -sin(self.camera.rotation[1])],
                      [0, 1, 0],
                      [sin(self.camera.rotation[1]), 0, cos(self.camera.rotation[1])]]

        rotation_z = [[cos(self.camera.rotation[2]), -sin(self.camera.rotation[2]), 0],
                      [sin(self.camera.rotation[2]), cos(self.camera.rotation[2]), 0],
                      [0, 0, 1]]

        rotated_2d = self.matrix_multiplication(rotation_y, point)
        rotated_2d = self.matrix_multiplication(rotation_x, rotated_2d)
        rotated_2d = self.matrix_multiplication(rotation_z, rotated_2d)
        distance = 5
        if distance - rotated_2d[2][0] == 0:
            distance += 0.01
        z = 1/(distance - rotated_2d[2][0])
        projection_matrix = [[z, 0, 0],
                            [0, z, 0]]
        projected_2d = self.matrix_multiplication(projection_matrix, rotated_2d)

        projected_x = int(projected_2d[0][0] * scale) + self.width/2
        projected_y = int(projected_2d[1][0] * scale) + self.height/2

        return (projected_x, projected_y)

    def add(self, shape):
        self.shapes.append(shape)

    def distance(self, shape):
        return sqrt(
        (shape.position[0]-self.camera.position[0])**2 +
        (shape.position[1]-self.camera.position[1])**2 +
        (shape.position[2]-self.camera.position[2])**2)

    def is_behind(self, shape):
        #general variables
        plus = 0
        player_x = self.camera.position[0]-self.width/2
        x,z = (shape.position[0]-player_x, shape.position[2]-self.camera.position[2])
        rot_num = self.camera.rotation[1]/(math.pi/2)%4
        roty = math.pi * rot_num / 2

        # for x axis rotation
        if self.camera.rotation[0] <= -math.pi/4:
            plus = -250
        if self.camera.rotation[0] >= math.pi/4:
            plus = 250
        if roty <= -math.pi/2:
            plus *= -1
        if roty >= math.pi/2:
            plus *= -1

        # for y axis rotation
        if roty <= -math.pi:
            roty = (2*math.pi + roty)
        if roty >= math.pi:
            roty = (roty - 2*math.pi)
        gamma = roty - math.pi
        f_x = x * tan(-gamma) + plus
        if roty <= 0:
            if gamma >= -3*math.pi/2:
                if z < f_x:
                    return True
            elif gamma <= -3*math.pi/2:
                if z > f_x:
                    return True
        elif roty >= 0:
            if gamma <= -math.pi/2:
                if z < f_x:
                    return True
            elif gamma >= -math.pi/2:
                if z > f_x:
                    return True

        return False

    # ----------------------------------------- CUBE ----------------------------------------------------------
    def render_cube(self, cube):
        point_list = []
        side_list = cube.get_sides(self.camera, self.width, self.height)
        for side in range(len(side_list)):
            point_list.append([])
            for point in cube.sides[side_list[side]]:
                point_list[side].append(self.flatten_point(point))
        return point_list

    def cube_on_screen(self, cube):
        pos = self.flatten_point(cube.position)
        width = cube.size[0]
        if not self.is_behind(cube):
            if pos[0] > -width and pos[0] < self.width+width and pos[1] > -width and pos[1] < self.height+width:
                return True
        return False

    def draw_cube(self, cube_points, cube, borders):
        for side in cube_points:
            pg.gfxdraw.filled_polygon(self.screen, [side[0], side[1], side[2], side[3]],
            (cube.color[0],cube.color[1],cube.color[2],cube.alpha))
            if borders:
                pg.draw.polygon(self.screen, black, [side[0], side[1], side[2], side[3]], 1)

    # ----------------------------------------- TRIANGLE ----------------------------------------------------------
    def render_triangle(self, triangle):
        point_list = []
        for point in triangle.points:
            point_list.append(self.flatten_point(point))
        return point_list

    def triangle_on_screen(self, triangle):
        pos = self.flatten_point(triangle.position)
        width = triangle.size[0]
        height = triangle.size[1]
        if not self.is_behind(triangle):
            if pos[0] > -width and pos[0] < self.width+width and pos[1] > -height and pos[1] < self.height+height:
                return True
        return False

    def draw_triangle(self, triangle_points, triangle, borders):
        pg.gfxdraw.filled_polygon(self.screen, [triangle_points[0], triangle_points[1], triangle_points[2]],
        (triangle.color[0],triangle.color[1],triangle.color[2],triangle.alpha))
        if borders:
            pg.draw.polygon(self.screen, black, [triangle_points[0], triangle_points[1], triangle_points[2]], 1)

    # ----------------------------------------- END ----------------------------------------------------------

    def draw(self, borders=False):
        draw_list = self.shapes.copy()
        draw_list.sort(key=lambda shape: self.distance(shape), reverse=True)

        for shape in draw_list:
            if shape.type() == 'Cube':
                point_list = self.render_cube(shape)
                if not self.cube_on_screen(shape):
                    continue
                self.draw_cube(point_list, shape, borders)

            if shape.type() == 'Triangle':
                point_list = self.render_triangle(shape)
                if not self.triangle_on_screen(shape):
                    continue
                self.draw_triangle(point_list, shape, borders)

    def draw_map(self, map_pos, map_size):
        ratio = [map_size[0]/self.width,map_size[1]/self.depth]
        def cam_to_map(pos):
            return (map_pos[0]+pos[0]*ratio[0],map_size[1]+map_pos[1]-pos[1]*ratio[1])
        def to_map(pos):
            return (map_pos[0]+pos[0]*ratio[0]+map_size[0]/2,map_pos[1]+map_size[1]-pos[1]*ratio[1])

        view = 800
        pg.draw.rect(self.screen, darkgrey, (map_pos[0], map_pos[1], map_size[0], map_size[1]))

        #self.screen.blit(self.font.render(str(self.camera.rotation[0]), False, black), (100,100))

        for shape in self.shapes:
            points = [
            to_map([shape.points[0][0],(shape.points[0][2]+shape.size[2]/2)-shape.size[2]/2]),
            to_map([shape.points[1][0],(shape.points[1][2]+shape.size[2]/2)-shape.size[2]/2]),
            to_map([shape.points[5][0],(shape.points[5][2]-shape.size[2]/2)+shape.size[2]/2]),
            to_map([shape.points[4][0],(shape.points[4][2]-shape.size[2]/2)+shape.size[2]/2])]
            pg.gfxdraw.filled_polygon(self.screen, points, (shape.color[0],shape.color[1],shape.color[2],shape.alpha))

        cam_pos = cam_to_map((self.camera.position[0],self.camera.position[2]))
        pg.draw.circle(self.screen, red, cam_pos, 5)

class Cube():
    def __init__(self, position, size, color, alpha=255):
        self.position = [position[0],position[1],position[2]]
        self.size = size

        self.points = [
        [self.position[0]-self.size[0]/2,self.position[1]-self.size[1]/2,self.position[2]-self.size[2]/2],
        [self.position[0]+self.size[0]/2,self.position[1]-self.size[1]/2,self.position[2]-self.size[2]/2],
        [self.position[0]+self.size[0]/2,self.position[1]+self.size[1]/2,self.position[2]-self.size[2]/2],
        [self.position[0]-self.size[0]/2,self.position[1]+self.size[1]/2,self.position[2]-self.size[2]/2],
        [self.position[0]-self.size[0]/2,self.position[1]-self.size[1]/2,self.position[2]+self.size[2]/2],
        [self.position[0]+self.size[0]/2,self.position[1]-self.size[1]/2,self.position[2]+self.size[2]/2],
        [self.position[0]+self.size[0]/2,self.position[1]+self.size[1]/2,self.position[2]+self.size[2]/2],
        [self.position[0]-self.size[0]/2,self.position[1]+self.size[1]/2,self.position[2]+self.size[2]/2]]

        self.color = color
        self.alpha = alpha

        self.sides = [
        [self.points[0], self.points[1], self.points[2], self.points[3]],   # front
        [self.points[4], self.points[5], self.points[6], self.points[7]],   # back
        [self.points[0], self.points[4], self.points[7], self.points[3]],   # right
        [self.points[5], self.points[1], self.points[2], self.points[6]],   # left
        [self.points[0], self.points[1], self.points[5], self.points[4]],   # up
        [self.points[7], self.points[6], self.points[2], self.points[3]]]   # down

    def get_sides(self, camera, width, height):
        sides = []
        if camera.position[1]-height/2 < self.position[1]:
            sides.append(4)
        if camera.position[1]-height/2 > self.position[1]:
            sides.append(5)
        if camera.position[0]-width/2 > self.position[0]:
            sides.append(3)
        if camera.position[0]-width/2 < self.position[0]:
            sides.append(2)
        if camera.position[2] < self.position[2]:
            sides.append(0)
        if camera.position[2] > self.position[2]:
            sides.append(1)
        return sides

    def type(self):
        return 'Cube'

    def __repr__(self):
        return 'Cube: ' + str(self.color) + ', ' + str(self.position)

class Triangle():
    def __init__(self, position, bb_size, points, color, alpha=255):
        self.position = [position[0],position[1],position[2]]
        self.points = points
        self.size = bb_size
        self.color = color
        self.alpha = alpha

        '''pg.draw.polygon(screen, (10,10,10), [
        ((margin + block_width) * column + margin, (margin + block_height) * row + margin),
        ((margin + block_width) * (column + 1) + margin, (margin + block_height) * row + margin),
        ((margin + block_width) * (column + 1) + margin, (margin + block_height) * (row + 1) + margin)])'''

    def type(self):
        return 'Triangle'

    def __repr__(self):
        return 'Triangle: ' + str(self.color) + ', ' + str(self.position)

class Camera():
    def __init__(self, pos=[0,0,0], rot=[0,0,0]):
        self.position = pos
        self.start_pos = pos.copy()
        self.rotation = rot
