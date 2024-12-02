import pico2d
from sdl2 import SDL_QUIT, SDL_KEYDOWN, SDLK_ESCAPE, SDLK_SPACE

import game_framework
from pico2d import load_image, get_time, clear_canvas, update_canvas, get_events

import play_mode


def init():
    global image, bgm
    bgm = pico2d.load_music('01. Dwelling.mp3')
    bgm.set_volume(64)
    bgm.play()
    image = load_image('logo.png')

def finish():
    global image, bgm
    del image, bgm

def update():
    handle_events()

def draw():
    clear_canvas()
    image.clip_draw_to_origin(0, 0, 2000, 1125, 0,0,1920,960 )
    update_canvas()

def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif (event.type, event.key) == (SDL_KEYDOWN, SDLK_SPACE):
            game_framework.change_mode(play_mode)