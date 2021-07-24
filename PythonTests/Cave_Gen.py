import pygame
import random
from math import sin, cos, floor, ceil
import os
import sys
import json
import zipfile

pygame.init()
win = pygame.display.set_mode((1920,1080)) #1400,861

block_size = 8 #block dimensions in px

pygame.display.set_caption("Conway's Game of Life")
run = True

def lerp(a, b, w):
    #return a + (b-a)*w
    return (b - a) * (3.0 - w * 2.0) * w * w + a
    #return (b - a) * ((w * (w * 6.0 - 15.0) + 10.0) * w * w * w) + a

class vec2d:
    def __init__(self, x, y):
        self.x, self.y = x, y

class perlin1d:
    def __init__(self, seed = None):
        self.seed = None
        if seed:
            self.seed = seed
        else:
            self.seed = random.randint(0, 2**32)
    
    def random_gradient(self, ix):
        random = 2920 * sin(ix * 21942 + self.seed * 171324 + 8912) * cos(ix * 23157 * self.seed * 217832 + 9758) * self.seed
        return sin(random)
    
    def get(self, x):
        x0 = int(x)
        x1 = x0 + 1
        w = x - x0
        return lerp(self.random_gradient(x0) * w, -self.random_gradient(x1) *w, w)/2+0.5

class perlin2d:
    def __init__(self, seed = None):
        self.seed = None
        if seed:
            self.seed = seed
        else:
            self.seed = random.randint(0, 2**32)

    def random_gradient(self, ix, iy):
        #random = 2920 * sin(ix * 21942 + iy * 171324 + 8912) * cos(ix * 23157 * iy * 217832 + 9758) * self.seed
        random = ((ix+0x1928d1)*(iy-0x23f012)) ^ (self.seed+2341010473)
        #random = ix*438932 << 38 + iy << 52 | self.seed
        return vec2d(cos(random), sin(random))

    def dot_gradients(self, ix, iy, x, y):
        gradient = self.random_gradient(ix, iy)
        dx = x - ix
        dy = y - iy

        return (gradient.x * dx + gradient.y * dy)
    
    def get(self, x, y):
        x0 = floor(x)
        x1 = x0 + 1
        y0 = floor(y)
        y1 = y0 + 1

        d1 = self.dot_gradients(x0, y0, x, y)
        d2 = self.dot_gradients(x1, y0, x, y)
        d3 = self.dot_gradients(x0, y1, x, y)
        d4 = self.dot_gradients(x1, y1, x, y)

        wx = x - x0
        wy = y - y0

        return lerp(lerp(d1, d2, wx), lerp(d3, d4, wx), wy)

    def get_l(self, x, y, octaves = 1):
        out = 0
        for i in range(octaves):
            out += self.get(x*i+x, y*i+y)/(2**i)
        out /= 2-0.5**(octaves-1)
        return out

class Block:
    tex_dict = {}
    def __init__(self, type):
        self.data = {"type":type, "appearance":0}
    @staticmethod
    def add_tex(Type, tex_hash, tex):
        if not Type in Block.tex_dict:
            Block.tex_dict[Type] = {}
        Block.tex_dict[Type][tex_hash] = tex
    def set_appearance(self, tex_hash):
        pass
    def get_tex(self):
        if self.data["type"] in Block.tex_dict:
            return Block.tex_dict[self.data["type"]][self.data["appearance"]]
        else:
            return None
class Game:
    def __init__(self,size,seed = 0):
        self.dir = os.path.dirname(os.path.realpath(__file__))
        self.stitch_textures()
        self.render_chunks = dict()
        self.font = pygame.font.SysFont("Arial", 32)
        self.clock = pygame.time.Clock()
        
        self.columns,self.rows = size
        self.column_chunks, self.row_chunks = self.columns//16, self.rows//16
        self.chunk_size_px = 16*block_size
        if seed == 0:
            self.seed = random.randint(0,2**32-1) #4213017313 is a good seed; 685186833 too
        else:
            self.seed = seed
        print(self.seed)
        
        self.connecting_noise2 = perlin2d(self.seed)
        self.blob_noise2 = perlin2d(2**32-self.seed-1)
        self.massif_noise2 = perlin2d(self.seed^0x8f1062d4)
        self.cave_translation_map = perlin2d(2**32-self.seed^0x8f1062d4-1)

        self.map = {}
        for x in range(11):
            self.new_chunk(x-5)

    def new_chunk(self,x):
        #new version
        #connecting caves
        passage_noise_cellsize = 112

        path_size = 0.0125

        path_value = 0.5

        path_value_shift = 0.0

        value_shift_start = 128

        value_shift_end = 736

        growth_rate = 0.008

        growth_start = 192

        growth_end = 288
        #giant caves
        cave_threshold = 0

        cave_growth = 0.46 #.46

        cave_growth_start = 228#448

        cave_growth_length = 64

        cave_noise_cellsize = 128#256

        #rock massifs
        massif_cellsize = 256

        #translation
        translation_cellsize = 8

        #passage_map = [[((self.connecting_noise2.get(.5*(16*x+columns)/self.noise_cell_size, 1*rows/self.noise_cell_size)/2 + 0.5 + self.connecting_noise2.get(1*(16*x+columns)/self.noise_cell_size, 2*rows/self.noise_cell_size)/4 + 0.25 + self.connecting_noise2.get(2*(16*x+columns)/self.noise_cell_size, 4*rows/self.noise_cell_size)/8 + 0.125)/1.75)  for rows in range(self.rows)] for columns in range(16)]
        #passage_map = [[self.connecting_noise2.get_l(0.5*(16*x +columns)/passage_noise_cellsize, rows/passage_noise_cellsize,3)/2 + 0.5  for rows in range(self.rows)] for columns in range(16)]
        #map_giant_caves = [[(self.blob_noise2.get_l(1 * (16 * x + columns) / cave_noise_cellsize, 1 * rows / cave_noise_cellsize, 3) / 2 + 0.5) for rows in range(self.rows)] for columns in range(16)] #*3.5 - 1*(1 - abs(passage_map[columns][rows] - path_value - path_value_shift * min(max((rows-value_shift_start)/(value_shift_end-value_shift_start),0),1)))
        #massif_map = [[((self.massif_noise2.get((16*x+columns)/massif_cellsize, rows/massif_cellsize)/2 + 0.5 + self.massif_noise2.get((16*x+columns)/massif_cellsize, rows/massif_cellsize)/4 + 0.25 + self.massif_noise2.get((16*x+columns)/massif_cellsize, rows/massif_cellsize)/8 + 0.125)/1.75)  for rows in range(self.rows)] for columns in range(16)]

        self.map[x] = [[None for row in range(self.rows)] for column in range(16)]
        for column in range(16):
            for row in range(self.rows):
                #if self.map[column][row] > min(0.42 + 0.06 * 2 * row/150, 0.48): #0.48:#0.42 + 0.06 * row/self.rows: #0.48:
                if (self.blob_noise2.get_l((16*x+column+self.cave_translation_map.get_l((16*x+column)/translation_cellsize, row/translation_cellsize, 1)*10)/cave_noise_cellsize, row/cave_noise_cellsize, 3)/2+0.5 < (cave_threshold + cave_growth*min(1,max(0, (row-cave_growth_start)/cave_growth_length)))*min(1, max(0,(682-row)/(100)))) or abs(self.connecting_noise2.get_l((8*x+column/2+self.cave_translation_map.get_l((16*x+column)/translation_cellsize, row/translation_cellsize, 1)*5)/passage_noise_cellsize, row/passage_noise_cellsize,3)/2+0.5 - path_value) < (1-min(max(0,self.massif_noise2.get((16*x+column)/massif_cellsize,row/massif_cellsize)-0.51)*20, 1))*(path_size + growth_rate*min(max((row-growth_start)/(growth_end-growth_start),0),1))*min(1, max(0,(732-row)/(50))): #8*x + column / 2 instead of 16*x + column because of the passage noise moving twice as fast in y direction
                    self.map[x][column][row] = Block("air")
                else:
                    self.map[x][column][row] = Block("stone") 

        for column in range(16):
            for row in range(self.rows):
                neighbours = self.neighbours_number(x*16+column, row)
                if neighbours < 1:
                    self.map[x][column][row] = Block("air")
                if neighbours > 6 and self.map[x][column][row].data["type"] == "air":
                    self.map[x][column][row] = Block("stone")

        for column in range(16):
            for row in range(100):
                if row + self.blob_noise2.get_l((16*x+column)/12, row/12, 4)*40 < 50 + self.massif_noise2.get_l((16*x+column)/8, 829, 3) * 10:
                    self.map[x][column][self.rows-1-row] = Block("void stone")

        for cy in range(self.row_chunks):
            self.update_render_chunk(x, cy)

        self.new_map = []
    def neighbours_number(self, x, y):
        if self.map[floor(x/16)][x%16][y].data["type"] != "air":
            number = -1
        else:
            number = 0
        for c in range(3):
            for r in range(3):
                if y+r-1 < self.rows:
                    chunk = floor((x+c-1)/16)
                    if chunk in self.map:
                        if self.map[chunk][(x+c-1)%16][y+r-1].data["type"] != "air":
                            number += 1
        return number

    def stitch_textures(self):
        with open(self.dir + os.sep + "block_data.json", "r") as file:
            data = json.load(file)
            for block_type in data["types"]:
                archive = zipfile.ZipFile(self.dir + os.sep + "Textures" + os.sep + block_type + ".zip")
                n = 0
                for appearance in archive.namelist():
                    Block.add_tex(block_type, n, pygame.image.load(archive.open(appearance)).convert_alpha())
                    n += 1

    def update_display(self):
        global block_size, win, scroll
        
        self.clock.tick()

        render = pygame.surface.Surface((win.get_width()/(block_size/16), win.get_height()/(block_size/16)))

        win.fill((0,0,0))
        
        c_off_x, c_off_y = floor((scroll[0]*16-render.get_width()/2)/256), floor((scroll[1]*16-render.get_height()/2)/256)
        
        px_off_x, px_off_y = scroll[0]*16 - c_off_x*256 - render.get_width()/2, scroll[1]*16 - c_off_y*256 - render.get_height()/2
        
        for c in range(ceil(render.get_width()/256)+1):
            for r in range(ceil(render.get_height()/256)+1):
                if (c_off_x + c, c_off_y + r) in self.render_chunks:
                    render.blit(self.render_chunks[(c_off_x + c, c_off_y + r)], (256 * c -px_off_x,  256 * r - px_off_y))

        win.blit(pygame.transform.scale(render, win.get_size()), (0,0))
        win.blit(self.font.render(str(floor(self.clock.get_fps())), True, (255,255,255)), (30,30))
    
    def update_render_chunk(self, cx, cy):
        rendered = pygame.surface.Surface((256, 256)).convert_alpha()
        rendered.fill((0,0,0,0))
        for x in range(16):
            for y in range(16):
                block = self.map[cx][x][cy*16+y] 
                if not block.data["type"] == "air":
                    rendered.blit(block.get_tex(), (x*16, y*16))
        self.render_chunks[(cx,cy)] = rendered.copy()

c = 0
m = [0,0,False,False]
scroll = [0.0,0.0]
game = Game((1024,832))#, 2681094141)

last_m = [0,0]
drag = False

world_start = -5
world_end = 5

while run:
    win.fill((0,0,0))
    
    last_m = m
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if pygame.key.get_pressed()[pygame.K_n]:
                game = Game((160, 64))
                c = 0
            if pygame.key.get_pressed()[pygame.K_1]:
                block_size = 16
                game.chunk_size_px = 256
            if pygame.key.get_pressed()[pygame.K_2]:
                block_size = 32
                game.chunk_size_px = 512
            if pygame.key.get_pressed()[pygame.K_3]:
                block_size = 48
                game.chunk_size_px = 768
            
        if event.type == pygame.MOUSEMOTION:
            m = pygame.mouse.get_pos()
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            drag = True
            
        if event.type == pygame.MOUSEBUTTONUP:
            drag = False
    scroll[0] -= ((m[0] - last_m[0])/block_size) * int(drag)
    scroll[1] -= ((m[1] - last_m[1])/block_size) * int(drag)

    if scroll[0] > (world_end-1) * 16:
        game.new_chunk(world_end+1)
        world_end += 1
    if scroll[0] < (world_start+1) * 16:
        game.new_chunk(world_start-1)
        world_start -= 1

    game.update_display()
    
    fadeout = min(1,max(0,(scroll[1]-712)/100))
    surf = pygame.surface.Surface((1920,1080))
    surf.set_alpha(round(fadeout*235))
    #win.blit(surf, (0,0))
    pygame.draw.rect(win, (255, 0, 200), (m[0]- 60, m[1]-34, 120, 68), 1)
    pygame.display.flip()

pygame.quit()