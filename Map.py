from pico2d import *

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
        self.rt = 5/8 * 100
        self.passable = self.tile_type not in ['solid', 'border']

    def draw(self, camera_x, camera_y):
        if self.tile_type == 'empty':
            Tile.sprite_sheet.clip_draw(self.f * 8, self.f * 6, self.f, self.f, (self.x * 80) - camera_x, (self.y * 80) - camera_y, self.rt, self.rt)
        elif self.tile_type == 'border':
            Tile.sprite_sheet.clip_draw(self.f * 7, self.f * 11, self.f, self.f, (self.x * 80) - camera_x, (self.y * 80) - camera_y, self.rt, self.rt)
        elif self.tile_type == 'solid':
            Tile.sprite_sheet.clip_draw(self.f * 8, self.f * 6, self.f, self.f, (self.x * 80) - camera_x, (self.y * 80) - camera_y, self.rt, self.rt)
        elif self.tile_type == 'ladder':
            Tile.sprite_sheet.clip_draw(self.f * 8, self.f * 6, self.f, self.f, (self.x * 80) - camera_x,(self.y * 80) - camera_y, self.rt, self.rt)
            Tile.sprite_sheet.clip_draw(self.f * 4, self.f * 10, self.f, self.f, (self.x * 80) - camera_x, (self.y * 80) - camera_y, self.rt, self.rt)
        elif self.tile_type == 'spike':
            Tile.sprite_sheet.clip_draw(self.f * 8, self.f * 6, self.f, self.f, (self.x * 80) - camera_x,(self.y * 80) - camera_y, self.rt, self.rt)
            Tile.sprite_sheet.clip_draw(self.f * 4, self.f * 10, self.f, self.f, (self.x * 80) - camera_x, (self.y * 80) - camera_y, self.rt, self.rt)
        elif self.tile_type == 'rope':
            Tile.sprite_sheet.clip_draw(self.f * 8, self.f * 6, self.f, self.f, (self.x * 80) - camera_x,(self.y * 80) - camera_y, self.rt, self.rt)
            Tile.rope_sheet.clip_draw(self.f * 5, 0, self.f, self.f, (self.x * 80) - camera_x, (self.y * 80) - camera_y, self.rt, self.rt)

    def get_bb(self):
        # 충돌 박스 (bounding box) 정의
        left = self.x * 80
        bottom = self.y * 80
        right = left + 80
        top = bottom + 80
        return left, bottom, right, top

    def handle_collision(self, group, other):
        # 타일 충돌 반응 폭발 구현
        pass


class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.tiles = {}
        for x in range(width):
            for y in range(height):
                self.tiles[(x, y)] = Tile('empty', x, y)

        for x in range(width):
            for y in range(height):
                if x < 3 or y < 3 or x >= width - 3 or y >= height - 3:
                    self.tiles[(x, y)] = Tile('border', x, y)

    def draw(self, camera_x, camera_y, screen_width, screen_height):
        start_x = max(camera_x // 80, 0)
        start_y = max(camera_y // 80, 0)
        end_x = min((camera_x + screen_width) // 80 + 1, self.width)
        end_y = min((camera_y + screen_height) // 80 + 1, self.height)

        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                self.tiles[(x, y)].draw(camera_x, camera_y)

    def add_tile(self, tile_type, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.tiles[(x, y)] = Tile(tile_type, x, y)

    def is_passable(self, x, y):
        if (x, y) in self.tiles:
            return self.tiles[(x, y)].passable
        return False