from tkinter.constants import SEL_FIRST

from pico2d import *
import game_world
import game_framework
from state_machine import landed

TIME_PER_ACTION = 1
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 3

class Rope:
    image = None
    def __init__(self, x, y, velocity = 1):
        if Rope.image == None:
            Rope.image = load_image('rope.png')
        self.x, self.y, self.velocity = x // 80 * 80, y // 80 * 80, velocity * 127
        self.frame = 0
        self.land = False

    def draw(self,vx, vy):
        self.image.clip_draw(128 * 10, 0, 128, 128, self.x - vx, self.y - vy ,80, 80)
        draw_rectangle(*self.get_bb())


    def update(self):
        self.y += self.velocity * game_framework.frame_time
        if self.velocity > 0:
            self.velocity = (abs(self.velocity) - 25 * game_framework.frame_time) * self.velocity / abs(self.velocity)
        else:
            self.velocity = 0


    def get_bb(self):
        return self.x - 20, self.y - 20, self.x + 20, self.y + 20

    def handle_collision(self, group, other):
        match(group):
            case('items:Map'):
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
            self.velocity = -self.velocity

        elif min_overlap == overlap_right:
            self.x += overlap_right
            self.velocity = -self.velocity

        elif min_overlap == overlap_bottom:
            self.y -= overlap_bottom
            self.land = True

        elif min_overlap == overlap_top:
            self.y += overlap_top
