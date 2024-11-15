from pico2d import *
import game_framework
import game_world
from Player import Player
from whip import Whip

def init():
    global player
    player = Player( 200, 200)
    game_world.add_object(player, 1)

def finish():
    game_world.clear()


def handle_events():
    events = pico2d.get_events()
    for event in events:
        if event.type == pico2d.SDL_QUIT:
            game_framework.quit()
        elif event.type == pico2d.SDL_KEYDOWN and event.key == pico2d.SDLK_ESCAPE:
            game_framework.quit()
        else:
            player.handle_event(event)

def update():
    game_world.update()
    game_world.handle_collisions()

def draw():
    pico2d.clear_canvas()
    game_world.render()
    pico2d.update_canvas()


def pause():
    pass

def resume():
    pass