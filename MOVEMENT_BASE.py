from pico2d import *

TUK_WIDTH, TUK_HEIGHT = 1280, 1024
open_canvas(TUK_WIDTH, TUK_HEIGHT)
#tuk_ground = load_image('TUK_GROUND.png')
character_sheet = load_image('Sprite_Sheet.jpg')
background_sheet = load_image('background_main.jpg')
items_sheet = load_image('items_sheet.jpg')

def get_sprite(sheet, frame, width, height):
    sprite = sheet.clip_draw(frame * width, 0, width, height, 0, 0)
    return sprite

def handle_events():
    global running
    global dirx
    global diry

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False

        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_RIGHT:
                dirx += 1
            elif event.key == SDLK_LEFT:
                dirx -= 1
            elif event.key == SDLK_UP:
                diry += 1
            elif event.key == SDLK_DOWN:
                diry -= 1
            elif event.key == SDLK_ESCAPE:
                running = False

        elif event.type == SDL_KEYUP:
            if event.key == SDLK_RIGHT:
                dirx -= 1
            elif event.key == SDLK_LEFT:
                dirx += 1
            elif event.key == SDLK_UP:
                diry -= 1
            elif event.key == SDLK_DOWN:
                diry += 1



running = True
hide_cursor()

dirx = 0
diry = 0
frame = 0
x, y = TUK_WIDTH // 2, TUK_HEIGHT // 2
frame_width = 80
frame_height = 80
frame_y = 80

while running:
    clear_canvas()
   # tuk_ground.draw(TUK_WIDTH // 2, TUK_HEIGHT // 2)

    if dirx == 0 and diry == 0: #idle
       character.clip_draw(frame * frame_width, frame_y * 3 + 64, frame_width, frame_height, x, y)

    elif dirx == -1: # left
        character.clip_composite_draw(frame * frame_width, frame_y * 11 + 64, frame_width, frame_height, 0, 'h', x, y, 80, 80)
    elif dirx == 1: #right
        character.clip_draw(frame * frame_width, frame_y * 11 + 64, frame_width, frame_height, x, y)
    elif diry == -1: #down
        character.clip_draw(frame * frame_width + frame_width * 6, frame_y * 6 + 64, frame_width, frame_height, x, y)
    elif diry == 1: #up
        character.clip_draw(frame * frame_width, frame_y * 6 + 64, frame_width, frame_height, x, y)

    update_canvas()
    handle_events()

    if dirx == 0 and diry == 0: #idle
        frame = (frame + 1) % 7
    elif dirx == -1: # left
        frame = (frame + 1) % 9
    elif dirx == 1: #right
        frame = (frame + 1) % 9
    elif diry == -1: #down
        frame = (frame + 1) % 6
    elif diry == 1: #up
        frame = (frame + 1) % 6


    #경계처리
    if (x + dirx * 5 >= frame_width // 2) and (x + dirx * 5 <= TUK_WIDTH - frame_width // 2):
        x += dirx * 5
    if (y + diry * 5 >= frame_height // 2) and (y + diry * 5 <= TUK_HEIGHT - frame_height // 2):
        y += diry * 5
    delay(0.05)

close_canvas()