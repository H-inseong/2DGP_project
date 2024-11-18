from pico2d import *

import game_framework
import game_world

class Item:
    image = None
    def __init__(self, x, y, x_i, y_i):
        if Item.image == None:
            Item.image = load_image('items_sheet.png')
        self.x, self.y = x, y
        self.dx, self.dy = 0, 0
        self.x_index, self.y_index = x_i, y_i

        match (x_i, y_i):
            case ( 14, 15):
                self.name = 'Gold Bar'
                self.value = 1
                self.take = 1
            case ( 14, 15):
                self.name = 'Gold Bars'
                self.value = 3
                self.take = 1
            case ( 0, 13):
                self.name = 'bomb'
                self.value = 2
                self.take = 1
            case ( 1, 13):
                self.name = 'bombs'
                self.value = 4
                self.take = 1
            case ( 0, 9):
                self.name = 'rope'
                self.value = 2
                self.take = 1
            case ( 6, 13):
                self.name = 'spike shoes'
                self.value = 1
                self.take = 1
            case ( 7, 13):
                self.name = 'spring shoes'
                self.value = 1
                self.take = 1
            case ( 1, 14):
                self.name = 'arrow'
                self.dx = 1
                self.value = 1
                self.take = 0

    def draw(self):
        Item.image.clip_draw(128 * self.x_index, 128 * self.y_index, 128, 128, self.x, self.y, 5/8 * 100, 5/8 * 100)
        draw_rectangle(*self.get_bb())

    def update(self, player_x, player_y, player_direction):
        self.x = self.dx * 100 * game_framework.frame_time

    def get_bb(self):
        return self.x - 40, self.y + 40, self.x + 40, self.y + 40

    def handle_collusion(self, group, other):
        pass