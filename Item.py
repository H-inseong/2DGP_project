from pico2d import *

import game_framework
import game_world
import play_mode
from random import choice

GRAVITY = -777

class Item:
    image = None
    def __init__(self, x, y, x_i, y_i):
        if Item.image == None:
            Item.image = load_image('items_sheet.png')
        self.x, self.y = x * 80, y * 80
        self.dx, self.dy = 0, 0
        self.x_index, self.y_index = x_i, y_i
        game_world.add_object(self)
        game_world.add_collision_pair('Items:Map', self, None)

        match (x_i, y_i):
            case ( 14, 15):
                self.name = 'Gold Bar'
                self.value = 1
                self.take = 1
                game_world.add_collision_pair('Player:Item', None, self)
            case ( 15, 15):
                self.name = 'Gold Bars'
                self.value = 3
                self.take = 1
                game_world.add_collision_pair('Player:Item', None, self)
            case ( 0, 13):
                self.name = 'bomb'
                self.value = 2
                self.take = 1
                game_world.add_collision_pair('Player:Item', None, self)
            case ( 1, 13):
                self.name = 'bombs'
                self.value = 4
                self.take = 1
                game_world.add_collision_pair('Player:Item', None, self)
            case ( 0, 9):
                self.name = 'rope'
                self.value = 2
                self.take = 1
                game_world.add_collision_pair('Player:Item', None, self)
            case ( 6, 13):
                self.name = 'spike shoes'
                self.value = 1
                self.take = 1
                game_world.add_collision_pair('Player:Item', None, self)
            case ( 0, 15):
                self.name = 'chest'
                self.take = 0
                game_world.add_collision_pair('Whip:Item', None, self)
            case ( 2, 15):
                self.name = 'item_box'
                self.take = 0
                game_world.add_collision_pair('Whip:Item', None, self)


    def draw(self,camera_x, camera_y):
        Item.image.clip_draw_to_origin(128 * self.x_index, 128 * self.y_index, 128, 128, self.x - camera_x, self.y - camera_y, 80, 80)



    def update(self):
        down_tile_type = play_mode.map_obj.get_tile_type(self.x, self.y - 1)
        if down_tile_type in ['border', 'solid']:
            pass
        else:
            self.y += GRAVITY * game_framework.frame_time



    def get_bb(self):
        return self.x - 40, self.y - 40, self.x + 40, self.y + 40



    def handle_collision(self, group, other):
        if group == 'Player:Item':
            if self.take == 1:
                game_world.remove_object(self)


        if group == 'Whip:Item' and self.name == 'chest':
            possible_items = [
                (14, 15),  # Gold Bar
                (15, 15),  # Gold Bars
            ]

            item_type = choice(possible_items)
            Item(self.x, self.y, *item_type)
            game_world.remove_object(self)


        if group == 'Whip:Item' and self.name == 'item_box':
            possible_items = [
                (0, 13),  # Bomb
                (1, 13),  # Bombs
                (0, 9),  # Rope
                (6, 13),  # Spike Shoes
            ]
            item_type = choice(possible_items)
            Item(self.x, self.y, *item_type)