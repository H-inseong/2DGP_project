from pico2d import *

import game_world

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
            Tile.sprite_sheet.clip_draw_to_origin(self.f * 0, self.f * 11, self.f, self.f, screen_x, screen_y, 80, 80)
        elif self.tile_type == 'ladder':
            Tile.sprite_sheet.clip_draw_to_origin(self.f * 4, self.f * 10, self.f, self.f, screen_x, screen_y, 80, 80)
        elif self.tile_type == 'spike':
            Tile.sprite_sheet.clip_draw_to_origin(self.f * 5, self.f * 2, self.f, self.f, screen_x, screen_y, 80, 80)
        elif self.tile_type == 'rope_head':
            Tile.rope_sheet.clip_draw_to_origin(self.f * 11, 0, self.f, self.f, screen_x + 1, screen_y + 3, self.rt, self.rt)
        elif self.tile_type == 'rope':
            Tile.rope_sheet.clip_draw_to_origin(self.f * 5, 0, self.f, self.f, screen_x, screen_y, self.rt, self.rt)

        left, bottom, right, top = self.get_bb()
        draw_rectangle(left - camera_x, bottom - camera_y, right - camera_x, top - camera_y)

    def get_bb(self):
        # 충돌 박스 (bounding box) 정의
        if self.tile_type == 'spike':
            left = self.x * 80 + 20
            bottom = self.y * 80 + 20
            right = left + 50
            top = bottom + 50
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
            for x in range(width):
                for y in range(height):
                    tile_type = 'empty'
                    if x < 3 or y < 3 or x >= width - 3 or y >= height - 3:
                        tile_type = 'border'
                    self.tiles[(x, y)] = Tile(tile_type, x, y)
                    if self.tiles[(x,y)].tile_type == 'border':
                        game_world.add_object(self.tiles[(x, y)], 1)
                        continue
                    game_world.add_object(self.tiles[(x, y)], 0)  # 타일을 깊이 0에 추가

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
                game_world.add_collision_pair('items:Map', None, new_tile)

    def is_passable(self, x, y):
        if (x, y) in self.tiles:
            return self.tiles[(x, y)].passable
        return False
    def update(self):
        pass

    def save_map(self, filename):
        with open(filename, 'w') as file:
            for y in range(self.height):
                row = []
                for x in range(self.width):
                    tile = self.tiles[(x, y)]
                    row.append(tile.tile_type)
                file.write(','.join(row) + '\n')
        print(f"Map saved to {filename}")

    def load_map(self, filename):
        with open(filename, 'r') as file:
            lines = file.readlines()
            for y, line in enumerate(lines):
                tile_types = line.strip().split(',')
                for x, tile_type in enumerate(tile_types):
                    self.add_tile(tile_type, x, self.height - y - 1)  # 상단이 0,0 기준
        print(f"Map loaded from {filename}")

    def get_tile_type(self, x, y):
        tile_x, tile_y = int(x // 80), int(y // 80)
        if (tile_x, tile_y) in self.tiles:
            return self.tiles[(tile_x, tile_y)].tile_type
        return None  # 타일이 없을 경우