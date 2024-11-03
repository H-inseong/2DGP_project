from pico2d import *

from Player import Player
from UI import UI

WIDTH, HEIGHT = 1920, 1080

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