from pico2d import *

import UI
import game_framework
import game_world
from Map import Tile
from state_machine import *
from whip import Whip
from bomb import Bomb

WIDTH, HEIGHT = 1920, 960
# Player move Speed
PIXEL_PER_METER = (10.0/0.3)
RUN_SPEED_KMPH = 28.0
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

# Player Action Speed
TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 8

DEBUG = True

GRAVITY = -300

class Player:
    image = None
    sec_image = None
    def load_image(self):
        if Player.image is None:
            Player.image = load_image('Sprite_Sheet.png')
        if Player.sec_image is None:
            Player.sec_image = load_image('boss.png')

    def __init__(self, x, y):
        self.ui = UI.UIP()
        self.state_machine = StateMachine(self)
        self.state_machine.start(Idle)
        self.state_machine.set_transitions(
            {
                Idle: {right_down: Run, left_down: Run, left_up: Run, right_up: Run,
                       space_down: Jump, down_down: Crouch, up_down: ClimbMove,
                       z_down: Attack},
                Run: {right_down: Run, left_down: Run, right_up: Idle, left_up: Idle, space_down: Jump, down_down: CrouchMove, z_down: Attack},
                Crouch: {down_up: Idle, left_down: CrouchMove, right_down:CrouchMove, down_down: Crouch, z_down: Attack, space_down: Jump},
                CrouchMove : {left_up: Crouch, right_up:Crouch, left_down: CrouchMove, right_down:CrouchMove, down_up: Run},
                Climb: {up_up: Climb, up_down: ClimbMove, down_up: Climb, down_down: ClimbMove, z_down: Idle},
                ClimbMove: {up_up: Climb, up_down: ClimbMove, down_up:Climb, down_down: ClimbMove},
                Stunned: { time_out: Idle },
                Attack: { right_up: Attack, left_up: Attack, right_down: Attack, left_down: Attack, space_down: Jump, time_out: Idle},
                Jump: { right_down: Jump, left_down: Jump }
            }
        )
        #f = frame
        self.f_w = 80
        self.f_h = 80

        self.x, self.y = x, y    #생성 위치
        self.dirx, self.diry = 0, 0
        self.dx, self.dy = 0, 0
        self.face_dir = 1
        self.frame = 0
        self.maxframe = 8
        self.act = 11
        self.load_image()
        self.view_x = 0
        self.view_y = 0
        self.whip = Whip(self.x, self.y)

        self.hp = 4
        self.bomb = 4
        self.rope = 4
        self.gold = 0

        self.aa = False
        self.ladder = False
        self.jumped = False
        self.land = True

        self.velocity_y = 0  # 초기 수직 속도

    def update(self):
        if not self.land:
            self.velocity_y += GRAVITY * game_framework.frame_time
            self.y += self.velocity_y * game_framework.frame_time

        self.state_machine.update()

        if self.x < 1920 // 2:
            self.view_x = 0
        elif self.x > 3440 - (1920 // 2):
            self.view_x = 3440 - 1920
        else:
            self.view_x = self.x - (1920 // 2)

        if self.y < 960 // 2:
            self.view_y = 0
        elif self.y > 3040 - (960 // 2):
            self.view_y = 3040 - 960
        else:
            self.view_y = self.y - (960 // 2)

    def draw(self, a,b):
        self.state_machine.draw()
        self.ui.draw(self.hp, self.bomb, self.rope, self.gold)
        if DEBUG:
            bb = self.get_bb()
            draw_rectangle(bb[0] - self.view_x, bb[1] - self.view_y, bb[2] - self.view_x, bb[3] - self.view_y)

    def handle_event(self, event):
        self.state_machine.handle_event(('INPUT', event))

    def handle_collision(self, group, other):
        if group == 'Player:Map':
            if isinstance(other, Tile):
                if other.tile_type in ['solid', 'border']:
                    self.resolve_collision(other)
                elif other.tile_type == 'spike':
                    if self.dy < 0:
                        self.hp =  0
                        self.state_machine.start(Dead)
                elif other.tile_type == 'ladder':
                    self.ladder = True
        elif group == 'Player:Item':
            match (other.name):
                case('Gold Bar'):
                    self.gold += other.value
                case ('Gold Bars'):
                    self.gold += other.value
                case ('bomb'):
                    self.bomb += other.value
                case ('bombs'):
                    self.bomb += other.value
                case ('rope'):
                    self.gold += other.value
                case ('spike shoes'):
                    self.gold += other.value
                case ('spring shoes'):
                    self.bomb += other.value
                case ('arrow'):
                    if other.dx != 0:
                        self.hp -= 1
        elif group == 'Player:Monster':
            self.hp -= 1

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
        elif min_overlap == overlap_right:
            self.x += overlap_right
        elif min_overlap == overlap_bottom:
            self.y -= overlap_bottom
            self.diry = 0  # 수직 속도 중지
            self.jumped = False  # 다시 점프 가능하도록 설정
            self.land = True
            self.velocity_y = 0
            self.state_machine.add_event(('TIME_OUT', 0))  # Idle 또는 Run 상태로 전환
        elif min_overlap == overlap_top:
            self.y += overlap_top
            self.diry = 0  # 상승 속도 중지

    def get_bb(self):
        if self.state_machine.cur_state == Crouch or self.state_machine.cur_state == CrouchMove:
            return self.x - 30, self.y - 33, self.x + 30, self.y
        if self.state_machine.cur_state == Stunned:
            return self.x - 30, self.y - 33, self.x + 30, self.y

        return self.x - 30, self.y - 33, self.x + 30, self.y + 30

    def bomb(self):
        if self.bomb > 0:
            self.bomb -= 1
            bomb = Bomb(self.x, self.y, self.face_dir * 10)
            game_world.add_object(bomb)
            game_world.add_collision_pair('items:Map', None, bomb)


class Idle:
    @staticmethod
    def enter(player, e):
        if start_event(e):
            player.face_dir = 1
        elif right_down(e) or left_up(e):
            player.face_dir = -1
        elif left_down(e) or right_up(e):
            player.face_dir = 1

        player.act = 11
        player.frame = 0
        player.maxframe = 1

    @staticmethod
    def exit(player, e):
        pass

    @staticmethod
    def do(player):
        player.frame = (
                                   int(player.frame) + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % player.maxframe

    @staticmethod
    def draw(player):
        if player.face_dir == 1:
            player.image.clip_draw(int(player.frame),
                                   player.f_h * player.act + 64,
                                   player.f_w,
                                   player.f_h,
                                   player.x - player.view_x,
                                   player.y - player.view_y, )
        else:
            player.image.clip_composite_draw(int(player.frame) * player.f_w,
                                             player.f_h * player.act + 64,
                                             player.f_w,
                                             player.f_h,
                                             0, 'h',
                                             player.x - player.view_x,
                                             player.y - player.view_y,
                                             80,
                                             80)


class Run:
    @staticmethod
    def enter(player, e):
        if right_down(e) or left_up(e):  # 오른쪽으로 RUN
            player.dirx, player.face_dir = 1, 1
        elif left_down(e) or right_up(e):  # 왼쪽으로 RUN
            player.dirx, player.face_dir = -1, -1

        player.act = 11
        player.frame = 0
        player.maxframe = 8
        if player.dirx == 0:
            player.state_machine.start(Idle)

    @staticmethod
    def exit(player, e):
        pass

    @staticmethod
    def do(player):
        player.frame = (
                                   player.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % player.maxframe
        player.x += player.dirx * RUN_SPEED_PPS * game_framework.frame_time

    @staticmethod
    def draw(player):
        if player.face_dir == 1:
            player.image.clip_draw(int(player.frame) * player.f_w + player.f_w,
                                   player.f_h * player.act + 64,
                                   player.f_w,
                                   player.f_h,
                                   player.x - player.view_x,
                                   player.y - player.view_y, )
        else:
            player.image.clip_composite_draw(int(player.frame) * player.f_w + player.f_w,
                                             player.f_h * player.act + 64,
                                             player.f_w,
                                             player.f_h,
                                             0, 'h',
                                             player.x - player.view_x,
                                             player.y - player.view_y,
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

        player.act = 10
        if player.frame != 2:
            player.frame = 0
        player.maxframe = 2
        player.c_time = get_time()

    @staticmethod
    def exit(player, e):
        pass

    @staticmethod
    def do(player):
        if player.frame != 2:
            player.frame = (player.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % (
                        player.maxframe + 1)
            if player.frame > 2:
                player.frame = 2
        if get_time() - player.c_time > 3:
            player.state_machine.add_event(('TIME_OUT', 0))
            player.view_y -= 50
            # 시야가 아래로 이동

    @staticmethod
    def draw(player):
        if player.face_dir == 1:
            player.image.clip_draw(int(player.frame) * player.f_w,
                                   player.f_h * player.act + 64,
                                   player.f_w,
                                   player.f_h,
                                   player.x - player.view_x,
                                   player.y - player.view_y, )
        else:
            player.image.clip_composite_draw(int(player.frame) * player.f_w,
                                             player.f_h * player.act + 64,
                                             player.f_w,
                                             player.f_h,
                                             0, 'h',
                                             player.x - player.view_x,
                                             player.y - player.view_y,
                                             80,
                                             80)


class CrouchMove:
    @staticmethod
    def enter(player, e):
        if right_down(e) or left_up(e):
            player.dirx, player.face_dir, player.act = 0.5, 1, 1
        elif left_down(e) or right_up(e):
            player.dirx, player.face_dir, player.act = -0.5, -1, 0

        player.act = 10
        player.frame = 0
        player.maxframe = 7

    @staticmethod
    def exit(player, e):
        player.dirx = 0
        player.frame = 2
        if down_up(e):
            player.dirx = 1 * player.face_dir

    @staticmethod
    def do(player):
        player.frame = (
                                   player.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % player.maxframe
        player.x += player.dirx * RUN_SPEED_PPS * game_framework.frame_time

    @staticmethod
    def draw(player):
        if player.face_dir == 1:
            player.image.clip_draw(int(player.frame) * player.f_w + player.f_w * 5,
                                   player.f_h * player.act + 64,
                                   player.f_w,
                                   player.f_h,
                                   player.x - player.view_x,
                                   player.y - player.view_y, )
        else:
            player.image.clip_composite_draw(int(player.frame) * player.f_w + player.f_w * 5,
                                             player.f_h * player.act + 64,
                                             player.f_w,
                                             player.f_h,
                                             0, 'h',
                                             player.x - player.view_x,
                                             player.y - player.view_y,
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
        # 플레이어가 사다리에 있을 때
        player.act = 3
        player.frame = 0
        player.maxframe = 4
        player.up_time = get_time()

    @staticmethod
    def exit(player, e):
        pass

    @staticmethod
    def do(player):
        player.frame = (
                                   player.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % player.maxframe
        if get_time() - player.up_time > 3:
            player.state_machine.add_event(('TIME_OUT', 0))

    @staticmethod
    def draw(player):
        player.image.clip_draw(int(player.frame) * player.f_w,
                               player.f_h * player.act + 64,
                               player.f_w,
                               player.f_h,
                               player.x - player.view_x,
                               player.y - player.view_y, )


class ClimbMove:
    @staticmethod
    def enter(player, e):
        if up_down(e) or down_up(e):
            player.diry = 1
        elif down_down(e) or up_up(e):
            player.diry = -1

        player.act = 4
        player.frame = 0
        player.maxframe = 10

    @staticmethod
    def exit(player, e):
        player.diry = 0

    @staticmethod
    def do(player):
        player.frame = (
                                   player.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % player.maxframe
        player.y += player.diry * RUN_SPEED_PPS * game_framework.frame_time

    @staticmethod
    def draw(player):
        player.image.clip_draw(int(player.frame) * player.f_w,
                               player.f_h * player.act + 64,
                               player.f_w,
                               player.f_h,
                               player.x - player.view_x,
                               player.y - player.view_y, )


class Stunned:
    @staticmethod
    def enter(player, e):
        player.act = 9
        player.frame = 0
        player.maxframe = 12
        player.st_time = get_time()

    @staticmethod
    def exit(player, e):
        if space_down(e):
            player.jump()

    @staticmethod
    def do(player):
        player.frame = (
                                   player.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % player.maxframe

        if get_time() - player.st_time > 5:
            player.state_machine.add_event(('TIME_OUT', 0))

    @staticmethod
    def draw(player):
        if player.face_dir == 1:
            if player.dx > 0:
                player.image.clip_draw(0,
                                       player.f_h * player.act + 64,
                                       player.f_w,
                                       player.f_h,
                                       player.x - player.view_x,
                                       player.y - player.view_y, )
            elif player.dx < 0:
                player.image.clip_draw(0 + player.f_w,
                                       player.f_w * player.act + 64,
                                       player.f_w,
                                       player.f_w,
                                       player.x - player.view_x,
                                       player.y - player.view_y, )
            elif player.dx == 0:
                player.image.clip_draw(player.f_w * 3,
                                       player.f_h * player.act + 64,
                                       player.f_w,
                                       player.f_h,
                                       player.x - player.view_x,
                                       player.y - player.view_y)
        else:
            if player.dx > 0:
                player.image.clip_composite_draw(0,
                                                 player.f_h * player.act + 64,
                                                 player.f_w,
                                                 player.f_h,
                                                 0, 'h',
                                                 player.x - player.view_x,
                                                 player.y - player.view_y,
                                                 80,
                                                 80)
            elif player.dx < 0:
                player.image.clip_composite_draw(0 + player.f_w,
                                                 player.f_h * player.act + 64,
                                                 player.f_w,
                                                 player.f_h,
                                                 0, 'h',
                                                 player.x - player.view_x,
                                                 player.y - player.view_y,
                                                 80,
                                                 80)
            elif player.dx == 0:
                player.image.clip_composite_draw(0 + player.f_w * 3,
                                                 player.f_h * player.act + 64,
                                                 player.f_w,
                                                 player.f_h,
                                                 0, 'h',
                                                 player.x - player.view_x,
                                                 player.y - player.view_y,
                                                 80,
                                                 80)

        player.sec_image.clip_draw(int(player.frame) * player.f_w,
                                   128 * 2,
                                   128,
                                   128,
                                   player.x - player.view_x,
                                   player.y - player.view_y,
                                   50,
                                   50)


class Dead:
    @staticmethod
    def enter(player, e):
        player.act = 9
        player.frame = 0
        player.maxframe = 12
        player.st_time = get_time()

    @staticmethod
    def exit(player, e):
        pass

    @staticmethod
    def do(player):
        player.frame = (
                                   player.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % player.maxframe

        if get_time() - player.st_time > 5:
            game_framework.quit()  # 게임 종료 또는 다른 동작 수행

    @staticmethod
    def draw(player):
        if player.face_dir == 1:
            if player.dx > 0:
                player.image.clip_draw(0,
                                       player.f_h * player.act + 64,
                                       player.f_w,
                                       player.f_h,
                                       player.x - player.view_x,
                                       player.y - player.view_y, )
            elif player.dx < 0:
                player.image.clip_draw(0 + player.f_w,
                                       player.f_w * player.act + 64,
                                       player.f_w,
                                       player.f_w,
                                       player.x - player.view_x,
                                       player.y - player.view_y, )
            elif player.dx == 0:
                player.image.clip_draw(player.f_w * 3,
                                       player.f_h * player.act + 64,
                                       player.f_w,
                                       player.f_h,
                                       player.x - player.view_x,
                                       player.y - player.view_y, )
        else:
            if player.dx > 0:
                player.image.clip_composite_draw(0,
                                                 player.f_h * player.act + 64,
                                                 player.f_w,
                                                 player.f_h,
                                                 0, 'h',
                                                 player.x - player.view_x,
                                                 player.y - player.view_y,
                                                 80,
                                                 80)
            elif player.dx < 0:
                player.image.clip_composite_draw(0 + player.f_w,
                                                 player.f_h * player.act + 64,
                                                 player.f_w,
                                                 player.f_h,
                                                 0, 'h',
                                                 player.x - player.view_x,
                                                 player.y - player.view_y,
                                                 80,
                                                 80)
            elif player.dx == 0:
                player.image.clip_composite_draw(0 + player.f_w * 3,
                                                 player.f_h * player.act + 64,
                                                 player.f_w,
                                                 player.f_h,
                                                 0, 'h',
                                                 player.x - player.view_x,
                                                 player.y - player.view_y,
                                                 80,
                                                 80)

    class Jump:
        @staticmethod
        def enter(player, e):
            if not player.jumped:
                player.velocity_y = 800  # 점프 초기 속도 (픽셀/초)
                player.jumped = True
                player.land = False

            player.act = 2
            player.maxframe = 7
            player.frame = 0

        @staticmethod
        def exit(player, e):
            pass

        @staticmethod
        def do(player):
            player.frame = (player.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % (player.maxframe + 1)
            if player.frame > 7:
                player.frame = 7

            # y 위치는 Player.update에서 이미 처리됨
            # 수직 속도는 Player.update에서 중력에 의해 업데이트됨

        @staticmethod
        def draw(player):
            if player.face_dir == 1:
                player.image.clip_draw(int(player.frame) * player.f_w,
                                       player.f_h * player.act + 64,
                                       player.f_w,
                                       player.f_h,
                                       player.x - player.view_x,
                                       player.y - player.view_y, )
            else:
                player.image.clip_composite_draw(int(player.frame) * player.f_w,
                                                 player.f_w * player.act + 64,
                                                 player.f_w,
                                                 player.f_w,
                                                 0, 'h',
                                                 player.x - player.view_x,
                                                 player.y - player.view_y,
                                                 80,
                                                 80)
class Jump:
        @staticmethod
        def enter(player, e):
            if not player.jumped:
                player.velocity_y = 800  # 점프 초기 속도 (픽셀/초)
                player.jumped = True
                player.land = False

            player.act = 2
            player.maxframe = 7
            player.frame = 0

        @staticmethod
        def exit(player, e):
            pass

        @staticmethod
        def do(player):
            player.frame = (player.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % (player.maxframe + 1)
            if player.frame > 7:
                player.frame = 7

            # y 위치는 Player.update에서 이미 처리됨
            # 수직 속도는 Player.update에서 중력에 의해 업데이트됨

        @staticmethod
        def draw(player):
            if player.face_dir == 1:
                player.image.clip_draw(int(player.frame) * player.f_w,
                                       player.f_h * player.act + 64,
                                       player.f_w,
                                       player.f_h,
                                       player.x - player.view_x,
                                       player.y - player.view_y, )
            else:
                player.image.clip_composite_draw(int(player.frame) * player.f_w,
                                                 player.f_w * player.act + 64,
                                                 player.f_w,
                                                 player.f_w,
                                                 0, 'h',
                                                 player.x - player.view_x,
                                                 player.y - player.view_y,
                                                 80,
                                                 80)

class Attack:
    @staticmethod
    def enter(player, e):
        if right_down(e):  # 오른쪽으로 RUN
            player.dirx, player.face_dir = 1, 1
        elif left_down(e):  # 왼쪽으로 RUN
            player.dirx, player.face_dir = -1, -1
        elif right_up(e):
            player.dirx = 0
        elif left_up(e):
            player.dirx = 0

        player.act = 7
        if not player.whip.active:
            player.frame = 0
        player.maxframe = 6
        player.whip.activate()
        player.whip.update(player.x, player.y, player.face_dir)
        player.aa = False

        if space_down(e) and not player.jumped:
            player.velocity_y = 800  # 점프 초기 속도
            player.jumped = True
            player.land = False

    @staticmethod
    def exit(player, e):
        pass

    @staticmethod
    def do(player):
        player.x += player.dirx * RUN_SPEED_PPS * game_framework.frame_time
        player.frame = (player.frame + 6 * ACTION_PER_TIME * game_framework.frame_time) % player.maxframe
        player.whip.update(player.x, player.y, player.face_dir)
        if int(player.frame) == 0 and player.aa:
            player.state_machine.add_event(('TIME_OUT', 0))

    @staticmethod
    def draw(player):
        player.whip.draw(player.view_x, player.view_y)
        if player.face_dir == 1:
            player.image.clip_draw(int(player.frame) * player.f_w,
                                   player.f_h * player.act + 64,
                                   player.f_w,
                                   player.f_h,
                                   player.x - player.view_x,
                                   player.y - player.view_y, )
        else:
            player.image.clip_composite_draw(int(player.frame) * player.f_w,
                                             player.f_w * player.act + 64,
                                             player.f_w,
                                             player.f_w,
                                             0, 'h',
                                             player.x - player.view_x,
                                             player.y - player.view_y,
                                             80,
                                             80)
        if int(player.frame) == 5:
            player.aa = True
