from sys import platlibdir

from pico2d import *
from pygame.examples.chimp import load_sound

import UI
import game_framework
import game_world
import play_mode
from Item import Item
from Map import Tile
from rope import Rope
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

GRAVITY = -777

class Player:
    image = None
    sec_image = None
    sound = None

    def load_image(self):
        if Player.image is None:
            Player.image = load_image('Sprite_Sheet.png')
        if Player.sec_image is None:
            Player.sec_image = load_image('boss.png')
        if Player.sound is None:
            Player.jump_sound = load_wav('jump.wav')
            Player.whip_sound = load_wav('knifeattack.wav')
            Player.land_sound = load_wav('land.wav')
            Player.up_sound = load_wav('up.wav')
            Player.down_sound = load_wav('down.wav')
            Player.intodoor_sound = load_wav('intodoor.wav')
            Player.spikehit = load_wav('spike_hit.wav')
            Player.damage = load_wav('heartbeat.wav')

    def __init__(self, x, y):
        self.spishoes = False
        self.ui = UI.UIP()
        self.state_machine = StateMachine(self)
        self.state_machine.start(Idle)
        self.state_machine.set_transitions(
            {
                Idle: {right_down: Run, left_down: Run, left_up: Run, right_up: Run,
                       space_down: Jump, down_down: Crouch,  up_down: Idle, up_up: Idle,
                       z_down: Attack, x_down: Idle, c_down: Idle, floating: Jump},
                Run: {right_down: Idle, left_down: Idle, right_up: Idle, left_up: Idle,
                      space_down: Jump, down_down: CrouchMove, z_down: Attack, x_down: Run, c_down:Run, floating: Jump},

                Crouch: {down_up: Idle, left_down: CrouchMove, right_down:CrouchMove, down_down: Crouch, z_down: Attack, space_down: Jump, x_down:Crouch, c_down:Crouch, floating: Jump},
                CrouchMove : {left_up: Crouch, right_up:Crouch, left_down: Crouch, right_down:Crouch, down_up: Run, space_down: Jump, x_down:CrouchMove, c_down:CrouchMove, floating: Jump},
                Climb: {up_up: ClimbMove, up_down: ClimbMove, down_up: ClimbMove, down_down: ClimbMove, z_down: Idle, x_down:Climb,c_down:Climb, space_down: Jump, floating: Jump},
                ClimbMove: {up_up: Climb, up_down: ClimbMove, down_up:Climb, down_down: ClimbMove, x_down:Climb ,c_down:Climb, space_down: Jump, floating: Jump},

                Stunned: { time_out: Idle },
                Attack: { right_up: Attack, left_up: Attack, right_down: Attack, left_down: Attack, space_down: Jump, time_out: Run, c_down:Attack},
                Jump: { right_down: Jump, left_down: Jump , landed: Run, z_down: Jump, x_down:Jump, c_down:Jump, up_down: ClimbMove},
                Dead: { time_out: Dead }
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
        self.view_down = False
        self.view_up = False
        self.whip = Whip(self.x, self.y)
        self.left_pressed = False
        self.right_pressed = False
        self.st_time = None
        self.invincible = False  # 무적 상태 여부
        self.invincible_timer = 0  # 무적 상태 지속 시간

        self.hp = 4
        self.bomb_count = 4
        self.rope_count = 4
        self.gold = 0

        self.aa = False
        self.ladder = False
        self.jumped = False
        self.land = True
        self.move_stage = False

        self.velocity_y = 0  # 초기 수직 속도

    def update(self):
        if self.invincible:
            self.invincible_timer -= game_framework.frame_time
            if self.invincible_timer <= 0:
                self.invincible = False

        currenttop_tile_type = play_mode.map_obj.get_tile_type(self.x, self.y + 30)
        currentdown_tile_type = play_mode.map_obj.get_tile_type(self.x, self.y -33)
        side_tile_type = play_mode.map_obj.get_tile_type(self.x - 80, self.y)
        downleft_tile_type = play_mode.map_obj.get_tile_type(self.x - 26, self.y - 35)
        downright_tile_type = play_mode.map_obj.get_tile_type(self.x+ 26, self.y - 35)

        if currenttop_tile_type not in ['ladder', 'rope', 'rope_head'] and currentdown_tile_type not in ['ladder', 'rope', 'rope_head']:
            self.ladder = False
        else:
            self.ladder = True
            self.jumped = False

        if currentdown_tile_type in ['end'] or side_tile_type in ['end']:
            self.move_stage = True
        else:
            self.move_stage = False

        if self.hp < 1:
            self.state_machine.start(Dead)

        if downleft_tile_type == 'empty' and downright_tile_type == 'empty':
                self.state_machine.add_event(('floating', 0))

        if self.left_pressed and not self.right_pressed:
            self.dirx = -1
            self.face_dir = -1
        elif self.right_pressed and not self.left_pressed:
            self.dirx = 1
            self.face_dir = 1
        else:
            self.dirx = 0


        if self.land or self.state_machine.cur_state in [Climb, ClimbMove]:
            pass

        else:
            if self.velocity_y > -777:
                self.velocity_y += GRAVITY * game_framework.frame_time
            self.y += self.velocity_y * game_framework.frame_time

        self.state_machine.update()

        self.land = False
        self.view_x = clamp(self.x - 960, 0, 1680)
        self.view_y = clamp(self.y - 320, 0, 2000)

    def draw(self, a,b):
        self.state_machine.draw()
        self.ui.draw(self.hp, self.bomb_count, self.rope_count, self.gold)
        if DEBUG:
            bb = self.get_bb()
            draw_rectangle(bb[0] - self.view_x, bb[1] - self.view_y, bb[2] - self.view_x, bb[3] - self.view_y)

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_LEFT:
                self.left_pressed = True
                self.dirx = -1
                self.face_dir = -1
            elif event.key == SDLK_RIGHT:
                self.right_pressed = True
                self.dirx = 1
                self.face_dir = 1
        elif event.type == SDL_KEYUP:
            if event.key == SDLK_LEFT:
                self.left_pressed = False
                if self.right_pressed:
                    self.dirx = 1
                    self.face_dir = 1
                else:
                    self.dirx = 0
            elif event.key == SDLK_RIGHT:
                self.right_pressed = False
                if self.left_pressed:
                    self.dirx = -1
                    self.face_dir = -1
                else:
                    self.dirx = 0
        self.state_machine.handle_event(('INPUT', event))

    def handle_collision(self, group, other):
        if group == 'Player:Map':
            if isinstance(other, Tile):
                if other.tile_type == 'empty':
                    self.land = False
                if other.tile_type in ['solid', 'border']:
                    self.resolve_collision(other)
                elif other.tile_type == 'spike':
                    if self.velocity_y < -200:
                        self.hp = 0
                        self.state_machine.start(Dead)
                        if not self.aa:
                            self.spikehit.set_volume(32)
                            self.spikehit.play()
                            self.aa = True

                if other.tile_type in ['rope', 'ladder', 'rope_head']:
                    self.ladder = True
                else:
                    pass

        elif group == 'Player:Item':
            print('아이템 충돌')
            match (other.name):
                case('Gold Bar'):
                    self.gold += other.value
                    Item.getgold.play()
                case ('Gold Bars'):
                    self.gold += other.value
                    Item.getgoldbar.play()
                case ('bomb'):
                    self.bomb_count += other.value
                    Item.getbomb.play()
                case ('bombs'):
                    self.bomb_count += other.value
                    Item.getbomb.play()
                case ('rope'):
                    self.rope_count += other.value
                    Item.getrope.play()
                case ('spike shoes'):
                    Player.spikehit.play()
                    self.spishoes = True
                case ('arrow'):
                    if other.dx != 0:
                        self.hp -= 1

        elif group == 'Player:Monster' and not self.invincible:
            self.monster_collision(other)


    def monster_collision(self, enemy):
        player_bb = self.get_bb()
        enemy_bb = enemy.get_bb()

        overlap_left = player_bb[2] - enemy_bb[0]
        overlap_right = enemy_bb[2] - player_bb[0]
        overlap_bottom = player_bb[3] - enemy_bb[1]
        overlap_top = enemy_bb[3] - player_bb[1]

        min_overlap = min(overlap_left, overlap_right, overlap_bottom, overlap_top)

        if min_overlap == overlap_left:
            self.take_damage(enemy)

        elif min_overlap == overlap_right:
            self.take_damage(enemy)

        elif min_overlap == overlap_bottom:
            enemy.take_damage(self.spishoes)
            self.velocity_y = 100

        if min_overlap == overlap_top:
            self.take_damage(enemy)


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
            self.dirx = 0

        elif min_overlap == overlap_right:
            self.x += overlap_right
            self.dirx = 0

        elif min_overlap == overlap_bottom:
            self.y -= overlap_bottom
            self.velocity_y = 0

        if min_overlap == overlap_top:
            self.y += overlap_top
            self.velocity_y = 0
            if self.jumped == True:
                self.land_sound.set_volume(64)
                self.land_sound.play()
            self.jumped = False
            self.land = True
            self.state_machine.add_event(('landed', 0))


    def get_bb(self):
        left = self.x - 25
        bottom = self.y - 33
        right = self.x + 25
        top = self.y + 30

        if self.state_machine.cur_state in [Crouch, CrouchMove, Stunned]:
            left = self.x - 25
            bottom = self.y - 33
            right = self.x + 25
            top = self.y

        return left, bottom, right, top

    def use_bomb(self):
        if self.bomb_count > 0:
            self.bomb_count -= 1
            if self.state_machine.cur_state in [Crouch, CrouchMove]:
                Bomb(self.x, self.y, 0)
            else:
                Bomb(self.x, self.y, self.face_dir * 10)


    def use_rope(self):
        if self.rope_count > 0:
            self.rope_count -= 1
            Rope(self.x, self.y)


    def take_damage(self, monster):
        self.hp -= 1
        self.damage.set_volume(32)
        self.damage.play()
        self.invincible = True
        self.invincible_timer = 1.5

        if self.x < monster.x:
            self.x -= 30
            self.velocity_y = 200
        else:
            self.x += 30
            self.velocity_y = 200

def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))






class Idle:
    @staticmethod
    def enter(player, e):
        if start_event(e):
            pass
        elif right_down(e) or left_up(e):
            player.face_dir = -1
        elif left_down(e) or right_up(e):
            player.face_dir = 1
        elif x_down(e):
            player.use_bomb()
        elif c_down(e):
            player.use_rope()
        elif up_down(e):
            if player.ladder:
                player.state_machine.start(ClimbMove)

        player.frame = 0
        player.act = 11
        player.maxframe = 1

    @staticmethod
    def exit(player, e):
        pass

    @staticmethod
    def do(player):
        pass

    @staticmethod
    def draw(player):
        player.act = 11
        player.maxframe = 1
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
        if c_down(e):
            player.use_rope()
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
        player.frame = (player.frame + 8 * ACTION_PER_TIME * game_framework.frame_time) % player.maxframe
        player.x += player.dirx * RUN_SPEED_PPS * game_framework.frame_time
        player.whip.draw(player.view_x, player.view_y)

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

        if x_down(e):
            player.use_bomb()
        if c_down(e):
            player.use_rope()

        player.act = 10
        if player.frame != 2:
            player.frame = 0
        player.maxframe = 2


    @staticmethod
    def exit(player, e):
        player.view_down = False
        pass

    @staticmethod
    def do(player):
        if player.frame != 2:
            player.frame = (player.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % (
                        player.maxframe + 1)
            if player.frame > 2:
                player.frame = 2


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
        if x_down(e):
            player.use_bomb()
        if c_down(e):
            player.use_rope()
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
        player.x += player.dirx * RUN_SPEED_PPS * game_framework.frame_time / 2

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
        if x_down(e):
            player.use_bomb()
        if c_down(e):
            player.use_rope()

        if start_event(e):
            player.face_dir = 1
        elif right_down(e) or left_up(e):
            player.face_dir = -1
        elif left_down(e) or right_up(e):
            player.face_dir = 1

        player.act = 4
        player.frame = 0
        player.maxframe = 1
        player.diry  = 0
        if player.ladder:
            player.x =  player.x // 80 * 80 + 40

    @staticmethod
    def exit(player, e):
        player.view_up = False

    @staticmethod
    def do(player):

        if not player.ladder:
            player.state_machine.start(Idle)
        else:
            if player.state_machine.cur_state in [Climb, ClimbMove]:
                player.velocity_y = 0
        if player.frame < 4:
            player.frame = (player.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % player.maxframe

    @staticmethod
    def draw(player):
        player.act = 4
        player.maxframe = 1
        player.image.clip_draw(int(player.frame) * player.f_w,
                               player.f_h * player.act + 64,
                               player.f_w,
                               player.f_h,
                               player.x - player.view_x,
                               player.y - player.view_y, 80, 80 )


class ClimbMove:
    @staticmethod
    def enter(player, e):
        if not player.ladder:
            player.state_machine.start(Idle)

        if up_down(e):
            player.diry = 1
        elif down_down(e):
            player.diry = -1
        if x_down(e):
            player.use_bomb()
        if c_down(e):
            player.use_rope()

        if player.diry == 0:
            player.diry = 1

        if player.diry == 1:
            player.up_sound.set_volume(32)
            player.up_sound.play()
        elif player.diry == -1:
            player.down_sound.set_volume(32)
            player.down_sound.play()

        player.act = 4
        player.frame = 0
        player.maxframe = 10
        if player.ladder:
            player.x = player.x // 80 * 80 + 40
    @staticmethod
    def exit(player, e):
        pass

    @staticmethod
    def do(player):
        if not player.ladder:
            player.state_machine.start(Idle)
        else:
            if player.state_machine.cur_state in [Climb, ClimbMove]:
                player.velocity_y = 0


        player.frame = (player.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % player.maxframe
        player.y += player.diry * RUN_SPEED_PPS * game_framework.frame_time


    @staticmethod
    def draw(player):
        player.act = 4
        player.maxframe = 10
        player.image.clip_draw(int(player.frame) * player.f_w,
                               player.f_h * player.act + 64,
                               player.f_w,
                               player.f_h,
                               player.x - player.view_x,
                               player.y - player.view_y, 80 ,80 )


class Stunned:
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
        player.frame = (player.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % player.maxframe

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
        if player.st_time is None:
            player.st_time = get_time()

    @staticmethod
    def exit(player, e):
        pass

    @staticmethod
    def do(player):
        player.frame = (player.frame + player.maxframe * ACTION_PER_TIME * game_framework.frame_time) % player.maxframe
        if get_time() - player.st_time > 5:
            game_framework.quit()
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
            if not player.jumped and space_down(e):
                player.velocity_y = 400  # 점프 초기 속도 (픽셀/초)
                player.jumped = True
                player.land = False
                player.jump_sound.set_volume(64)
                player.jump_sound.play()

            if floating(e):
                player.jumped = True
                player.land = False

            if x_down(e):
                player.use_bomb()
            if c_down(e):
                player.use_rope()

            if z_down(e):
                if not player.whip.active:
                    player.frame = 0
                player.whip.activate()
                player.whip.update(player.x, player.y, player.face_dir)

            player.act = 2
            player.maxframe = 7
            player.frame = 0

        @staticmethod
        def exit(player, e):
            pass

        @staticmethod
        def do(player):
            player.act = 2
            player.maxframe = 7
            player.x += player.dirx * RUN_SPEED_PPS * game_framework.frame_time
            player.frame = (player.frame + 7 * 0.7 * game_framework.frame_time) % (player.maxframe + 1)

            if player.whip.active:
                player.whip.update(player.x, player.y, player.face_dir)

            if player.frame > 7:
                player.frame = 7

        @staticmethod
        def draw(player):
            player.act = 2
            player.maxframe = 7
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
            if player.whip.active:
                player.whip.draw(player.view_x, player.view_y)

class Attack:
    @staticmethod
    def enter(player, e):
        if right_down(e):  # 오른쪽으로 RUN
            player.dirx, player.face_dir = 1, 1
        elif left_down(e):  # 왼쪽으로 RUN
            player.dirx, player.face_dir = -1, -1
        if x_down(e):
            player.use_bomb()
        if c_down(e):
            player.use_rope()
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
        player.frame = (player.frame + 6 * ACTION_PER_TIME * game_framework.frame_time) % (player.maxframe + 1)
        player.whip.update(player.x, player.y, player.face_dir)

        if player.frame > 6:
            player.state_machine.add_event(('TIME_OUT', 0))

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
        player.whip.draw(player.view_x, player.view_y)
        if int(player.frame) == 5:
            player.aa = True
