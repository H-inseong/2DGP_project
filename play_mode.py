from pico2d import *
import game_framework
import game_world
from Map import Map
from Player import Player
from enemies import Snake
from whip import Whip

def init():
    global player, map, camera_x, camera_y
    player = Player(240, 240)
    game_world.add_object(player, 1)

    map_obj = Map(46, 38)  # 맵 생성 (가로 46 타일, 세로 38 타일 예시)
    camera_x, camera_y = 0, 0

    s = Snake(0)
    game_world.add_object(s, 1)
    game_world.add_collision_pair('Player:Monster', player, s)
    game_world.add_collision_pair('Whip:Monster', None, s)

    game_world.add_collision_pair('Player:Map', player, None)  # 그룹 A에 플레이어 추가
    for tile in map_obj.tiles.values():  # Tile 객체를 순회
        game_world.add_collision_pair('Player:Map', None, tile)

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
    global camera_x, camera_y
    player.update()
    camera_x, camera_y = player.view_x, player.view_y
    game_world.update()
    game_world.handle_collisions()

def draw():
    pico2d.clear_canvas()
    if player.view_down == True:
        game_world.render(camera_x, camera_y - 240)
    if player.view_down == True:
        game_world.render(camera_x, camera_y + 240)
    game_world.render(camera_x, camera_y)
    pico2d.update_canvas()


def pause():
    pass

def resume():
    pass