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
            Tile.sprite_sheet.clip_draw(self.f * 8, self.f * 6, self.f, self.f, screen_x, screen_y, self.rt, self.rt)
        elif self.tile_type == 'border':
            Tile.sprite_sheet.clip_draw(self.f * 7, self.f * 11, self.f, self.f, screen_x, screen_y, self.rt, self.rt)
        elif self.tile_type == 'solid':
            Tile.sprite_sheet.clip_draw(self.f * 0, self.f * 11, self.f, self.f, screen_x, screen_y, self.rt, self.rt)
        elif self.tile_type == 'ladder':
            Tile.sprite_sheet.clip_draw(self.f * 8, self.f * 6, self.f, self.f, screen_x, screen_y, self.rt, self.rt)
            Tile.sprite_sheet.clip_draw(self.f * 4, self.f * 10, self.f, self.f, screen_x, screen_y, 80, 80)
        elif self.tile_type == 'spike':
            Tile.sprite_sheet.clip_draw(self.f * 8, self.f * 6, self.f, self.f, screen_x, screen_y, self.rt, self.rt)
            Tile.sprite_sheet.clip_draw(self.f * 5, self.f * 2, self.f, self.f, screen_x, screen_y, 80, 80)
        elif self.tile_type == 'rope_head':
            Tile.sprite_sheet.clip_draw(self.f * 8, self.f * 6, self.f, self.f, screen_x, screen_y, self.rt, self.rt)
            Tile.rope_sheet.clip_draw(self.f * 11, 0, self.f, self.f, screen_x + 1, screen_y + 3, self.rt, self.rt)
        elif self.tile_type == 'rope':
            Tile.sprite_sheet.clip_draw(self.f * 8, self.f * 6, self.f, self.f, screen_x, screen_y, self.rt, self.rt)
            Tile.rope_sheet.clip_draw(self.f * 5, 0, self.f, self.f, screen_x, screen_y, self.rt, self.rt)


    def get_bb(self):
        # 충돌 박스 (bounding box) 정의
        left = self.x * 80 - 40
        bottom = self.y * 80 - 40
        right = left + 80
        top = bottom + 80
        return left, bottom, right, top

    def handle_collision(self, group, other):
        # 타일 충돌 반응 폭발 구현
        pass

    def update(self):
        pass


class Map:
    def __init__(self, width, height):
            self.width = width
            self.height = height

            self.tiles = {}
            for x in range(width):
                for y in range(height):
                    tile_type = 'empty'
                    if x < 3 or y < 3 or x >= width - 3 or y >= height - 3:
                        tile_type = 'border'
                    self.tiles[(x, y)] = Tile(tile_type, x, y)
                    game_world.add_object(self.tiles[(x, y)], 0)  # 타일을 깊이 0에 추가

    def draw(self, camera_x=0, camera_y=0):
        start_x = int(max(camera_x // 80, 0))
        start_y = int(max(camera_y // 80, 0))
        end_x = int(min((camera_x + screen_width) // 80 + 1, self.width))
        end_y = int(min((camera_y + screen_height) // 80 + 1, self.height))

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
