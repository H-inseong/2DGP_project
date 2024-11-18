from pico2d import *

import game_framework
import game_world

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 6.0

class Whip:
    image = None
    def __init__(self, x, y):
        if Whip.image == None:
            Whip.image = load_image('whip.png')
        self.x, self.y = x, y
        self.frame = 0
        self.active = False
        self.aa = False

    def draw(self, x, y):
        if self.direction == 1:
            if int(self.frame) == 3:
                Whip.image.clip_draw(int(self.frame) * 128, 0, 128, 128,
                                     self.x - 60 - (6 - int(self.frame) * 15) + x, self.y + 40 + y, 60, 60)
            else:
                Whip.image.clip_draw(int(self.frame) * 128, 0, 128, 128,
                                 self.x - 60 - (6 - int(self.frame) * 15)+ x, self.y+ y, 60, 60)
        else:
            if int(self.frame) == 3:
                Whip.image.clip_composite_draw(int(self.frame) * 128, 0, 128, 128, 0, 'h',
                                     self.x + 60 + (6 - int(self.frame) * 15) + x,self.y + 40+ y, 60, 60)
            else:
                Whip.image.clip_composite_draw(int(self.frame) * 128, 0, 128, 128, 0, 'h',
                                           self.x + 60 + (6 - int(self.frame) * 15) + x,self.y+ y, 60, 60)
        if int(self.frame) == 5:
            aa = True
        draw_rectangle(*self.get_bb())

    def update(self, player_x, player_y, player_direction):
        if self.active:
            self.frame = (self.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 6
        if int(self.frame) == 0 and self.aa:
            self.active = False
        self.direction = player_direction
        self.x = player_x + (40 * player_direction)  # Offset by direction to position in front of player
        self.y = player_y - 10

    def get_bb(self):
        if self.active:
            if int(self.frame) in [0, 1, 2]:
                return self.x - 100 - (6 - int(self.frame) * 15), self.y + 50, self.x + 15, self.y + 15
            else:
                return self.x - 25, self.y - 10, self.x + 25, self.y + 10
        return None

    def activate(self):
        self.active = True
        self.frame = 0
        self.aa = False

    def handle_collision(self, group, other):
        pass