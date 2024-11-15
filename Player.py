from pico2d import *

import UI
import game_framework
import game_world
from state_machine import *
from whip import Whip

WIDTH, HEIGHT = 1280, 720
# Player move Speed
PIXEL_PER_METER = (10.0/0.3)
RUN_SPEED_KMPH = 25.0
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

# Player Action Speed
TIME_PER_ACTION = 0.3
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 8

class Idle:
    @staticmethod
    def enter(player, e):
        if start_event(e):
            player.face_dir = 1
        elif right_down(e) or left_up(e):
            player.face_dir = -1
        elif left_down(e) or right_up(e):
            player.face_dir = 1

        player.action = 11
        player.frame = 0
        player.maxframe = 1

    @staticmethod
    def exit(player, e):
        if space_down(e):
            player.jump()

    @staticmethod
    def do(player):
        player.frame = (int(player.frame) +  FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % player.maxframe

    @staticmethod
    def draw(player):
        if player.face_dir == 1:
            player.image.clip_draw(int(player.frame),
                                   player.frame_height * player.action + 64,
                                   player.frame_width,
                                   player.frame_height,
                                   player.x,
                                   player.y, )
        else:
            player.image.clip_composite_draw(int(player.frame),
                                             player.frame_height * player.action + 64,
                                             player.frame_width,
                                             player.frame_height,
                                             0, 'h',
                                             player.x,
                                             player.y,
                                             80,
                                             80)



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
        player.frame = (int(player.frame) +  FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % player.maxframe


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
            player.dirx, player.face_dir, player.action = 1, 1, 1
        elif left_down(e) or right_up(e): # 왼쪽으로 RUN
            player.dirx, player.face_dir, player.action = -1, -1, 0

        player.action = 11
        player.frame = 0
        player.maxframe = 8

    @staticmethod
    def exit(player, e):
        if space_down(e):
            player.jump()

    @staticmethod
    def do(player):
        player.frame = (player.frame +  FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % player.maxframe
        player.x += player.dirx * RUN_SPEED_PPS * game_framework.frame_time


    @staticmethod
    def draw(player):
        if player.face_dir == 1:
            player.image.clip_draw(int(player.frame) * player.frame_width + player.frame_width,
                                   player.frame_height * player.action + 64,
                                   player.frame_width,
                                   player.frame_height,
                                   player.x,
                                   player.y, )
        else:
            player.image.clip_composite_draw(int(player.frame) * player.frame_width + player.frame_width,
                                             player.frame_height * player.action + 64,
                                             player.frame_width,
                                             player.frame_height,
                                             0, 'h',
                                             player.x,
                                             player.y,
                                             80,
                                             80)

class Crouch:
    @staticmethod
    def enter(player, e):
        if start_event(e):
            player.face_dir = 1
        elif right_down(e) or left_up(e):
            player.face_dir = -1
        elif left_down(e) or right_up(e):
            player.face_dir = 1

        player.action = 11
        player.frame = 0
        player.maxframe = 1

    @staticmethod
    def exit(player, e):
        if space_down(e):
            player.jump()

    @staticmethod
    def do(player):
        player.frame = (int(player.frame) +  FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % player.maxframe

    @staticmethod
    def draw(player):
        if player.face_dir == 1:
            player.image.clip_draw(int(player.frame),
                                   player.frame_height * player.action + 64,
                                   player.frame_width,
                                   player.frame_height,
                                   player.x,
                                   player.y, )
        else:
            player.image.clip_composite_draw(int(player.frame),
                                             player.frame_height * player.action + 64,
                                             player.frame_width,
                                             player.frame_height,
                                             0, 'h',
                                             player.x,
                                             player.y,
                                             80,
                                             80)
class Climb:
    @staticmethod
    def enter(player, e):
        if start_event(e):
            player.face_dir = 1
        elif right_down(e) or left_up(e):
            player.face_dir = -1
        elif left_down(e) or right_up(e):
            player.face_dir = 1

        player.action = 11
        player.frame = 0
        player.maxframe = 1

    @staticmethod
    def exit(player, e):
        if space_down(e):
            player.jump()

    @staticmethod
    def do(player):
        player.frame = (int(player.frame) +  FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % player.maxframe

    @staticmethod
    def draw(player):
        if player.face_dir == 1:
            player.image.clip_draw(int(player.frame),
                                   player.frame_height * player.action + 64,
                                   player.frame_width,
                                   player.frame_height,
                                   player.x,
                                   player.y, )
        else:
            player.image.clip_composite_draw(int(player.frame),
                                             player.frame_height * player.action + 64,
                                             player.frame_width,
                                             player.frame_height,
                                             0, 'h',
                                             player.x,
                                             player.y,
                                             80,
                                             80)
class Stunned:
    @staticmethod
    def enter(player, e):
        if start_event(e):
            player.face_dir = 1
        elif right_down(e) or left_up(e):
            player.face_dir = -1
        elif left_down(e) or right_up(e):
            player.face_dir = 1

        player.action = 11
        player.frame = 0
        player.maxframe = 1

    @staticmethod
    def exit(player, e):
        if space_down(e):
            player.jump()

    @staticmethod
    def do(player):
        player.frame = (int(player.frame) +  FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % player.maxframe

    @staticmethod
    def draw(player):
        if player.face_dir == 1:
            player.image.clip_draw(int(player.frame),
                                   player.frame_height * player.action + 64,
                                   player.frame_width,
                                   player.frame_height,
                                   player.x,
                                   player.y, )
        else:
            player.image.clip_composite_draw(int(player.frame),
                                             player.frame_height * player.action + 64,
                                             player.frame_width,
                                             player.frame_height,
                                             0, 'h',
                                             player.x,
                                             player.y,
                                             80,
                                             80)

class Dead:
    @staticmethod
    def enter(player, e):
        if start_event(e):
            player.face_dir = 1
        elif right_down(e) or left_up(e):
            player.face_dir = -1
        elif left_down(e) or right_up(e):
            player.face_dir = 1

        player.action = 11
        player.frame = 0
        player.maxframe = 1

    @staticmethod
    def exit(player, e):
        if space_down(e):
            player.jump()

    @staticmethod
    def do(player):
        player.frame = (int(player.frame) +  FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % player.maxframe

    @staticmethod
    def draw(player):
        if player.face_dir == 1:
            player.image.clip_draw(int(player.frame),
                                   player.frame_height * player.action + 64,
                                   player.frame_width,
                                   player.frame_height,
                                   player.x,
                                   player.y, )
        else:
            player.image.clip_composite_draw(int(player.frame),
                                             player.frame_height * player.action + 64,
                                             player.frame_width,
                                             player.frame_height,
                                             0, 'h',
                                             player.x,
                                             player.y,
                                             80,
                                             80)

class Jump:
    @staticmethod
    def enter(player, e):
        if start_event(e):
            player.face_dir = 1
        elif right_down(e) or left_up(e):
            player.face_dir = -1
        elif left_down(e) or right_up(e):
            player.face_dir = 1

        player.action = 11
        player.frame = 0
        player.maxframe = 1

    @staticmethod
    def exit(player, e):
        if space_down(e):
            player.jump()

    @staticmethod
    def do(player):
        player.frame = (int(player.frame) +  FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % player.maxframe

    @staticmethod
    def draw(player):
        if player.face_dir == 1:
            player.image.clip_draw(int(player.frame),
                                   player.frame_height * player.action + 64,
                                   player.frame_width,
                                   player.frame_height,
                                   player.x,
                                   player.y, )
        else:
            player.image.clip_composite_draw(int(player.frame),
                                             player.frame_height * player.action + 64,
                                             player.frame_width,
                                             player.frame_height,
                                             0, 'h',
                                             player.x,
                                             player.y,
                                             80,
                                             80)

class Attack:
    @staticmethod
    def enter(player, e):
        if start_event(e):
            player.face_dir = 1
        elif right_down(e) or left_up(e):
            player.face_dir = -1
        elif left_down(e) or right_up(e):
            player.face_dir = 1

        player.action = 11
        player.frame = 0
        player.maxframe = 1

    @staticmethod
    def exit(player, e):
        if space_down(e):
            player.jump()

    @staticmethod
    def do(player):
        player.frame = (int(player.frame) +  FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % player.maxframe

    @staticmethod
    def draw(player):
        if player.face_dir == 1:
            player.image.clip_draw(int(player.frame),
                                   player.frame_height * player.action + 64,
                                   player.frame_width,
                                   player.frame_height,
                                   player.x,
                                   player.y, )
        else:
            player.image.clip_composite_draw(int(player.frame),
                                             player.frame_height * player.action + 64,
                                             player.frame_width,
                                             player.frame_height,
                                             0, 'h',
                                             player.x,
                                             player.y,
                                             80,
                                             80)

class Player:
    image = None

    def load_image(self):
        if Player.image == None:
            Player.image = load_image('Sprite_Sheet.png')

    def __init__(self, x, y):
        self.ui = UI.UIP()
        self.state_machine = StateMachine(self)
        self.state_machine.start(Idle)
        self.state_machine.set_transitions(
            {
                Idle: {right_down: Run, left_down: Run, left_up: Run, right_up: Run, time_out: Sleep, space_down: Idle},
                Run: {right_down: Idle, left_down: Idle, right_up: Idle, left_up: Idle, space_down: Run},
                Sleep: {right_down: Run, left_down: Run, right_up: Run, left_up: Run, space_down: Idle}
            }
        )

        self.frame_width = 80
        self.frame_height = 80

        self.x, self.y = x, y    #생성 위치
        self.dirx, self.diry = 5, 5
        self.face_dir = 1
        self.frame = 0
        self.maxframe = 8
        self.action = 11
        self.load_image()

        self.hp = 4
        self.bomb = 4
        self.rope = 4
        self.gold = 0

    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()


        self.ui.draw(self.hp, self.bomb, self.rope)

    def handle_event(self, event):
        self.state_machine.handle_event(('INPUT', event))

    def whip(self):
        whip = Whip(self.x, self.y, self.face_dir * 10)
        game_world.add_object(whip)
        #if 파워팩 장착시 FireWhip 작동
    def handle_collusion(self, group, other):
        pass