import random
import math
import game_framework
import game_world

from pico2d import *

# zombie Run Speed
PIXEL_PER_METER = (10.0 / 0.3)  # 10 pixel 30 cm
RUN_SPEED_KMPH = 10.0  # Km / Hour
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

# zombie Action Speed
TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 10.0

class Snake:
    image = None

    def load_images(self):
        if Snake.image == None:
            Snake.image = load_image('Snakes.png')
    def __init__(self, color):
        self.x, self.y = random.randint(1600-800, 1600), 240
        self.load_images()
        self.f_size = 80
        self.frame = 0
        self.color = color  # 0 : blue  1 : green
        self.dir = random.choice([-1,1])
        self.attack = False


    def update(self):
        self.frame = (self.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % FRAMES_PER_ACTION
        self.x += RUN_SPEED_PPS * self.dir * game_framework.frame_time

        #Map 충돌체크 추가
        if self.x > 1600:
            self.dir = -1
        elif self.x < 800:
            self.dir = 1
        self.x = clamp(800, self.x, 1600)
        pass


    def draw(self, x, y):
        if self.dir < 0:
            Snake.image.clip_composite_draw(int(self.frame) * self.f_size, self.f_size * self.color + self.f_size + 28, self.f_size, self.f_size, 0, 'h', self.x - x, self.y - y, 80, 80)
        else:
            Snake.image.clip_composite_draw(int(self.frame) * self.f_size, self.f_size * self.color + self.f_size + 28, self.f_size, self.f_size, 0, 'h', self.x - x, self.y - y, 80, 80)
        draw_rectangle(*self.get_bb())

    def handle_event(self, event):
        pass

    def handle_collision(self, group, other):
        if group == 'Whip:Monster':
            game_world.remove_object(self)


    def get_bb(self):
        return self.x - self.f_size/2 , self.y - self.f_size/2 , self.x + self.f_size/2 , self.y + self.f_size/2

class Boss:
    images = None

    def load_images(self):
        if Boss.image == None:
            Boss.image = load_image('boss.png')

    def __init__(self, color):
        self.x, self.y = random.randint(1600 - 800, 1600), 150
        self.load_images()
        self.f_size = 128
        self.frame = 0
        self.color = color  # 0 : blue  1 : green
        self.dir = random.choice([-1, 1])
        self.attack = False

    def update(self):
        self.frame = (self.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % FRAMES_PER_ACTION
        self.x += RUN_SPEED_PPS * self.dir * game_framework.frame_time

        # Map 충돌체크 추가
        if self.x > 1600:
            self.dir = -1
        elif self.x < 800:
            self.dir = 1
        self.x = clamp(800, self.x, 1600)
        pass

    def draw(self):
        if self.dir < 0:
            Snake.images.clip_composite_draw(int(self.frame) * self.f_size, self.f_size * self.color + self.size, 'h',
                                             self.x, self.y, 80, 80)
        else:
            Snake.images.clip_composite_draw(int(self.frame) * self.f_size, self.f_size * self.color + self.size, 'h',
                                             self.x, self.y, 80, 80)

        draw_rectangle(*self.get_bb())

    def handle_event(self, event):
        pass

    def handle_collision(self, group, other):
        pass

    def get_bb(self):
        return self.x - self.f_size / 2, self.y - self.f_size / 2, self.x + self.f_size / 2, self.y + self.f_size / 2
