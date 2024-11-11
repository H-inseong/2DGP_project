from pico2d import load_image, get_events
from sdl2 import SDL_QUIT, SDL_KEYDOWN, SDLK_RIGHT, SDLK_LEFT, SDLK_UP, SDLK_DOWN, SDLK_ESCAPE, SDL_KEYUP

from MOVEMENT_BASE import WIDTH, HEIGHT
from state_machine import StateMachine

PIXEL_PER_METER = (10.0/0.3)
RUN_SPEED_KMPH = 20.0
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)


class Player:
    def __init__(self):
        self.state_machine = StateMachine(self)
        self.state_machine.start()
        self.x, self.y = WIDTH // 2, HEIGHT // 2
        self.dirx, self.diry = 0, 0
        self.last_dir = 0
        self.frame = 0
        self.image = load_image('Sprite_Sheet.png')
        self.frame_width = 80
        self.frame_height = 80
        self.frame_y = 80

        #hp와 item 등을 여기서 관리하는게 맞는가?
        #게임 루프가 더 좋지 않은가?

        self.hp = 4
        self.item = [4, 4, 0] # bomb, rope, gold


    def update(self):
        if abs(self.dirx == 0) and abs(self.diry == 0):  # idle
            self.frame = 0
        elif abs(self.dirx) != 0:  # left or right
            self.frame = (self.frame + 1) % 8
        elif self.diry != 0:  # up or down
            self.frame = (self.frame + 1) % 6

    def draw(self):
        if self.dirx == 0 and self.diry == 0:  # idle
            if self.last_dir == 1 or self.last_dir == 0:
                self.image.clip_draw(self.frame,
                                    self.frame_y * 11+ 64,
                                    self.frame_width,
                                    self.frame_height,
                                    self.x,
                                    self.y,)
            else:
                self.image.clip_composite_draw(self.frame,
                                    self.frame_y * 11+ 64,
                                    self.frame_width,
                                    self.frame_height,
                                    0, 'h',
                                    self.x,
                                    self.y,
                                    80,
                                    80)
        elif self.dirx == -1:  # left
            self.image.clip_composite_draw((self.frame + 1) * self.frame_width,
                                           self.frame_y * 11 + 64,
                                           self.frame_width,
                                           self.frame_height,
                                           0, 'h',
                                           self.x,
                                           self.y,
                                           80,
                                           80)
        elif self.dirx == 1:  # right
            self.image.clip_draw(self.frame * self.frame_width,
                                 self.frame_y * 11 + 64,
                                 self.frame_width,
                                 self.frame_height,
                                 self.x,
                                 self.y)
        elif self.diry == -1:  # down
            self.image.clip_draw(self.frame * self.frame_width +
                                 self.frame_width * 6,
                                 self.frame_y * 6 + 64,
                                 self.frame_width,
                                 self.frame_height,
                                 self.x,
                                 self.y)
        elif self.diry == 1:  # up
            self.image.clip_draw(self.frame * self.frame_width,
                                 self.frame_y * 6 + 64,
                                 self.frame_width,
                                 self.frame_height,
                                 self.x,
                                 self.y)

    def handle_event(self, event):
        self.state_machine.handle_event(('INPUT', event))

    def move(self):
        # 경계 처리 및 이동
        if (self.x + player.dirx * 10 >= player.frame_width // 2) and (
                self.x + player.dirx * 10 <= WIDTH - player.frame_width // 2):
            player.x += player.dirx * 10

        if (player.y + player.diry * 10 >= player.frame_height // 2) and (
                player.y + player.diry * 10 <= HEIGHT - player.frame_height // 2):
            player.y += player.diry * 10
