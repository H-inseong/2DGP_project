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
        self.rolling = False
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
        self.rolling = False
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
            Boss.dead = load_wav('grunt01.wav')
            Boss.skr = load_wav('grunt03.wav')
            Boss.skrr = load_wav('hit.wav')
            Boss.tong.set_volume(64)
            Boss.dead.set_volume(64)
            Boss.skr.set_volume(64)
            Boss.skrr.set_volume(64)

        self.x, self.y = x * 80, y * 80 + 80  # y 위치 조정
        self.frame = 0
        self.f_size = 160
        self.maxframe = 9
        self.action = 15
        self.direction = -1  # -1: 왼쪽, 1: 오른쪽
        self.hp = 10
        self.speed = RUN_SPEED_PPS / 2
        self.roll_speed = RUN_SPEED_PPS * 3
        self.roll_timer = 0
        self.recover_timer = 0
        self.build_behavior_tree()
        self.invincible = False
        self.invincible_timer = 0

        self.direction_locked = False
        self.attacking = False
        self.jumping = False
        self.rolling = False
        self.waiting = False
        self.wait_timer = 0

        self.dir_timer = get_time()

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
        if self.direction == 1:
            self.image.clip_draw(int(self.frame) * 128, 128 * self.action, 128, 128, screen_x, screen_y, 160, 160)
        else:
            self.image.clip_composite_draw(int(self.frame) * 128, 128 * self.action, 128, 128, 0, 'h', screen_x, screen_y, 160, 160)

    def build_behavior_tree(self):
        die = Condition('체력이 0인가?', self.is_dead)
        detect_player_or_attacking = Condition('플레이어가 4칸 이내에 있거나 공격 중인가?', self.is_player_within_4_tiles_or_attacking)
        jump_attack = Action('점프 공격', self.do_jump_attack)
        roll_attack = Action('구르기', self.do_roll)
        wait_after_roll = Action('롤 후 대기', self.do_wait_after_roll)
        idle = Action('배회', self.idle_behavior)

        attack_sequence = Sequence('공격 시퀀스', detect_player_or_attacking, jump_attack, roll_attack, wait_after_roll)


        root = Selector('Quillback 행동 선택', die, attack_sequence, idle)
        self.bt = BehaviorTree(root)



    def is_dead(self):
        return BehaviorTree.SUCCESS if self.hp <= 0 else BehaviorTree.FAIL

    def is_player_within_4_tiles_or_attacking(self):
        if self.attacking:
            return BehaviorTree.SUCCESS
        return self.is_player_within_4_tiles()

    def is_player_within_4_tiles(self):
        dx, dy = self.x - play_mode.player.x, self.y - play_mode.player.y
        distance = (dx**2 + dy**2)**0.5
        if distance < 320:
            return BehaviorTree.SUCCESS
        return BehaviorTree.FAIL




    def idle_behavior(self):
        self.action = 15
        self.maxframe = 9
        self.attacking = False
        self.jumping = False
        self.rolling = False
        self.waiting = False
        self.direction_locked = False

        if get_time() - self.dir_timer > 3:
            self.direction = random.choice([-1, 0, 1])
            self.dir_timer = get_time()

        if self.direction != 0:
            front_x = self.x + self.direction * 80
            front_y = self.y
            tile_x, tile_y = play_mode.map_obj.get_tile_coords(front_x, front_y)
            tile_type = play_mode.map_obj.get_tile_type(front_x, front_y)

            if not play_mode.map_obj.is_passable(tile_x, tile_y):
                self.direction = -self.direction

        self.x += self.speed * self.direction * game_framework.frame_time
        return BehaviorTree.RUNNING

    def do_jump_attack(self):
        if not self.direction_locked:
            self.direction = 1 if play_mode.player.x > self.x else -1
            self.direction_locked = True
            self.attacking = True

        self.jumping = True
        self.attacking = True
        self.action = 10
        self.maxframe = 9

        if not hasattr(self, 'jump_timer'):
            self.jump_timer = 0
        self.jump_timer += game_framework.frame_time

        self.break_front_tiles()

        if self.jump_timer > 0.5:
            self.jumping = False
            self.jump_timer = 0
            return BehaviorTree.SUCCESS

        return BehaviorTree.RUNNING

    def do_roll(self):
        if not self.rolling:
            self.rolling = True
            self.action = 9
            self.maxframe = 9

        result = self.roll_forward_and_break()
        if result == 'border_hit':
            self.rolling = False
            self.attacking = False  # 공격 상태 해제
            return BehaviorTree.SUCCESS

        return BehaviorTree.RUNNING

    def do_wait_after_roll(self):
        if not self.waiting:
            self.waiting = True
            self.wait_timer = 5.0
            self.action = 15  # 대기 애니메이션

        self.wait_timer -= game_framework.frame_time
        if self.wait_timer <= 0:
            self.waiting = False
            return BehaviorTree.SUCCESS

        return BehaviorTree.RUNNING

    # ---- 부가 함수들 ----
    def break_front_tiles(self):
        front_check_distance = 80
        vertical_offsets = [0, 120]  # 점프 중 파괴할 타일의 y 오프셋

        for v_off in vertical_offsets:
            cx = self.x + self.direction * front_check_distance
            cy = self.y + v_off
            t_type = play_mode.map_obj.get_tile_type(cx, cy)

            # border 블럭은 파괴하지 않음
            if t_type == 'solid':
                tx, ty = play_mode.map_obj.get_tile_coords(cx, cy)
                play_mode.map_obj.break_tile(tx, ty)
            # border인 경우 파괴하지 않고 롤 중단 조건 없음

    def roll_forward_and_break(self):
        front_check_distance = 80
        vertical_offsets = [80, 0]  # 롤 중 파괴할 타일의 y 오프셋
        border_encountered = False

        for v_off in vertical_offsets:
            cx = self.x + self.direction * front_check_distance
            cy = self.y + v_off
            t_type = play_mode.map_obj.get_tile_type(cx, cy)

            if t_type == 'solid':
                tx, ty = play_mode.map_obj.get_tile_coords(cx, cy)
                play_mode.map_obj.break_tile(tx, ty)
            elif t_type == 'border':
                border_encountered = True

        self.x += self.roll_speed * self.direction * game_framework.frame_time

        if border_encountered:
            return 'border_hit'
        return 'continue'

    def handle_collision(self, group, other):
        if group == 'Whip:Monster':
            if not self.invincible:
                self.invincible = True
                self.invincible_timer = 2
                self.hp -= 1
                Boss.skr.play()

            if self.hp <= 0:
                self.drop_items()
                game_world.remove_object(self)
        if group == 'Monster:Map':
            pass  # 구르기나 점프 도중 타일 파괴는 이미 처리했으므로 추가 처리 없음

    def drop_items(self):
        Item(self.x // 80, self.y // 80, 0, 13)
        Boss.dead.play()


    def get_bb(self):
        return self.x - 80, self.y - 80, self.x + 80, self.y + 80

    def take_damage(self, spi):
        if not self.invincible:
            if spi:
                self.hp -= 3
                self.invincible = True
                self.invincible_timer = 2
                Boss.skr.play()
            else:
                Boss.tong.play()
        else:
            Boss.tong.play()