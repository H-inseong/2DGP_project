from pico2d import *
import game_world
import game_framework

TIME_PER_ACTION = 1
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 3

class Bomb:
    image = None

    def __init__(self, x, y, velocity = 1):
        if Bomb.image == None:
            Bomb.image = load_image('items_sheet.png')
        self.x, self.y, self.velocity = x, y, velocity
        self.frame = 0

    def draw(self):
        self.image.clip_draw(128 * int(self.frame), 128 * 10, 128, 128, 50/128 * 100, 50/128 * 100)
        draw_rectangle(*self.get_bb())

    def update(self):
        self.x += self.velocity * 100 * game_framework.frame_time
        self.frame = (self.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % (3 + 1)
        if self.frame > 3:
            game_world.remove_object(self)
            #폭발 explosion()

    def get_bb(self):
        return self.x - 10, self.y - 10, self.x + 10, self.y + 10

    def handle_collision(self, group, other):
        pass