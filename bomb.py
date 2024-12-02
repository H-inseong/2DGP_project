from tkinter.constants import SEL_FIRST

from pico2d import *
from pygame.draw_py import draw_pixel

import game_world
import game_framework
import play_mode
from state_machine import landed

TIME_PER_ACTION = 2
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 3
GRAVITY = -300
class Bomb:
    image = None
    def __init__(self, x, y, velocity = 1):
        if Bomb.image == None:
            Bomb.image = load_image('items_sheet.png')
            Bomb.initsound = load_wav('throw_item.wav')
            Bomb.timer = load_wav('bomb_timer.wav')
            Bomb.endsound = load_wav('shotgun.wav')
        self.x, self.y, self.velocity = x, y, velocity * 120
        self.frame = 0
        self.land = False
        Bomb.initsound.set_volume(64)
        Bomb.initsound.play()
        Bomb.timer.set_volume(64)
        Bomb.timer.play()

    def draw(self,vx, vy):
        self.image.clip_draw(128 * int(self.frame), 128 * 10, 128, 128, self.x - vx, self.y - vy ,80, 80)

    def update(self):
        self.x += self.velocity * game_framework.frame_time
        if self.velocity != 0:
            self.velocity = (abs(self.velocity) - 25) * self.velocity / abs(self.velocity)
        if not self.land:
            self.y += GRAVITY * game_framework.frame_time

        self.frame = (self.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % (3 + 1)
        if self.frame > 3:
            play_mode.explosive(self.x // 80, self.y // 80)
            Bomb.endsound.set_volume(64)
            Bomb.endsound.play()
            game_world.remove_object(self)

    def get_bb(self):
        return self.x - 20, self.y - 20, self.x + 20, self.y + 20

    def handle_collision(self, group, other):
        match(group):
            case('Item:Map'):
                if other.tile_type in ['solid', 'border']:
                    self.resolve_collision(other)

    def resolve_collision(self, tile):
        player_bb = self.get_bb()
        tile_bb = tile.get_bb()

        overlap_left = player_bb[2] - tile_bb[0]
        overlap_right = tile_bb[2] - player_bb[0]
        overlap_bottom = player_bb[3] - tile_bb[1]
        overlap_top = tile_bb[3] - player_bb[1]

        min_overlap = min(overlap_left, overlap_right, overlap_bottom, overlap_top)

        if min_overlap == overlap_left:
            self.x -= overlap_left
            self.velocity = -self.velocity/2

        elif min_overlap == overlap_right:
            self.x += overlap_right
            self.velocity = -self.velocity/2

        elif min_overlap == overlap_bottom:
            self.y -= overlap_bottom
            self.land = True

        elif min_overlap == overlap_top:
            self.y += overlap_top
