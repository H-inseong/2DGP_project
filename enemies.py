import random
import game_framework
import game_world

from pico2d import *

import play_mode
from Item import Item
from behavior_tree import BehaviorTree, Condition, Sequence, Action, Selector

PIXEL_PER_METER = (10.0 / 0.3)
RUN_SPEED_KMPH = 10.0
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

TIME_PER_ACTION = 1
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 10.0

GRAVITY = -500

class Snake:
    image = None

    def load_images(self):
        if Snake.image == None:
            Snake.image = load_image('Snakes.png')

    def __init__(self, x, y):
        game_world.add_object(self, 1)
        game_world.add_collision_pair('Player:Monster', None, self)
        game_world.add_collision_pair('Whip:Monster', None, self)
        game_world.add_collision_pair('Monster:Map', self, None)

        self.land = False
        self.x, self.y = x * 80 + 40, y * 80
        self.load_images()
        self.f_size = 80
        self.frame = 0
        self.dir = random.randint(-1, 1)
        self.dir_timer = get_time()

    def update(self):
        self.frame = (self.frame + 12 * ACTION_PER_TIME * game_framework.frame_time) % 12

        self.x += RUN_SPEED_PPS * self.dir * game_framework.frame_time * 2

        if get_time() - self.dir_timer > 3:
            self.dir = random.choice([-1, 0, 1])  # 방향 무작위 선택
            self.dir_timer = get_time()

        down_tile_type = play_mode.map_obj.get_tile_type(self.x, self.y - 35)
        if down_tile_type == 'empty':
            self.land = False

        next_down_tile_type = play_mode.map_obj.get_tile_type(self.x + -self.dir * 21, self.y - 35)
        if next_down_tile_type == 'empty':
            self.dir = -self.dir
        if not self.land:
            self.y += GRAVITY * game_framework.frame_time

    def draw(self, x, y):
        if self.dir < 0:
            Snake.image.clip_composite_draw(int(self.frame) * self.f_size, self.f_size + 28,
                                            self.f_size, self.f_size, 0, 'h',
                                            self.x - x, self.y - y, 60, 60)
        else:
            Snake.image.clip_draw(int(self.frame) * self.f_size, self.f_size + 28,
                                            self.f_size, self.f_size,
                                            self.x - x, self.y - y, 60, 60)
        bb = self.get_bb()
        draw_rectangle(bb[0] - x, bb[1] - y, bb[2] - x, bb[3] - y)

    def handle_event(self, event):
        pass

    def handle_collision(self, group, other):
        if group == 'Whip:Monster':
            game_world.remove_object(self)
            play_mode.player.spikehit.play()

        if group == 'Monster:Map':
            if other.tile_type in ['solid', 'border']:
                    self.resolve_collision(other)

    def get_bb(self):
        return self.x - 20 , self.y - 30 , self.x + 20 , self.y + 20

    def resolve_collision(self, tile):
        monster_bb = self.get_bb()
        tile_bb = tile.get_bb()

        overlap_left = monster_bb[2] - tile_bb[0]
        overlap_right = tile_bb[2] - monster_bb[0]
        overlap_bottom = monster_bb[3] - tile_bb[1]
        overlap_top = tile_bb[3] - monster_bb[1]

        min_overlap = min(overlap_left, overlap_right, overlap_bottom, overlap_top)

        if min_overlap == overlap_left:
            self.x -= overlap_left

        elif min_overlap == overlap_right:
            self.x += overlap_right

        elif min_overlap == overlap_bottom:
            self.y -= overlap_bottom
            self.land = True
            self.dir_timer = get_time()

        elif min_overlap == overlap_top:
            self.y += overlap_top

    def take_damage(self, x):
        game_world.remove_object(self)

class gSnake:
    image = None

    def load_images(self):
        if gSnake.image == None:
            gSnake.image = load_image('Snakes.png')

    def __init__(self, x, y):
        game_world.add_object(self, 1)
        game_world.add_collision_pair('Player:Monster', None, self)
        game_world.add_collision_pair('Whip:Monster', None, self)
        game_world.add_collision_pair('Monster:Map', self, None)

        self.land = False
        self.x, self.y = x * 80 + 40, y * 80
        self.load_images()
        self.f_size = 80
        self.frame = 0
        self.dir = random.randint(-1, 1)
        self.dir_timer = get_time()

    def update(self):
        self.frame = (self.frame + 12 * ACTION_PER_TIME * game_framework.frame_time) % 12

        self.x += RUN_SPEED_PPS * self.dir * game_framework.frame_time * 2

        if get_time() - self.dir_timer > 1:
            self.dir = random.choice([-1, 0, 1])  # 방향 무작위 선택
            self.dir_timer = get_time()

        down_tile_type = play_mode.map_obj.get_tile_type(self.x, self.y - 25)
        if down_tile_type == 'empty':
            self.land = False

        next_down_tile_type = play_mode.map_obj.get_tile_type(self.x + -self.dir * 21, self.y - 25)
        if next_down_tile_type == 'empty':
            self.dir = -self.dir
        if not self.land:
            self.y += GRAVITY * game_framework.frame_time

    def draw(self, x, y):
        if self.dir < 0:
            gSnake.image.clip_composite_draw(int(self.frame) * self.f_size, self.f_size*3 + 28,
                                            self.f_size, self.f_size, 0, 'h',
                                            self.x - x, self.y - y, 60, 60)
        else:
            gSnake.image.clip_draw(int(self.frame) * self.f_size, self.f_size*3 + 28,
                                            self.f_size, self.f_size,
                                            self.x - x, self.y - y, 60, 60)
        bb = self.get_bb()
        draw_rectangle(bb[0] - x, bb[1] - y, bb[2] - x, bb[3] - y)

    def handle_event(self, event):
        pass

    def handle_collision(self, group, other):
        if group == 'Whip:Monster':
            game_world.remove_object(self)
            play_mode.player.spikehit.play()

        if group == 'Monster:Map':
            if other.tile_type in ['solid', 'border']:
                    self.resolve_collision(other)

    def get_bb(self):
        return self.x - 20 , self.y - 20 , self.x + 20 , self.y + 20

    def resolve_collision(self, tile):
        monster_bb = self.get_bb()
        tile_bb = tile.get_bb()

        overlap_left = monster_bb[2] - tile_bb[0]
        overlap_right = tile_bb[2] - monster_bb[0]
        overlap_bottom = monster_bb[3] - tile_bb[1]
        overlap_top = tile_bb[3] - monster_bb[1]

        min_overlap = min(overlap_left, overlap_right, overlap_bottom, overlap_top)

        if min_overlap == overlap_left:
            self.x -= overlap_left

        elif min_overlap == overlap_right:
            self.x += overlap_right

        elif min_overlap == overlap_bottom:
            self.y -= overlap_bottom
            self.land = True
            self.dir_timer = get_time()

        elif min_overlap == overlap_top:
            self.y += overlap_top

    def take_damage(self, x):
        game_world.remove_object(self)



class Boss:
    image = None

    def __init__(self, x, y):
        game_world.add_object(self, 1)
        game_world.add_collision_pair('Player:Monster', None, self)
        game_world.add_collision_pair('Whip:Monster', None, self)
        game_world.add_collision_pair('Monster:Map', self, None)

        if Boss.image is None:
            Boss.image = load_image('boss.png')
            Boss.tong = load_wav('tank.wav')
            """Boss.dead = load_wav('')
            Boss.skr = load_wav('')
            Boss.skrr = load_wav('')"""

        self.x, self.y = x * 80, y * 80
        self.frame = 0
        self.maxframe = 9
        self.action = 15
        self.direction = -1  # -1: 왼쪽, 1: 오른쪽
        self.hp = 10
        self.speed = RUN_SPEED_PPS / 2
        self.roll_speed = RUN_SPEED_PPS * 3
        self.roll_timer = 0
        self.recover_timer = 0
        self.build_behavior_tree()
        self.invincible = False  # 무적 상태 여부
        self.invincible_timer = 0  # 무적 상태 지속 시간

    def update(self):
        if self.invincible:
            self.invincible_timer -= game_framework.frame_time
            if self.invincible_timer <= 0:
                self.invincible = False

        down_tile_type = play_mode.map_obj.get_tile_type(self.x, self.y - 80)
        if down_tile_type == 'empty':
            self.y += GRAVITY * game_framework.frame_time
        else:

            pass

        self.frame = (self.frame + self.maxframe * game_framework.frame_time) % self.maxframe
        self.bt.run()

        if self.hp <= 0:
            self.drop_items()
            game_world.remove_object(self)

    def draw(self, camera_x, camera_y):
        screen_x, screen_y = self.x - camera_x, self.y - camera_y
        if self.direction == 1:  # 오른쪽
            self.image.clip_draw_to_origin(int(self.frame) * 128, 128 * self.action, 128, 128, screen_x, screen_y, 160, 160)
        else:  # 왼쪽
            self.image.clip_composite_draw(int(self.frame) * 128, 128 * self.action, 128, 128, 0, 'h', screen_x + 80, screen_y + 80, 160, 160)

    def build_behavior_tree(self):
        die = Condition('체력이 0인가?', self.is_dead)
        recover = Condition('회복 중인가?', self.is_recovering)
        attack = Sequence('플레이어 공격', Condition('플레이어가 가까운가?', self.is_player_nearby), Action('공격', self.attack_player))
        chase = Sequence('플레이어 추격', Condition('플레이어가 범위 내에 있는가?', self.is_player_in_range), Action('돌진', self.chase_player))
        idle = Action('Idle 상태 유지', self.idle_behavior)

        root = Selector('Quillback 행동 선택', die, recover, attack, chase, idle)
        self.bt = BehaviorTree(root)

    # ---- 상태 확인 ----
    def is_dead(self):
        return BehaviorTree.SUCCESS if self.hp <= 0 else BehaviorTree.FAIL

    def is_recovering(self):
        if self.recover_timer > 0:
            self.recover_timer -= game_framework.frame_time
            return BehaviorTree.SUCCESS
        return BehaviorTree.FAIL

    def is_player_nearby(self, distance=50):
        global player
        dx, dy = self.x - play_mode.player.x, self.y - play_mode.player.y
        return BehaviorTree.SUCCESS if (dx**2 + dy**2) < (distance**2) else BehaviorTree.FAIL

    def is_player_in_range(self, range_distance=400):
        dx, dy = self.x - play_mode.player.x, self.y - play_mode.player.y
        return BehaviorTree.SUCCESS if (dx**2 + dy**2) < (range_distance**2) else BehaviorTree.FAIL

    # ---- 행동 ----
    def idle_behavior(self):
        self.x += self.speed * self.direction * game_framework.frame_time
        if self.x < 800 or self.x > 1600:  # 벽에 닿으면 방향 전환
            self.direction *= -1
        return BehaviorTree.RUNNING

    def chase_player(self):
        self.roll_timer += game_framework.frame_time
        self.maxframe = 9
        self.action = 9
        self.x += self.roll_speed * self.direction * game_framework.frame_time
        if abs(play_mode.player.x - self.x) < 50:  # 플레이어 근처에 도달
            self.recover_timer = 2  # 2초 동안 회복 상태
            return BehaviorTree.SUCCESS
        elif self.roll_timer > 2:  # 일정 시간 후 멈춤
            self.roll_timer = 0
            return BehaviorTree.FAIL
        return BehaviorTree.RUNNING

    def attack_player(self):
        self.frame = (self.frame + FRAMES_PER_ACTION * game_framework.frame_time) % FRAMES_PER_ACTION
        # 점프 공격 구현
        return BehaviorTree.SUCCESS

    def handle_collision(self, group, other):
        if group == 'Whip:Monster':  # 채찍 공격에 맞을 때
            self.hp -= 1
            if self.hp <= 0:
                game_world.remove_object(self)
        if group == 'Monster:Map':
            if other.tile_type == 'empty':
                self.land = False
            if other.tile_type in ['solid', 'border']:
                #self.resolve_collision(other)
                pass

    def drop_items(self):
        Item(self.x // 80, self.y // 80, 0, 13)
        pass

    def get_bb(self):
        return self.x - 80, self.y - 80, self.x + 80, self.y + 80

    def take_damage(self, spi):
        if not self.invincible:
            if spi:
                self.hp -= 3
                self.invincible = True
                self.invincible_timer = 2
            else:
                pass