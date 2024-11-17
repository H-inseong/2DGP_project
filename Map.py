from pico2d import *

class Tile:
    sprite_sheet = None
    sprite_sheet = None
    def __init__(self, tile_type, x, y):
        if Tile.sprite_sheet is None:
            Tile.sprite_sheet = load_image('background_main.png')

        self.tile_type = tile_type  # 'empty', 'solid', 'ladder', etc.
        self.x = x
        self.y = y
        self.f = 128
        self.rt = 5/8
        self.passable = self.tile_type not in ['solid', 'spike']

    def draw(self, camera_x, camera_y):
        if self.tile_type == 'empty':
            Tile.sprite_sheet.clip_draw(self.f * 8, self.f * 6, self.f, self.f, (self.x * 80) - camera_x, (self.y * 80) - camera_y)
        elif self.tile_type == 'border':
            Tile.sprite_sheet.clip_draw(self.f * 7, self.f * 11, self.f, self.f, (self.x * 80) - camera_x, (self.y * 80) - camera_y)
        elif self.tile_type == 'solid':
            Tile.sprite_sheet.clip_draw(self.f * 8, self.f * 6, self.f, self.f, (self.x * 80) - camera_x, (self.y * 80) - camera_y)
        elif self.tile_type == 'ladder':
            Tile.sprite_sheet.clip_draw(self.f * 4, self.f * 10, self.f, self.f, (self.x * 80) - camera_x, (self.y * 80) - camera_y)


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