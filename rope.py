from pico2d import *
import game_world
import game_framework
import play_mode
from state_machine import landed

TIME_PER_ACTION = 1
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 3

class Rope:
    image = None
    def __init__(self, x, y):
        if Rope.image == None:
            Rope.image = load_image('rope.png')
            Rope.initsound = load_wav('ropetoss.wav')
            Rope.endsound = load_wav('ropecatch.wav')
        self.x, self.y= x // 80 * 80 + 40, y // 80 * 80
        self. velocity = 1000
        self.frame = 0
        self.land = False
        self.max_height = self.y // 80 + 7
        Rope.initsound.set_volume(64)
        Rope.initsound.play()
        game_world.add_object(self)
        game_world.add_collision_pair('Item:Map', self, None)

    def draw(self,vx, vy):
        self.image.clip_draw(128 * 10, 0, 128, 128, self.x - vx, self.y - vy ,80, 80)
        draw_rectangle(*self.get_bb())

    def update(self):
        global map_obj
        self.y += self.velocity * game_framework.frame_time

        tile_x = int(self.x // 80)
        tile_y = int(self.y // 80)

        if tile_y >= self.max_height:
            play_mode.create_rope(self, tile_x, tile_y)
            Rope.endsound.set_volume(64)
            Rope.endsound.play()
            game_world.remove_object(self)

    def get_bb(self):
        return self.x - 10, self.y , self.x + 10, self.y + 40

    def handle_collision(self, group, other):
        match(group):
            case('Item:Map'):
                if other.tile_type in ['solid', 'border']:
                    self.resolve_collision(other)

    def resolve_collision(self, tile):
        item_bb = self.get_bb()
        tile_bb = tile.get_bb()

        overlap_left = item_bb[2] - tile_bb[0]
        overlap_right = tile_bb[2] - item_bb[0]
        overlap_bottom = item_bb[3] - tile_bb[1]
        overlap_top = tile_bb[3] - item_bb[1]

        min_overlap = min(overlap_left, overlap_right, overlap_bottom, overlap_top)

        if min_overlap == overlap_left:
            self.x -= overlap_left


        elif min_overlap == overlap_right:
            self.x += overlap_right

        elif min_overlap == overlap_bottom:
            self.y -= overlap_bottom
            play_mode.create_rope(self, int(self.x // 80), int(self.y // 80) )
            Rope.endsound.set_volume(64)
            Rope.endsound.play()
            game_world.remove_object(self)

        elif min_overlap == overlap_top:
            self.y += overlap_top
