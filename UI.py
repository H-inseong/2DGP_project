from pico2d import load_image, load_font

from MOVEMENT_BASE import HEIGHT


class UI:
    #UI를 한개씩 다루는게 아닌 여기서 한번에 다루는게 맞는가?
    #UI객체들을 다루는 추가 객체?

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
