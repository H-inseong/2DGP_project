from sys import platform

from pico2d import *
from pygame.examples.cursors import image

WIDTH, HEIGHT = 1920, 1080

class UI:
    lbs = 80 # left blank size
    ypos = HEIGHT - 70
    def __init__(self):
        self.heart_image = load_image('Sprite_Sheet.png')
        self.items_image = load_image('items_sheet.png')
        self.small_font = load_font('DNFBitBitTTF.ttf', 30)
        self.font = load_font('DNFBitBitTTF.ttf', 35)
        self.large_font = load_font('DNFBitBitTTF.ttf', 40)
    def draw(self, hp, bomb, rope): # 추가할 것: gold, time, stage
        #draw heart
        self.heart_image.clip_draw(800, 64, 160, 160,
                                   self.lbs, self.ypos, 90, 90)
        self.large_font.draw(self.lbs + 10, self.ypos - 23, f'{hp}', (0, 0, 0))
        self.font.draw(self.lbs + 10, self.ypos - 20, f'{hp}', (255, 255, 255))

        #draw bomb
        self.items_image.clip_draw(0, 128*10 , 128, 128,
                                   self.lbs*2, self.ypos - 10, 90,90)
        self.font.draw(self.lbs*2.2, self.ypos - 25, f'{bomb}', (0, 0, 0))
        self.small_font.draw(self.lbs*2.2, self.ypos - 24, f'{bomb}', (255, 255, 255))

        #draw rope
        self.items_image.clip_draw(0, 128 * 9, 128, 128,
                                   self.lbs * 3, self.ypos - 10, 90, 90)
        self.font.draw(self.lbs * 3.2, self.ypos - 25, f'{rope}', (0, 0, 0))
        self.small_font.draw(self.lbs * 3.2, self.ypos - 24, f'{rope}', (255, 255, 255))



class Player:
    def __init__(self):
        self.x, self.y = WIDTH // 2, HEIGHT // 2
        self.dirx, self.diry = 0, 0
        self.last_dir = 0
        self.frame = 0
        self.image = load_image('Sprite_Sheet.png')
        self.frame_width = 80
        self.frame_height = 80
        self.frame_y = 80
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

    def handle_events(self):
        events = get_events()
        for event in events:
            if event.type == SDL_QUIT:
                return False

            elif event.type == SDL_KEYDOWN:
                if event.key == SDLK_RIGHT:
                    player.dirx += 1
                    player.last_dir = 1
                elif event.key == SDLK_LEFT:
                    player.dirx -= 1
                    player.last_dir = -1
                elif event.key == SDLK_UP:
                    player.diry += 1
                elif event.key == SDLK_DOWN:
                    player.diry -= 1
                elif event.key == SDLK_ESCAPE:
                    return False

            elif event.type == SDL_KEYUP:
                if event.key == SDLK_RIGHT:
                    player.dirx -= 1
                elif event.key == SDLK_LEFT:
                    player.dirx += 1
                elif event.key == SDLK_UP:
                    player.diry -= 1
                elif event.key == SDLK_DOWN:
                    player.diry += 1
        return True

    def move(self):
        # 경계 처리 및 이동
        if (self.x + player.dirx * 10 >= player.frame_width // 2) and (
                self.x + player.dirx * 10 <= WIDTH - player.frame_width // 2):
            player.x += player.dirx * 10

        if (player.y + player.diry * 10 >= player.frame_height // 2) and (
                player.y + player.diry * 10 <= HEIGHT - player.frame_height // 2):
            player.y += player.diry * 10


def main():
    open_canvas(WIDTH, HEIGHT)
    hide_cursor()

    global player
    player = Player()
    ui = UI()

    running = True
    while running:
        clear_canvas()

        running = player.handle_events()

        player.update()
        player.move()

        # 배경 그리기 (예시)
        # background_sheet.draw(WIDTH //2 , HEIGHT //2)

        player.draw()
        ui.draw(player.hp, player.item[0], player.item[1])

        update_canvas()

        delay(0.05)

    close_canvas()


if __name__ == '__main__':
    main()