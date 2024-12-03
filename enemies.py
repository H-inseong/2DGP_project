import random
import math
import game_framework
import game_world

from pico2d import *

import play_mode
from behavior_tree import BehaviorTree, Condition, Sequence, Action, Selector

# zombie Run Speed
PIXEL_PER_METER = (10.0 / 0.3)  # 10 pixel 30 cm
RUN_SPEED_KMPH = 10.0  # Km / Hour
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

# zombie Action Speed
TIME_PER_ACTION = 1
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 10.0

class Snake:
    image = None

    def load_images(self):
        if Snake.image == None:
            Snake.image = load_image('Snakes.png')
    def __init__(self):
        game_world.add_object(self, 1)
        game_world.add_collision_pair('Player:Monster', None, self)
        game_world.add_collision_pair('Whip:Monster', None, self)

        self.x, self.y = random.randint(1600-800, 1600), 240
        self.load_images()
        self.f_size = 80
        self.frame = 0
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
            Snake.image.clip_composite_draw(int(self.frame) * self.f_size, self.f_size * self.f_size + 28,
                                            self.f_size, self.f_size, 0, 'h',
                                            self.x - x + 40, self.y - y + 40, 80, 80)
        else:
            Snake.image.clip_draw_to_origin(int(self.frame) * self.f_size, self.f_size + 28,
                                            self.f_size, self.f_size,
                                            self.x - x, self.y - y , 80, 80)

    def handle_event(self, event):
        pass

    def handle_collision(self, group, other):
        if group == 'Whip:Monster':
            game_world.remove_object(self)


    def get_bb(self):
        return self.x - self.f_size/3 , self.y - self.f_size/2 , self.x + self.f_size/3 , self.y + self.f_size/3

class Boss:
    image = None

    def __init__(self, x, y):
        game_world.add_object(self, 1)
        game_world.add_collision_pair('Player:Monster', None, self)
        game_world.add_collision_pair('Whip:Monster', None, self)
        game_world.add_collision_pair('Monster:Map', self, None)

        if Boss.image is None:
            Boss.image = load_image('boss.png')

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
        self.frame = (self.frame + self.maxframe * game_framework.frame_time) % self.maxframe
        self.bt.run()

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
        if isinstance(other, Tile):
            if other.tile_type == 'empty':
                self.land = False
            if other.tile_type in ['solid', 'border']:
                self.resolve_collision(other)

    def drop_items(self):
        # 아이템 드롭 로직
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
            #boss는 신발이 없으면 밟히지 않음