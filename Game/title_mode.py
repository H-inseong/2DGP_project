import pico2d
from sdl2 import SDL_QUIT, SDL_KEYDOWN, SDLK_ESCAPE, SDLK_SPACE, SDLK_a

import game_framework
from pico2d import load_image, get_time, clear_canvas, update_canvas, get_events

import play_mode


def init():
    global image, bgm
    bgm = pico2d.load_music('29. Spelunky 2.mp3')
    bgm.set_volume(48)
    bgm.play()
    image = load_image('title.png')

def finish():
    global image, bgm
    del image, bgm

def update():
    handle_events()

def draw():
    clear_canvas()
    image.clip_draw_to_origin(0, 0, 1920, 1080, 0,0,1920,960 )
    update_canvas()

def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif (event.type, event.key) == (SDL_KEYDOWN, SDLK_SPACE) or (event.type, event.key) == (SDL_KEYDOWN, SDLK_a):
            game_framework.change_mode(play_mode)