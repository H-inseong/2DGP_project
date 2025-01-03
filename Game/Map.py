from random import randint


from pico2d import *

import game_world
import play_mode
from Item import Item
from enemies import Snake, gSnake, Boss

screen_width = 1920
screen_height = 960

class Tile:
    rope_sheet = None
    sprite_sheet = None
    def __init__(self, tile_type, x, y):
        if Tile.sprite_sheet is None:
            Tile.sprite_sheet = load_image('background_main.png')
            Tile.ex_sheet = load_image('background_extrashape.png')
            Tile.wood_sheet = load_image('background_woods.png')
            Tile.rope_sheet = load_image('rope.png')
            Tile.bkb = load_wav('crushblock.wav')
            Tile.bkb.set_volume(64)
        if tile_type in 'solid':
            self.solid_num = randint(1,3)
        self.tile_type = tile_type
        self.x = x
        self.y = y
        self.f = 128
        self.rt = 95
        self.passable = self.tile_type not in ['solid', 'border']

    def draw(self, camera_x=0, camera_y=0):
        screen_x = (self.x * 80) - camera_x
        screen_y = (self.y * 80) - camera_y

        if self.tile_type == 'empty':
            pass
        elif self.tile_type == 'border':
            Tile.sprite_sheet.clip_draw_to_origin(self.f * 7, self.f * 11, self.f, self.f, screen_x, screen_y, self.rt, self.rt)
        elif self.tile_type == 'solid':
            match(self.solid_num):
                case (1):
                    Tile.sprite_sheet.clip_draw_to_origin(self.f * 0, self.f * 11,
                                                          self.f, self.f, screen_x, screen_y, 80, 80)
                case (2):
                    Tile.sprite_sheet.clip_draw_to_origin(self.f * 1, self.f * 11,
                                                          self.f, self.f, screen_x, screen_y, 80, 80)
                case (3):
                    Tile.sprite_sheet.clip_draw_to_origin(self.f * 0, self.f * 7,
                                                          self.f, self.f, screen_x, screen_y, 80, 80)
        elif self.tile_type == 'ladder':
            Tile.sprite_sheet.clip_draw_to_origin(self.f * 4, self.f * 10, self.f, self.f, screen_x, screen_y, 80, 80)
        elif self.tile_type == 'spike':
            Tile.sprite_sheet.clip_draw_to_origin(self.f * 5, self.f * 2, self.f, self.f, screen_x, screen_y, 80, 80)
        elif self.tile_type == 'rope_head':
            Tile.rope_sheet.clip_draw_to_origin(self.f * 11, 0, self.f, self.f, screen_x, screen_y, self.rt, self.rt)
        elif self.tile_type == 'rope':
            Tile.rope_sheet.clip_draw_to_origin(self.f * 5, 0, self.f, self.f, screen_x - 1, screen_y, self.rt, self.rt)
        elif self.tile_type == 'start':
            Tile.sprite_sheet.clip_draw_to_origin(43, 380, 300, 240, screen_x, screen_y, 160, 160)
        elif self.tile_type == 'end':
            Tile.sprite_sheet.clip_draw_to_origin(43, 80, 300, 240, screen_x, screen_y, 160, 160)

    def get_bb(self):
        # 충돌 박스 (bounding box) 정의
        if self.tile_type == 'spike':
            left = self.x * 80 + 20
            bottom = self.y * 80 + 20
            right = left + 50
            top = bottom + 50

        elif self.tile_type in [ 'start', 'end']:
            left = self.x * 80
            bottom = self.y * 80
            right = left + 160
            top = bottom + 160

        else:
            left = self.x * 80
            bottom = self.y * 80
            right = left + 80
            top = bottom + 80
        return left, bottom, right, top

    def handle_collision(self, group, other):
        pass

    def update(self):
        pass


class Map:
    def __init__(self, width, height):
            self.width = width
            self.height = height
            self.image = load_image('background_main.png')
            self.tiles = {}

    def draw(self, camera_x=0, camera_y=0):
        start_x = int(max(camera_x // 80, 0))
        start_y = int(max(camera_y // 80, 0))
        end_x = int(min((camera_x + screen_width) // 80 + 1, self.width))
        end_y = int(min((camera_y + screen_height) // 80 + 1, self.height))

        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                screen_x = (x * 80) - camera_x
                screen_y = (y * 80) - camera_y
                self.image.clip_draw_to_origin(128 * 8, 128 * 6, 128, 128, screen_x, screen_y, 95, 95)

        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                self.tiles[(x, y)].draw(camera_x, camera_y)


    def add_tile(self, tile_type, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            current_tile = self.tiles.get((x, y))
            game_world.remove_object(current_tile)


            new_tile = Tile(tile_type, x, y)
            self.tiles[(x, y)] = new_tile
            game_world.add_object(new_tile, 0)

            if tile_type != 'empty':
                game_world.add_collision_pair('Player:Map', None, new_tile)
                game_world.add_collision_pair('Item:Map', None, new_tile)
                game_world.add_collision_pair('Monster:Map', None, new_tile)


    def is_passable(self, x, y):
        if (x, y) in self.tiles:
            return self.tiles[(x, y)].passable
        return False
    def update(self):
        pass

    def save_map(self, filename):
        with open(filename, 'w') as file:
            for y in reversed(range(self.height)):  # Reverse the Y-axis
                row = [self.tiles[(x, y)].tile_type for x in range(self.width)]
                file.write(','.join(row) + '\n')
        print(f"Map saved to {filename}")

    def load_map(self, filename):
        for layer in game_world.world:
            for obj in layer[:]:  # 리스트 복사로 안전하게 순회
                if isinstance(obj, Tile):
                    game_world.remove_object(obj)
        try:
            with open(filename, 'r') as file:
                lines = file.readlines()
        except FileNotFoundError:
            print(f"Error: {filename} not found.")
            return
        except Exception as e:
            print(f"Error reading file {filename}: {e}")
            return

        for y, line in enumerate(reversed(lines)):  # 파일의 첫 줄이 맵의 상단
            tile_types = line.strip().split(',')
            for x, tile_type in enumerate(tile_types):

                if tile_type == 'item':
                    self.add_tile('empty', x, y)
                    Item(x, y, 2, 15)
                elif tile_type == 'crate':
                    self.add_tile('empty', x, y)
                    Item(x, y, 0, 15)
                elif tile_type == 's':
                    self.add_tile('empty', x, y)
                    Snake(x, y)
                elif tile_type == 'gs':
                    self.add_tile('empty', x, y)
                    gSnake(x, y)
                elif tile_type == 'boss':
                    self.add_tile('empty', x, y)
                    Boss(x,y)
                elif tile_type == 'start':
                    self.add_tile('start', x, y)
                    play_mode.player.x = 80 * x + 70
                    play_mode.player.y = 80 * y + 80
                else:
                    self.add_tile(tile_type, x, y)
        game_world.add_collision_pair('Player:Map', play_mode.player, None)
        game_world.add_collision_pair('Player:Item', play_mode.player, None)
        game_world.add_collision_pair('Player:Monster', play_mode.player, None)
        game_world.add_collision_pair('Whip:Monster', play_mode.player.whip, None)
        game_world.add_collision_pair('Whip:Item', play_mode.player.whip, None)

    def get_tile_type(self, x, y):
        tile_x, tile_y = int(x // 80), int(y // 80)
        if (tile_x, tile_y) in self.tiles:
            return self.tiles[(tile_x, tile_y)].tile_type
        return None

    def get_tile_position(self, tile_type):
        for (x, y), tile in self.tiles.items():
            if tile.tile_type == tile_type:
                return x * 80 + 40, y * 80 + 40  # 타일의 중심 좌표
        return None

    def get_tile_coords(self, cx, cy):
        tile_x = int(cx // 80)
        tile_y = int(cy // 80)
        return tile_x, tile_y

    def break_tile(self, tile_x, tile_y):
        if (tile_x, tile_y) in self.tiles:
            current_tile = self.tiles[(tile_x, tile_y)]
            if current_tile is not None:
                game_world.remove_object(current_tile)
            self.tiles[(tile_x, tile_y)] = None
            self.add_tile('empty', tile_x, tile_y)
            Tile.bkb.play()