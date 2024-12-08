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
        self.direction = 1

        game_world.add_collision_pair('Whip:Monster', self, None)
        game_world.add_collision_pair('Whip:Item', self, None)

    def draw(self, x, y):
        if self.direction == 1:
            if int(self.frame) < 2:
                Whip.image.clip_draw(int(self.frame) * 128, 0, 128, 128,
                                        self.x - (6 - int(self.frame)) * 15 - x , self.y + 30 - y, 60, 60)
            else:
                Whip.image.clip_draw(int(self.frame) * 128, 0, 128, 128,
                                        self.x + 20 - (6 - int(self.frame)) * 15 - x, self.y - y, 60, 60)
        else:

            if int(self.frame) < 2:
                Whip.image.clip_composite_draw(int(self.frame) * 128, 0, 128, 128, 0, 'h',
                                        self.x + (6 - int(self.frame)) * 15 - x,self.y + 30 - y, 60, 60)
            else:
                Whip.image.clip_composite_draw(int(self.frame) * 128, 0, 128, 128, 0, 'h',
                                        self.x - 20 + (6 - int(self.frame)) * 15 - x, self.y - y, 60, 60)
        bb = self.get_bb()
        draw_rectangle(bb[0], bb[1], bb[2], bb[3])

    def update(self, x, y, dr):
        if self.active:
            self.frame = (self.frame + 6 * ACTION_PER_TIME * game_framework.frame_time) % (6 + 1)
        if self.frame > 6:
            self.active = False
        self.direction = dr
        self.x = x + (40 * dr)
        self.y = y - 10

    def get_bb(self):
        if self.active:
            if self.direction == 1:
                if int(self.frame) in [0, 1, 2]:
                    left = self.x - 20 - (6 - int(self.frame)) * 15
                    bottom = self.y + 15
                    right = self.x - 15
                    top = self.y + 50
                else:
                    left = self.x - 25
                    bottom = self.y - 10
                    right = self.x + 40
                    top = self.y + 20
            elif self.direction == -1:
                if int(self.frame) in [0, 1, 2]:
                    left = self.x
                    bottom = self.y + 15
                    right = self.x + 160 - (6 - int(self.frame)) * 15
                    top = self.y + 50
                else:
                    left = self.x - 40
                    bottom = self.y - 10
                    right = self.x + 25
                    top = self.y + 20
            return left, bottom, right, top
        return 0, 0, 0, 0

    def activate(self):
        from Player import Player
        Player.whip_sound.set_volume(32)
        Player.whip_sound.play()
        self.active = True
        self.frame = 0
        self.aa = False

    def handle_collision(self, group, other):
        pass