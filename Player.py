from pico2d import load_image, get_time
from sdl2 import SDL_QUIT, SDL_KEYDOWN, SDLK_RIGHT, SDLK_LEFT, SDLK_UP, SDLK_DOWN, SDLK_ESCAPE, SDL_KEYUP

import game_framework
import game_world
from MOVEMENT_BASE import WIDTH, HEIGHT
from state_machine import *
from whip import Whip

# Player move Speed
PIXEL_PER_METER = (10.0/0.3)
RUN_SPEED_KMPH = 20.0
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

# Player Action Speed
TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 8

class Idle:
    @staticmethod
    def enter(player, e):
        if start_event(e):
            player.action = 3
            player.face_dir = 1
        elif right_down(e) or left_up(e):
            player.action = 2
            player.face_dir = -1
        elif left_down(e) or right_up(e):
            player.action = 3
            player.face_dir = 1

        player.frame = 0
        player.wait_time = get_time()

    @staticmethod
    def exit(player, e):
        if space_down(e):
            player.jump()

    @staticmethod
    def do(player):
        player.frame = (player.frame +  FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) & 8
        if get_time() - player.wait_time > 2:
            player.state_machine.add_event(('TIME_OUT', 0))

    @staticmethod
    def draw(player):
        player.image.clip_draw(int(player.frame) * 100, player.action * 100, 100, 100, player.x, player.y)



class Sleep:
    @staticmethod
    def enter(player, e):
        if start_event(e):
            player.face_dir = 1
            player.action = 3
            player.frame = 0

    @staticmethod
    def exit(player, e):
        pass

    @staticmethod
    def do(player):
        player.frame = (player.frame +  FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) & 8


    @staticmethod
    def draw(player):
        if player.face_dir == 1:
            player.image.clip_composite_draw(int(player.frame) * 100, 300, 100, 100,
                                          3.141592 / 2, '', player.x - 25, player.y - 25, 100, 100)
        else:
            player.image.clip_composite_draw(int(player.frame) * 100, 200, 100, 100,
                                          -3.141592 / 2, '', player.x + 25, player.y - 25, 100, 100)


class Run:
    @staticmethod
    def enter(player, e):
        if right_down(e) or left_up(e): # 오른쪽으로 RUN
            player.dir, player.face_dir, player.action = 1, 1, 1
        elif left_down(e) or right_up(e): # 왼쪽으로 RUN
            player.dir, player.face_dir, player.action = -1, -1, 0

    @staticmethod
    def exit(player, e):
        if space_down(e):
            player.jump()


    @staticmethod
    def do(player):
        player.frame = (player.frame +  FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) & 8
        player.x += player.dir * 5


    @staticmethod
    def draw(player):
        player.image.clip_draw(int(player.frame) * 100, player.action * 100, 100, 100, player.x, player.y)



class Player:
    def __init__(self):
        self.state_machine = StateMachine(self)
        self.state_machine.start()
        
        self.x, self.y = WIDTH // 2, HEIGHT // 2
        self.dirx, self.diry = 0, 0
        self.face_dir = 1
        self.frame = 0
        self.action = 0
        self.image = load_image('Sprite_Sheet.png')
        self.frame_width = 80
        self.frame_height = 80
        self.frame_y = 80

        #hp와 item 등을 여기서 관리하는게 맞는가?
        self.hp = 4
        self.item = [4, 4, 0] # bomb, rope, gold

    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()

    def handle_event(self, event):
        self.state_machine.handle_event(('INPUT', event))

    def whip(self):
        whip = Whip(self.x, self.y, self.face_dir * 10)
        game_world.add_object(whip)
        #if 파워팩 장착시 FireWhip 작동

    def 